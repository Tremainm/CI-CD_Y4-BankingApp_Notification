import aio_pika
import asyncio
import json
import os

RABBIT_URL = os.getenv("RABBIT_URL")

async def publish_dummy_event():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()
    
    await channel.declare_queue("notifications", durable=True)
    
    event = {
        "transaction_id": 999,
        "sender_email": "alice@example.com",
        "receiver_email": "bob@example.com",
        "sender_name": "Alice",
        "receiver_name": "Bob",
        "amount": 100.5
    }
    
    message = aio_pika.Message(
        body=json.dumps(event).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )
    
    await channel.default_exchange.publish(message, routing_key="notifications")
    
    print("[x] Sent dummy transaction event")
    await connection.close()

if __name__ == "__main__":
    asyncio.run(publish_dummy_event())
