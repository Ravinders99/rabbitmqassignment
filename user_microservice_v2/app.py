# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# import pika
# import json
# import logging

# app = Flask(__name__)

# # Set up logging
# logging.basicConfig(level=logging.INFO)

# # MongoDB connection
# client = MongoClient("mongodb+srv://assignment2:singh123@cluster0.lxswb.mongodb.net/poc_assignment2?retryWrites=true&w=majority")
# db = client['Poc_assignment2']
# user_collection = db['User']

# @app.route('/user', methods=['GET'])
# def get_user_v2():
#     user_id = request.args.get('user_id')
#     if not user_id:
#         return jsonify({"error": "user_id is required"}), 400

#     user = user_collection.find_one({"user_id": user_id}, {"_id": 0})
#     if user:
#         return jsonify(user), 200
#     else:
#         return jsonify({"error": "User not found"}), 404

# @app.route('/user', methods=['POST'])
# def create_user_v2():
#     data = request.json
#     if not data.get("user_id"):
#         return jsonify({"error": "user_id is required"}), 400

#     user_collection.insert_one(data)
#     return jsonify({"message": "User created successfully!"}), 201

# @app.route('/user', methods=['PUT'])
# def update_user_v2():
#     data = request.json
#     user_id = data.get('user_id')
#     new_email = data.get('new_email')
#     new_address = data.get('new_address')

#     if not user_id or not new_email or not new_address:
#         return jsonify({"error": "user_id, new_email, and new_address are required"}), 400

#     # Update user in MongoDB
#     result = user_collection.update_one(
#         {"user_id": user_id},
#         {"$set": {"email": new_email, "address": new_address}}
#     )

#     if result.matched_count == 0:
#         return jsonify({"error": "User not found"}), 404

#     # Publish event to RabbitMQ
#     connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
#     channel = connection.channel()
#     channel.queue_declare(queue='user_updates')
#     channel.basic_publish(
#         exchange='',
#         routing_key='user_updates',
#         body=json.dumps(data)
#     )
#     connection.close()

#     return jsonify({"message": "User updated and event published (v2)"}), 200


# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5002)


# UPdate code 
from flask import Flask, request, jsonify
from pymongo import MongoClient
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MongoDB connection
try:
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["poc_assignment2"]
    users_collection = db["users"]
    logging.info("Connected to MongoDB successfully!")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    exit(1)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "user_id" not in data:
        return jsonify({"error": "user_id is required"}), 400

    if users_collection.find_one({"user_id": data["user_id"]}):
        return jsonify({"error": "User already exists"}), 409

    users_collection.insert_one(data)
    return jsonify({"message": "User created successfully!"}), 201

@app.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    new_email = data.get("new_email")
    new_address = data.get("new_address")

    if not new_email or not new_address:
        return jsonify({"error": "new_email and new_address are required"}), 400

    result = users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"email": new_email, "address": new_address}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "No changes made or user not found"}), 404

    return jsonify({"message": "User updated successfully!"}), 200

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = users_collection.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)  # Ensure port matches for v2
