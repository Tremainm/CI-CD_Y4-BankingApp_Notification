# publisher.py
# Dummy Accounts Microservice that sends dummy transaction information
import json
import pika

def publish_dummy_event():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    # durable queue
    channel.queue_declare(queue="notifications", durable=True)

    event = {
        "transaction_id": 999,
        "sender_email":    "alice@example.com",
        "receiver_email":  "bob@example.com",
        "sender_name":     "Alice",
        "receiver_name":   "Bob",
        "amount":          100.5
    }

    message = json.dumps(event)

    channel.basic_publish(
        exchange="",
        routing_key="notifications",
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent   # message durability
        )
    )

    print("[x] Sent dummy transaction event")
    connection.close()


if __name__ == "__main__":
    publish_dummy_event()
