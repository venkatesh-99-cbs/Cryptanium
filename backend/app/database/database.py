from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.base import Base
import app.database.models  # noqa: F401

print("DATABASE_URL =", repr(settings.DATABASE_URL))

connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db(target_engine=None):
    """Initialize database tables and perform lightweight safe schema migrations if columns are missing."""
    eng = target_engine or engine

    # Step 1: Create any missing tables
    Base.metadata.create_all(bind=eng)

    # Step 2: Check for missing columns on pre-existing 'scans' table
    inspector = inspect(eng)
    if "scans" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("scans")}
        missing_columns = {
            "critical_severity_count": "INTEGER DEFAULT 0",
            "high_severity_count": "INTEGER DEFAULT 0",
            "medium_severity_count": "INTEGER DEFAULT 0",
            "low_severity_count": "INTEGER DEFAULT 0",
            "findings_json": "TEXT",
            "ai_summary": "TEXT",
            "ai_risk_level": "VARCHAR(50)",
            "ai_key_concerns": "TEXT",
            "ai_recommendations": "TEXT",
            "started_at": "DATETIME",
            "completed_at": "DATETIME",
            "updated_at": "DATETIME",
        }

        with eng.begin() as conn:
            for col_name, col_type in missing_columns.items():
                if col_name not in columns:
                    conn.execute(
                        text(f"ALTER TABLE scans ADD COLUMN {col_name} {col_type}")
                    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
