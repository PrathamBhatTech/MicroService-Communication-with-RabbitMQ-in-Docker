import pymongo
import pika

# Connect to MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["students"]

# RabbitMQ setup
credentials = pika.PlainCredentials(username='guest', password='guest')
parameters = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()


# Declare the "insert_record" queue
channel.queue_declare(queue='insert_record')

# Define a callback function to handle incoming messages
def callback(ch, method, properties, body):
    # Parse incoming message
    message = body.decode()
    data = message.split(',')

    # Insert record into MongoDB
    record = {
        "name": data[0],
        "srn": data[1],
        "section": data[2]
    }
    collection.insert_one(record)

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Start consuming messages from the "insert_record" queue
channel.basic_consume(queue='insert_record', on_message_callback=callback)

print('Waiting for messages...')
channel.start_consuming()
