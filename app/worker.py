import aio_pika
import asyncio
import json
import os
from decimal import Decimal

from .database import SessionLocal
from .models import NotificationDB

RABBIT_URL = os.getenv("RABBIT_URL")


def create_notification(db, tx_id, recipient, subject, message):
    n = NotificationDB(
        transaction_id=tx_id,
        recipient=recipient,
        subject=subject,
        message=message,
        status="sent",
    )
    db.add(n)
    db.commit()


async def handle_transaction(event: dict):
    db = SessionLocal()

    tx_type = event["tx_type"]
    amount = Decimal(event["amount"])

    sender_name = event.get("sender_name")
    sender_acc = event.get("sender_account_number")

    receiver_name = event.get("receiver_name")
    receiver_acc = event.get("receiver_account_number")

    tx_id = event["id"]

    # ---------- Deposit ----------
    if tx_type == "deposit":
        create_notification(
            db,
            tx_id,
            receiver_acc,
            "Deposit Successful",
            f"You received €{amount}."
        )

    # ---------- Withdrawal ----------
    elif tx_type == "withdrawal":
        create_notification(
            db,
            tx_id,
            sender_acc,
            "Withdrawal Successful",
            f"You withdrew €{amount}."
        )

    # ---------- Transfer ----------
    elif tx_type == "transfer_out":
        create_notification(
            db,
            tx_id,
            sender_acc,
            "Transfer Sent",
            f"You sent €{amount} to {receiver_name} ({receiver_acc})."
        )

    elif tx_type == "transfer_in":
        create_notification(
            db,
            tx_id,
            receiver_acc,
            "Transfer Received",
            f"You received €{amount} from {sender_name} ({sender_acc})."
        )

    db.close()


async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()

    queue = await channel.declare_queue("transactions", durable=True)
    await channel.set_qos(prefetch_count=1)

    print(" [*] Notification worker listening for transactions")

    async with queue.iterator() as q:
        async for message in q:
            async with message.process():
                event = json.loads(message.body)
                await handle_transaction(event)


if __name__ == "__main__":
    asyncio.run(main())
