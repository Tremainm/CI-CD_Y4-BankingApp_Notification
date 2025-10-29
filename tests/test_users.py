import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # allows only one session with StaticPool to avoid 'no such table' error

from app.main import app, get_db
from app.models import Base

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
    with TestClient(app) as c:
        # hand the client to the test
        yield c
        # --- teardown happens when the 'with' block exits ---

def test_create_notification(client):
    r = client.post("/api/notifications", json={
                                            "transaction_id": 42,
                                            "recipient": "jane@example.com",
                                            "subject": "Payment received",
                                            "message": "You received €100 from John",
                                            "status": "sent",
                                            "timestamp": "2025-10-29T11:10:18.088000"})
    assert r.status_code == 201