from flask import Flask, request, jsonify
from pymongo import MongoClient
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MongoDB connection setup
try:
    mongo_client = MongoClient(
        "mongodb+srv://assignment2:singh123@cluster0.lxswb.mongodb.net/poc_assignment2?retryWrites=true&w=majority"
    )
    db = mongo_client["poc_assignment2"]  # Ensure the case matches your database name
    orders = db["orders"]
    logging.info("Connected to MongoDB successfully!")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    exit(1)

# Create an order
@app.route("/orders", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        order_id = data.get("order_id")
        email = data.get("email")
        delivery_address = data.get("delivery_address")

        if not order_id or not email or not delivery_address:
            return jsonify({"error": "Missing required fields: 'order_id', 'email', 'delivery_address'"}), 400

        # Check if order ID already exists
        if orders.find_one({"order_id": order_id}):
            return jsonify({"error": f"Order with ID {order_id} already exists"}), 409

        # Insert order into MongoDB
        order = {
            "order_id": order_id,
            "email": email,
            "delivery_address": delivery_address,
            "status": "under process",
        }
        orders.insert_one(order)
        logging.info(f"Order {order_id} created successfully!")
        return jsonify({"message": "Order created successfully!"}), 201
    except Exception as e:
        logging.error(f"Error creating order: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Get a specific order by ID
@app.route("/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    try:
        order = orders.find_one({"order_id": order_id}, {"_id": 0})
        if not order:
            return jsonify({"error": "Order not found"}), 404
        return jsonify(order), 200
    except Exception as e:
        logging.error(f"Error retrieving order {order_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Update an order
@app.route("/orders/<order_id>", methods=["PUT"])
def update_order(order_id):
    try:
        data = request.get_json()
        update_result = orders.update_one({"order_id": order_id}, {"$set": data})

        if update_result.matched_count == 0:
            return jsonify({"error": "Order not found"}), 404

        logging.info(f"Order {order_id} updated successfully!")
        return jsonify({"message": "Order updated successfully!"}), 200
    except Exception as e:
        logging.error(f"Error updating order {order_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
