import pika
import json
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = client["database"]
collection = db["ccdb"]

# RabbitMQ Connection
credentials = pika.PlainCredentials(username='guest', password='guest')
parameters = pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='delete_record', durable=True)

# Define callback function
def callback(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    srn = body.decode()
    collection.delete_one({'srn': srn})

# Start consuming from the queue
channel.basic_consume(queue='delete_record', on_message_callback=callback)

# Wait for messages
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
