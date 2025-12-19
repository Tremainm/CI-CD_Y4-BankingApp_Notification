from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .database import engine, SessionLocal
from .models import Base, NotificationDB
from .schemas import NotificationCreate, NotificationRead

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

# CORS (add this block)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/notifications", response_model=list[NotificationRead])
def list_notifications(db: Session = Depends(get_db)):
    stmt = select(NotificationDB).order_by(NotificationDB.id)
    return list(db.execute(stmt).scalars())

@app.get("/api/notifications/by-account/{account_number}", response_model=list[NotificationRead])
def get_notifications_by_account(account_number: str, db: Session = Depends(get_db),):
    notifications = (db.query(NotificationDB).filter(NotificationDB.recipient == account_number)
    .order_by(NotificationDB.created_at.desc(), NotificationDB.id.desc()).all())

    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found for this account number")

    return notifications
