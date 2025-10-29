from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class NotificationDB(Base):
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(Integer, nullable=False)
    recipient: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="sent")
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # ^ Map timestamps of transaction notifications