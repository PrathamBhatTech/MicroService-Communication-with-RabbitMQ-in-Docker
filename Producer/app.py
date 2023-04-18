import logging
import time
from flask import Flask, request, render_template
import pika
import json

app = Flask(
    __name__,
    template_folder='templates'
)

# RabbitMQ setup
credentials = pika.PlainCredentials(username='guest', password='guest')
parameters = pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare exchange
channel.exchange_declare(
    exchange='microservices', 
    exchange_type='direct',
    durable=True
)

# Declare queues
channel.queue_declare(queue='health_check', durable=True)
channel.queue_declare(queue='insert_record', durable=True)
channel.queue_declare(queue='delete_record', durable=True)
channel.queue_declare(queue='read_database', durable=True)

channel.queue_declare(queue='send_database', durable=True)

# Bind queues to exchange with routing keys
# TODO: make the queue name and the routing key name different
channel.queue_bind(exchange='microservices', queue='health_check', routing_key='health_check')
channel.queue_bind(exchange='microservices', queue='insert_record', routing_key='insert_record')
channel.queue_bind(exchange='microservices', queue='delete_record', routing_key='delete_record')
channel.queue_bind(exchange='microservices', queue='read_database', routing_key='read_database')


@app.route('/')
def index():
    return render_template('index.html')
    # return "<p>Hello, World!</p>"

# Health check endpoint
@app.route('/health_check', methods=['GET'])
def health_check():
    message = 'RabbitMQ connection established successfully'
    # Publish message to health_check queue
    channel.basic_publish(exchange='microservices', routing_key='health_check', body=message)
    return 'Health Check message sent!'


# Insert record endpoint
@app.route('/insert_record', methods=['GET'])
def insert_record():
    # name = request.form.get('Name')
    # srn = request.form.get('SRN')
    # section = request.form.get('Section')
    # message = json.dumps({'name': name, 'srn': srn, 'section': section})
    # # Publish message to insert_record queue
    # channel.basic_publish(exchange='microservices', routing_key='insert_record', body=message)
    return render_template('insert.html', message='Record Inserted Successfully!')

# Insert record endpoint
@app.route('/insert_record_actually', methods=['POST'])
def insert_record_actually():
    name = request.form['name']
    srn = request.form['srn']
    section = request.form['section']
    message = json.dumps({'name': name, 'srn': srn, 'section': section})
    logging.info(message)
    # Publish message to insert_record queue
    channel.basic_publish(exchange='microservices', routing_key='insert_record', body=message)

    return render_template('insert.html', message='Record Inserted Successfully!')

# Delete record endpoint
@app.route('/delete_record', methods=['GET'])
def delete_record():
    return render_template('delete.html', message='Record Deleted Successfully!')

@app.route('/delete_record_actually', methods=['POST'])
def delete_record_actually():
    srn = request.form['srn']
    message = srn
    logging.info(message)
    # Publish message to delete_record queue
    channel.basic_publish(exchange='microservices', routing_key='delete_record', body=message)
    return render_template('delete.html', message='Record Deleted Successfully!')

# Read database endpoint
@app.route('/read_database', methods=['GET'])
def read_database():
    # Publish message to read_database queue
    channel.basic_publish(exchange='microservices', routing_key='read_database', body='Read database request')

    return render_template('read.html', message='Read Database message sent!')

@app.route('/read_database_actually', methods=['GET'])
def read_database_actually():

    method_frame, header_frame, body  = channel.basic_get(queue='send_database')
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    if method_frame:
        records = body.decode()
    else:
        records = {}

    return records

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
