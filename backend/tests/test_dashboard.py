import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.database import get_db, init_db
from app.database.models import Scan
from app.main import app

# Setup test in-memory SQLite database
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


def test_get_dashboard_empty_db():
    response = client.get("/dashboard")

    assert response.status_code == 200
    data = response.json()

    assert data["total_repositories"] == 0
    assert data["total_scans"] == 0
    assert data["average_trust_score"] == 0.0
    assert data["total_vulnerabilities"] == 0
    assert data["high_severity_count"] == 0
    assert data["medium_severity_count"] == 0
    assert data["low_severity_count"] == 0
    assert data["recent_scans"] == []


def test_get_dashboard_with_scan_history():
    db = TestingSessionLocal()

    scans = [
        Scan(
            repository_id="repo-1",
            repository_name="Cryptanium-Core",
            status="completed",
            trust_score=90,
            findings_count=3,
            high_severity_count=1,
            medium_severity_count=2,
            low_severity_count=0,
        ),
        Scan(
            repository_id="repo-1",
            repository_name="Cryptanium-Core",
            status="completed",
            trust_score=80,
            findings_count=5,
            high_severity_count=2,
            medium_severity_count=2,
            low_severity_count=1,
        ),
        Scan(
            repository_id="repo-2",
            repository_name="Cryptanium-Web",
            status="completed",
            trust_score=70,
            findings_count=4,
            high_severity_count=1,
            medium_severity_count=1,
            low_severity_count=2,
        ),
    ]
    for s in scans:
        db.add(s)
    db.commit()
    db.close()

    response = client.get("/dashboard")

    assert response.status_code == 200
    data = response.json()

    assert data["total_repositories"] == 2
    assert data["total_scans"] == 3
    # Average trust score: (90 + 80 + 70) / 3 = 80.0
    assert data["average_trust_score"] == 80.0
    # Total vulnerabilities: 3 + 5 + 4 = 12
    assert data["total_vulnerabilities"] == 12
    # High: 1 + 2 + 1 = 4
    assert data["high_severity_count"] == 4
    # Medium: 2 + 2 + 1 = 5
    assert data["medium_severity_count"] == 5
    # Low: 0 + 1 + 2 = 3
    assert data["low_severity_count"] == 3
    # Recent scans count should be 3
    assert len(data["recent_scans"]) == 3


def test_dashboard_migration_pre_existing_db():
    # 1. Manually drop scans table and recreate with OLD schema (missing severity columns)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS scans"))
        conn.execute(
            text(
                """
                CREATE TABLE scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repository_id VARCHAR(100),
                    repository_name VARCHAR(255) NOT NULL,
                    status VARCHAR(50) DEFAULT 'completed',
                    trust_score INTEGER DEFAULT 85,
                    findings_count INTEGER DEFAULT 0,
                    created_at DATETIME
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO scans (repository_name, status, trust_score, findings_count)
                VALUES ('Old-Repo', 'completed', 85, 2)
                """
            )
        )

    # 2. Run init_db to perform safe schema migration
    init_db(engine)

    # 3. GET /dashboard must succeed without OperationalError
    response = client.get("/dashboard")
    assert response.status_code == 200, response.json()
    data = response.json()

    assert data["total_scans"] == 1
    assert data["total_repositories"] == 1
    assert data["recent_scans"][0]["repository_name"] == "Old-Repo"
    assert data["high_severity_count"] == 0

