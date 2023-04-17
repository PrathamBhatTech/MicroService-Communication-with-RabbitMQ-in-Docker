import pika
import pymongo

# RabbitMQ setup
credentials = pika.PlainCredentials(username='guest', password='guest')
parameters = pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()


# Connect to MongoDB
client = pymongo.MongoClient("mongodb://mongodb:27017")
db = client["database"]
collection = db["ccdb"]

# Declare the "read_database" queue
channel.queue_declare(
    queue='read_database',
    durable=True
)

# Define the callback function to process incoming messages
def callback(ch, method, properties, body):
    print("Received %r" % body)

    # Retrieve all records from the database
    records = collection.find()

    print(records)
    
    # Send each record to the producer through RabbitMQ
    channel.basic_publish(exchange='', routing_key='send_database', body=str(records))

    # Acknowledge that the message has been processed
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Consume messages from the "read_database" queue
channel.basic_consume(queue='read_database', on_message_callback=callback)

# Start consuming messages
print('Waiting for messages...')
channel.start_consuming()
