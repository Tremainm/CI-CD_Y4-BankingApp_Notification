import pika, sys, os, time

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # channel.queue_declare(queue='hello')

    # Message durability: ensure messages are not lost is rabbitMQ is terminated/restarted
    channel.queue_declare(queue='task_queue', durable=True)

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        time.sleep(body.count(b'.'))
        print(" [x] Done")

        # Send aknowledgement from worker once we're done with a task. Ensures message is never lost if worker is terminated
        ch.basic_ack(delivery_tag = method.delivery_tag)

    # Tell rabbitMQ not to give more than one message to a worker at a time 
    # i.e; don't dispatch a new message to a worker until it has processed and acknowledged the previous one
    # It will dispatch it to the next worker that is not still busy.
    channel.basic_qos(prefetch_count=1)
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