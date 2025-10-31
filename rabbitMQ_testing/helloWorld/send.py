# RabbitMQ tutorial from here:https://www.rabbitmq.com/tutorials/tutorial-one-python
# Downloading rabbitMQ in codespace:
# 1. docker run -d --hostname rabbit --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
# 2. If restarting codespace, run 'docker start rabbitmq' to restart rabbitmq

import pika

# Establish connection with rabbitMQ, localhost is local machine
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Creating recipient queue. Message will be dropped if we send it to non-existing location
channel.queue_declare(queue='hello')

#**** READY TO SEND FIRST MESSAGE ****

# Message goes through an exchange first (default exchange is identified by an empty string)
# The exchange allows us to specify which queue the message goes to (routing_key = queue name)
channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
print(" [x] Sent 'Hello World!'")

connection.close()