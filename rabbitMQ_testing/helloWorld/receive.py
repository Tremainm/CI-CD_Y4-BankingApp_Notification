import pika, sys, os

def main():
    #  Setup connection same as in send.py
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Make sure queue exists
    channel.queue_declare(queue='hello')

    # Receiving messages from a queue: 
    # 1. subscribing callback func to a queue
    # 2. When we receive a message, callback func is called by pika
    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    # Receive messages from 'hello' queue
    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)