import pika, sys, os, time

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    # Message durability: ensure messages are not lost is rabbitMQ is terminated/restarted
    channel.queue_declare(queue='task_queue', durable=True)

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        time.sleep(body.count(b'.'))
        print(" [x] Done")

        # Send aknowledgement from worker once we're done with a task. Ensures message is never lost if worker is terminated
        ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_consume(queue='task_queue', on_message_callback=callback)

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