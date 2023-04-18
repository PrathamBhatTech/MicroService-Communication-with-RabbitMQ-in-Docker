import json
import logging
import pymongo
import pika

# Connect to MongoDB database
client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = client["database"]
collection = db["ccdb"]

# RabbitMQ setup
credentials = pika.PlainCredentials(username='guest', password='guest')
parameters = pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()


# Declare the "insert_record" queue
channel.queue_declare(queue='insert_record', durable=True)

# Define a callback function to handle incoming messages
def callback(ch, method, properties, body):
    # Parse incoming message
    body = body.decode()
    body = json.loads(body)
    # message = json.loads(body)

    record = {
        "name": body['name'],
        "srn": body['srn'],
        "section": body['section'],
    }
    collection.insert_one(record)

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Start consuming messages from the "insert_record" queue
channel.basic_consume(queue='insert_record', on_message_callback=callback)

print('Waiting for messages...')
channel.start_consuming()
