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

@app.get("/api/notifications/{notification_id}", response_model=NotificationRead)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.get(NotificationDB, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@app.post("/api/notifications", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
def add_notification(payload: NotificationCreate, db: Session = Depends(get_db)):
    notification = NotificationDB(**payload.model_dump())
    db.add(notification)
    try:
        db.commit()
        db.refresh(notification)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Notification already exists")
    return notification