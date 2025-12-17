import aio_pika
import asyncio
import json
import os
from sqlalchemy.orm import Session
from .database import SessionLocal
from .schemas import NotificationCreate
from .models import NotificationDB
from datetime import datetime

RABBIT_URL = os.getenv("RABBIT_URL")

def store_notification(db: Session, transaction_id: int, recipient: str, subject: str, message: str):
    record = NotificationDB(
        transaction_id=transaction_id,
        recipient=recipient,
        subject=subject,
        message=message,
        status="sent",
        timestamp=datetime.now()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def send_dummy_email(recipient: str, subject: str, message: str):
    print(f"[Email] To: {recipient}\nSubject: {subject}\nMessage: {message}\n")
    return True

async def callback(message):
    async with message.process():
        print("[x] Received event")
        
        data = json.loads(message.body)
        print("Parsed event:", data)
        
        transaction_id = data["transaction_id"]
        sender = data["sender_email"]
        receiver = data["receiver_email"]
        sender_name = data["sender_name"]
        receiver_name = data["receiver_name"]
        amount = data["amount"]
        
        db = SessionLocal()
        
        sender_msg = f"You sent €{amount} to {receiver_name}"
        receiver_msg = f"You received €{amount} from {sender_name}"
        
        send_dummy_email(sender, "Transaction Sent", sender_msg)
        send_dummy_email(receiver, "Transaction Received", receiver_msg)
        
        store_notification(db, transaction_id, sender, "Transaction Sent", sender_msg)
        store_notification(db, transaction_id, receiver, "Transaction Received", receiver_msg)
        
        db.close()
        print("[x] Done")

async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()
    
    queue = await channel.declare_queue("notifications", durable=True)
    await channel.set_qos(prefetch_count=1)
    
    print(" [*] Waiting for messages. To exit press CTRL+C")
    
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await callback(message)

if __name__ == "__main__":
    asyncio.run(main())
