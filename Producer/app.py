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

# Bind queues to exchange with routing keys
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
@app.route('/insert_record', methods=['POST'])
def insert_record():
    name = request.form.get('Name')
    srn = request.form.get('SRN')
    section = request.form.get('Section')
    message = json.dumps({'name': name, 'srn': srn, 'section': section})
    # Publish message to insert_record queue
    channel.basic_publish(exchange='microservices', routing_key='insert_record', body=message)
    return render_template('insert.html', message='Record Inserted Successfully!')


# Delete record endpoint
@app.route('/delete_record', methods=['GET'])
def delete_record():
    srn = request.args.get('SRN')
    message = srn
    # Publish message to delete_record queue
    channel.basic_publish(exchange='microservices', routing_key='delete_record', body=message)
    return 'Record Delete message sent!'


# Read database endpoint
@app.route('/read_database', methods=['GET'])
def read_database():
    # Publish message to read_database queue
    channel.basic_publish(exchange='microservices', routing_key='read_database', body='Read database request')
    return render_template('read.html', message='Read Database message sent!')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
