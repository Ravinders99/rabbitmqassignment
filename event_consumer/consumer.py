# import pika
# import json
# import logging
# from pymongo import MongoClient

# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# # MongoDB connection setup
# try:
#     mongo_client = MongoClient(
#         "mongodb+srv://assignment2:singh123@cluster0.lxswb.mongodb.net/poc_assignment2?retryWrites=true&w=majority"
#     )
#     db = mongo_client["poc_assignment2"]
#     order_collection = db["orders"]
#     logging.info("Connected to MongoDB successfully!")
# except Exception as e:
#     logging.error(f"Error connecting to MongoDB: {e}")
#     exit(1)


# # Function to process events
# def process_event(body):
#     try:
#         event = json.loads(body)
#         logging.info(f"Processing event: {event}")

#         # Validate event payload
#         if "old_email" in event and "new_email" in event and "new_address" in event:
#             result = order_collection.update_many(
#                 {"email": event["old_email"]},  # Match old email
#                 {"$set": {"email": event["new_email"], "delivery_address": event["new_address"]}}
#             )
#             logging.info(
#                 f"Order database synchronized! Matched: {result.matched_count}, Updated: {result.modified_count}"
#             )
#         else:
#             logging.warning("Invalid event payload: Missing required fields.")
#     except json.JSONDecodeError as e:
#         logging.error(f"Error decoding JSON message: {e}")
#     except Exception as e:
#         logging.error(f"Error processing event: {e}")


# # RabbitMQ connection setup
# def consume_events():
#     try:
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host="rabbitmq",  # Hostname must match the RabbitMQ service name in docker-compose.yml
#                 heartbeat=600,
#                 blocked_connection_timeout=300,
#             )
#         )
#         channel = connection.channel()

#         # Declare the queue with consistent properties
#         channel.queue_declare(queue="user_updates", durable=True)

#         logging.info("Connected to RabbitMQ successfully!")
#         logging.info("Waiting for messages. To exit, press CTRL+C")

#         # Callback for processing messages
#         def callback(ch, method, properties, body):
#             logging.info(f"Received message: {body}")
#             process_event(body)

#         # Start consuming messages
#         channel.basic_consume(queue="user_updates", on_message_callback=callback, auto_ack=True)
#         channel.start_consuming()

#     except pika.exceptions.AMQPConnectionError as e:
#         logging.error(f"Error connecting to RabbitMQ: {e}")
#     except KeyboardInterrupt:
#         logging.info("Exiting...")
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#     finally:
#         try:
#             connection.close()
#             logging.info("RabbitMQ connection closed.")
#         except Exception as e:
#             logging.error(f"Error closing RabbitMQ connection: {e}")


# if __name__ == "__main__":
#     consume_events()

import pika
import json
import logging
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MongoDB connection setup
try:
    mongo_client = MongoClient(
        "mongodb+srv://assignment2:singh123@cluster0.lxswb.mongodb.net/poc_assignment2?retryWrites=true&w=majority"
    )
    db = mongo_client["poc_assignment2"]
    users_collection = db["users"]
    logging.info("Connected to MongoDB successfully!")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    exit(1)

# Function to process events received from RabbitMQ
def process_event(body):
    try:
        # Decode the JSON message
        event = json.loads(body)
        logging.info(f"Processing event: {event}")

        # Validate event payload
        if "old_email" in event and "new_email" in event and "new_address" in event:
            # Update MongoDB
            result = users_collection.update_many(
                {"email": event["old_email"]},
                {"$set": {"email": event["new_email"], "address": event["new_address"]}},
            )
            logging.info(
                f"Database update: Matched {result.matched_count}, Updated {result.modified_count}"
            )
        else:
            logging.warning("Invalid event payload: Missing required fields.")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON message: {e}")
    except Exception as e:
        logging.error(f"Error processing event: {e}")

# RabbitMQ connection and consumer setup
def consume_events():
    try:
        connection = pika.BlockingConnection(
                 pika.ConnectionParameters(
                    host="rabbitmq",
                    heartbeat=30,  # Send heartbeat every 30 seconds
                    blocked_connection_timeout=300,  # Allow 5 minutes to recover
             )
        )

        # # Connect to RabbitMQ
        # connection = pika.BlockingConnection(
        #     pika.ConnectionParameters(
        #         host="rabbitmq",  # RabbitMQ service name in Docker
        #         heartbeat=600,
        #         blocked_connection_timeout=300,
        #     )
        # )
        channel = connection.channel()

        # Declare the queue with consistent properties
        channel.queue_declare(queue="user_updates", durable=True)

        logging.info("Connected to RabbitMQ successfully!")
        logging.info("Waiting for messages. To exit, press CTRL+C")

        # Define callback for message consumption
        def callback(ch, method, properties, body):
            logging.info(f"Received message: {body}")
            process_event(body)

        # Start consuming messages
        channel.basic_consume(queue="user_updates", on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Error connecting to RabbitMQ: {e}")
    except KeyboardInterrupt:
        logging.info("Exiting...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        try:
            connection.close()
            logging.info("RabbitMQ connection closed.")
        except Exception as e:
            logging.error(f"Error closing RabbitMQ connection: {e}")

if __name__ == "__main__":
    consume_events()
