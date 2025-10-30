# Work queues example: avoids doing resource-intesive task immediately and having to wait for it to complete.
# We schedule tasks to be done later, we encapsulate a task as a message and send it to the queue.
# A worker process will pop the tasks and eventually execute the job.
# When you run many workers the tasks will be shared between them.

import pika, sys

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

# Allows messages from command line
message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange='', routing_key='hello', body=message)
print(f" [x] Sent {message}")

connection.close()