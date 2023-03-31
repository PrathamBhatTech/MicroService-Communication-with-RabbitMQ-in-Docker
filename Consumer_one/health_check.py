import pika

# Connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare health_check queue
channel.queue_declare(queue='health_check')

# Define callback function to handle incoming messages
def callback(ch, method, properties, body):
    # Process incoming message here
    print("Received health check message: %r" % body)

    # Acknowledge message using simple acknowledgement (ack)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Consume messages from health_check queue
channel.basic_consume(queue='health_check', on_message_callback=callback)

# Start consuming messages
print('Waiting for health check messages...')
channel.start_consuming()
