'''
For the consumer_one (health_check):

RabbitMQ Client to listen for incoming requests on the “health_check” queue and process it.

This consumer must acknowledge that the health-check message has been listened to through the “health_check” queue. (Simple Ack)
'''

import pika
import time

# RabbitMQ setup
credentials = pika.PlainCredentials(username='guest', password='guest')
parameters = pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

# Declare the queue
channel.queue_declare(
    queue='health_check',
    durable=True
)

# Callback function
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

# Consume the queue
channel.basic_consume(queue='health_check', on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()