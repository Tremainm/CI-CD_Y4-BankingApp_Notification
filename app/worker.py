# worker.py  (runs independently of FastAPI)
import pika, json, time
from sqlalchemy.orm import Session
from .database import SessionLocal
from .schemas import NotificationCreate
from .models import NotificationDB
from datetime import datetime


def store_notification(
    db: Session,
    transaction_id: int,
    recipient: str,
    subject: str,
    message: str,
):
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


def callback(ch, method, properties, body):
    print("[x] Received event")

    data = json.loads(body)
    print("Parsed event:", data)

    transaction_id = data["transaction_id"]
    sender = data["sender_email"]
    receiver = data["receiver_email"]
    sender_name = data["sender_name"]
    receiver_name = data["receiver_name"]
    amount = data["amount"]

    db = SessionLocal()

    # Construct email text
    sender_msg = f"You sent €{amount} to {receiver_name}"
    receiver_msg = f"You received €{amount} from {sender_name}"

    # Send “email”
    send_dummy_email(sender, "Transaction Sent", sender_msg)
    send_dummy_email(receiver, "Transaction Received", receiver_msg)

    # Store in DB
    store_notification(
        db,
        transaction_id=transaction_id,
        recipient=sender,
        subject="Transaction Sent",
        message=sender_msg,
    )

    store_notification(
        db,
        transaction_id=transaction_id,
        recipient=receiver,
        subject="Transaction Received",
        message=receiver_msg,
    )

    db.close()

    print("[x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.queue_declare(queue="notifications", durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue="notifications",
        on_message_callback=callback
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()
