from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict
from datetime import datetime

SubjectStr = Annotated[str, StringConstraints(min_length=2, max_length=20)]
MsgStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]

class NotificationCreate(BaseModel):
    transaction_id: int
    recipient: EmailStr
    subject: SubjectStr
    message: MsgStr
    status: str = "sent"
    timestamp: Optional[datetime] = None

class NotificationRead(BaseModel):
    id: int
    transaction_id: int
    recipient: EmailStr
    subject: str
    message: str
    status: str
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)
