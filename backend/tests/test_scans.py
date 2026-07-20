import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.database import get_db
from app.database.models import Scan
from app.main import app

# Setup test in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_post_scan_missing_identifier():
    response = client.post("/scan", json={})
    assert response.status_code in (400, 422)


def test_post_scan_with_repository_name():
    payload = {"repository_name": "Cryptanium"}
    response = client.post("/scan", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["scan_id"] is not None
    assert data["repository_name"] == "Cryptanium"
    assert data["status"] == "completed"
    assert data["trust_score"] == 88
    assert data["summary"]["total_findings"] == 2
    assert len(data["findings"]) == 2

    # Verify DB persistence
    db = TestingSessionLocal()
    scan_in_db = db.query(Scan).filter(Scan.id == data["scan_id"]).first()
    assert scan_in_db is not None
    assert scan_in_db.repository_name == "Cryptanium"
    assert scan_in_db.findings_count == 2
    db.close()


def test_post_scan_with_repository_id():
    payload = {"repository_id": "98765"}
    response = client.post("/scan", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["scan_id"] is not None
    assert data["repository_id"] == "98765"
    assert data["repository_name"] == "repo-98765"
    assert data["status"] == "completed"
    assert data["trust_score"] == 88

    # Verify DB persistence
    db = TestingSessionLocal()
    scan_in_db = db.query(Scan).filter(Scan.id == data["scan_id"]).first()
    assert scan_in_db is not None
    assert scan_in_db.repository_id == "98765"
    db.close()
