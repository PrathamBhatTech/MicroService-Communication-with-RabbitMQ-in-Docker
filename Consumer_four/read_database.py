import pika
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["database"]
collection = db["ccdb"]

# RabbitMQ setup
credentials = pika.PlainCredentials(username='guest', password='guest')
parameters = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()


# Declare the "read_database" queue
channel.queue_declare(queue='read_database', durable=True)

# Define the callback function to process incoming messages
def callback(ch, method, properties, body):
    print("Received %r" % body)

    # Retrieve all records from the database
    records = collection.find()

    # Send each record to the producer through RabbitMQ
    for record in records:
        channel.basic_publish(exchange='', routing_key='send_database', body=str(record))

    # Acknowledge that the message has been processed
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Consume messages from the "read_database" queue
channel.basic_consume(queue='read_database', on_message_callback=callback)

# Start consuming messages
print('Waiting for messages...')
channel.start_consuming()
