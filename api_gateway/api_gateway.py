from flask import Flask, request, jsonify
import random
import yaml
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load routing configuration
try:
    with open("routing_config.yaml", "r") as file:
        config = yaml.safe_load(file)
        v1_percentage = config["routing"]["v1_percentage"]
    if not (0 <= v1_percentage <= 100):
        raise ValueError("Invalid v1_percentage value in config")
except Exception as e:
    logging.error(f"Failed to load routing configuration: {str(e)}")
    v1_percentage = 50  # Default to 50%
    logging.info("Defaulting v1_percentage to 50%")

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Users Routing


@app.route("/users/<user_id>", methods=["POST", "PUT", "GET"])
@app.route("/users", methods=["POST", "GET"])
def route_users(user_id=None):
    try:
        # Decide routing based on random percentage
        if random.randint(1, 100) <= v1_percentage:
            target = "http://user_service_v1:5001"
        else:
            target = "http://user_service_v2:5002"

        # Construct the target URL
        if user_id:
            target = f"{target}/users/{user_id}"
        else:
            target = f"{target}/users"

        logging.info(f"Routing to: {target} | Method: {request.method}")

        # Forward request to the appropriate user service
        if request.method == "POST":
            response = requests.post(
                url=target,
                headers=request.headers,
                json=request.get_json(),
            )
        elif request.method == "PUT":
            response = requests.put(
                url=target,
                headers=request.headers,
                json=request.get_json(),
            )
        elif request.method == "GET":
            response = requests.get(
                url=target,
                headers=request.headers,
                params=request.args,
            )
        else:
            return jsonify({"error": "Method not allowed"}), 405

        return response.text, response.status_code, response.headers.items()
    except Exception as e:
        logging.error(f"Error during routing: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Orders Routing
@app.route("/orders", methods=["POST"])
@app.route("/orders/<order_id>", methods=["GET", "PUT"])
def route_orders(order_id=None):
    try:
        # Fixed target for orders service
        target = "http://order_service:5003"
        target = f"{target}/orders/{order_id}" if order_id else f"{target}/orders"

        logging.info(f"Routing to: {target} | Method: {request.method}")

        # Forward requests to the Orders Microservice
        if request.method == "POST":
            payload = request.get_json() or {}
            response = requests.post(url=target, headers=request.headers, json=payload)
        elif request.method == "PUT":
            payload = request.get_json() or {}
            response = requests.put(url=target, headers=request.headers, json=payload)
        elif request.method == "GET":
            response = requests.get(url=target, headers=request.headers, params=request.args)
        else:
            return jsonify({"error": "Method not allowed"}), 405

        logging.info(f"Response from {target} - Status: {response.status_code}")
        return response.text, response.status_code, response.headers.items()

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while routing to {target}: {str(e)}")
        return jsonify({"error": "Network error"}), 502
    except Exception as e:
        logging.error(f"Unexpected error during routing: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
