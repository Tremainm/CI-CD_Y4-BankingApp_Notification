import pytest, json, asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # allows only one session with StaticPool to avoid 'no such table' error

from decimal import Decimal

from app.main import app, get_db
from app.models import Base, NotificationDB

TEST_DB_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db

    # Clear all data before each test
    db = TestingSessionLocal()
    db.query(NotificationDB).delete()
    db.commit()
    db.close()

    with TestClient(app) as c:
        # hand the client to the test
        yield c
        # --- teardown happens when the 'with' block exits ---

def test_list_notifications_empty(client):
    r = client.get("/api/notifications")
    assert r.status_code == 200
    assert r.json() == []

def test_list_notifications_with_data(client):
    # Add notification to database
    db = TestingSessionLocal()
    notification = NotificationDB(
        transaction_id=1,
        recipient="AC1234",
        subject="Test",
        message="Test message",
        status="sent"
    )
    db.add(notification)
    db.commit()
    db.close()
    
    r = client.get("/api/notifications")
    assert r.status_code == 200
    assert len(r.json()) == 1

def test_get_notifications_by_account_success(client):
    # Add notification to database
    db = TestingSessionLocal()
    notification = NotificationDB(
        transaction_id=1,
        recipient="AC1234",
        subject="Test",
        message="Test message",
        status="sent"
    )
    db.add(notification)
    db.commit()
    db.close()
    
    r = client.get("/api/notifications/by-account/AC1234")
    assert r.status_code == 200
    assert len(r.json()) == 1

def test_get_notifications_by_account_not_found(client):
    r = client.get("/api/notifications/by-account/AC9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "No notifications found for this account number"

def test_get_db_function():
    """Test the get_db dependency function"""
    from app.main import get_db
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    # Test cleanup
    try:
        next(db_gen)
    except StopIteration:
        pass

def test_database_connection():
    """Test database connection and retry logic"""
    from app.database import SessionLocal, get_db
    
    # Test SessionLocal works
    db = SessionLocal()
    assert db is not None
    db.close()
    
    # Test get_db function
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    try:
        next(db_gen)
    except StopIteration:
        pass

# Worker tests
def test_create_notification():
    """Test create_notification function"""

    from app.worker import create_notification
    
    db = TestingSessionLocal()
    create_notification(db, 123, "AC1234", "Test Subject", "Test Message")
    
    # Verify notification was created
    notification = db.query(NotificationDB).first()
    assert notification.transaction_id == 123
    assert notification.recipient == "AC1234"
    assert notification.subject == "Test Subject"
    assert notification.message == "Test Message"
    db.close()

def test_handle_transaction_withdrawal():
    """Test handle_transaction for withdrawal"""
    from app.worker import handle_transaction
    from unittest.mock import patch
    
    # Clear database first
    db = TestingSessionLocal()
    db.query(NotificationDB).delete()
    db.commit()
    db.close()
    
    # Mock SessionLocal to use test database
    with patch('app.worker.SessionLocal', TestingSessionLocal):
        event = {
            "event_type": "withdrawal",
            "transaction_id": 200,
            "amount": "50.00",
            "account_number": "AC5678",
            "account_name": "Jane Doe"
        }
        
        asyncio.run(handle_transaction(event))
    
    # Verify notification was created
    db = TestingSessionLocal()
    notification = db.query(NotificationDB).filter_by(transaction_id=200).first()
    assert notification is not None
    assert notification.subject == "Withdrawal Successful"
    assert "€50.00" in notification.message
    db.close()


