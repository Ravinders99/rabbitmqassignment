from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb+srv://assignment2:singh123@cluster0.lxswb.mongodb.net/poc_assignment2?retryWrites=true&w=majority")
db = client['Poc_assignment2']  # Ensure this matches the database name in Compass

# Insert data into the User collection
user_collection = db['User']  # Ensure this matches the collection name in Compass
user_data = {
    "user_id": "u123",
    "email": "user123@example.com",
    "delivery_address": "123 Main St, City, Country"
}
user_collection.insert_one(user_data)

# Insert data into the Orders collection
order_collection = db['orders']  # Ensure this matches the collection name in Compass
order_data = {
    "order_id": "o456",
    "items": ["item1", "item2"],
    "email": "user123@example.com",
    "delivery_address": "123 Main St, City, Country",
    "status": "under process"
}
order_collection.insert_one(order_data)

print("Data inserted successfully!")
