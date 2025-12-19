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

    try:
        tx_type = event["event_type"]
        tx_id = event["transaction_id"]
        amount = Decimal(event["amount"])

        account_number = event["account_number"]
        account_name = event["account_name"]

        counterparty_acc = event.get("counterparty_account_number")
        counterparty_name = event.get("counterparty_name")

        if tx_type == "deposit":
            create_notification(
                db,
                tx_id,
                account_number,
                "Deposit Successful",
                f"{account_name} received €{amount}."
            )

        elif tx_type == "withdrawal":
            create_notification(
                db,
                tx_id,
                account_number,
                "Withdrawal Successful",
                f"{account_name} withdrew €{amount}."
            )

        elif tx_type == "transfer_out":
            create_notification(
                db,
                tx_id,
                account_number,
                "Transfer Sent",
                f"{account_name} sent €{amount} to {counterparty_name} ({counterparty_acc})."
            )

        elif tx_type == "transfer_in":
            create_notification(
                db,
                tx_id,
                account_number,
                "Transfer Received",
                f"{account_name} received €{amount} from {counterparty_name} ({counterparty_acc})."
            )

    finally:
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
