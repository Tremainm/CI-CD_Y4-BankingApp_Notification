from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal


# Incoming transaction event (from Account service)
class TransactionEvent(BaseModel):
    id: int
    tx_type: str
    amount: Decimal

    sender_account_number: Optional[str] = None
    sender_name: Optional[str] = None

    receiver_account_number: Optional[str] = None
    receiver_name: Optional[str] = None

    created_at: datetime

# Notification API schemas
class NotificationCreate(BaseModel):
    transaction_id: int
    recipient: str
    subject: str
    message: str
    status: str = "sent"


class NotificationRead(NotificationCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
