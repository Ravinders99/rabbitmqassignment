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

# @app.route("/users/<user_id>", methods=["GET"])
# def get_user(user_id):
#     user = users_collection.find_one({"user_id": user_id}, {"_id": 0})
#     if not user:
#         return jsonify({"error": "User not found"}), 404
#     return jsonify(user), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # Ensure port matches for v1
