"""
tests/conftest.py
-----------------
Shared fixtures for the entire test suite.

What is a fixture?
  A fixture is a helper that pytest calls automatically before each test.
  Think of it like "setting up the stage" before a play.
  We use fixtures to:
    - Create a clean MySQL test database (separate from production)
    - Create a test HTTP client that talks to our FastAPI app directly
      (no real network call needed — it's all in-process)
    - Generate mock vital sign records so every test starts with the same data
"""

import sys
import os

# Add the project root to Python's module search path.
# Without this, Python wouldn't find our backend, ml, etc. packages.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load .env file so DB credentials are available as environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import urllib.parse
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------
# 1. Use a SEPARATE MySQL database for tests.
#    This ensures tests never corrupt the real production database.
#    Credentials are loaded from the project .env file.
# ---------------------------------------------------------------
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "3306")
# Dedicated test DB — never the production neonatal_watch_ai schema
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_neonatal_watch_ai")

# URL-encode the password so special characters (e.g. @) don't break the URL
_encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

TEST_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{_encoded_password}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"
)

from backend.app.db.database import Base, get_db
from backend.app.main import app

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Provides a test database session instead of the real one."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the real database dependency with the test database
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """
    Create all database tables before any tests run,
    and drop them all when the session is done.
    'scope=session' means this runs ONCE for the entire test run.
    Tables are created in the dedicated test MySQL database.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="module")
def client():
    """
    Returns a TestClient that lets us send HTTP requests to our app.
    'scope=module' means one client is shared by all tests in a file.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def vital_records():
    """
    Generates 60 minutes of fake (but realistic) vital sign records.
    This is the standard payload for the /predict endpoint.
    """
    base_time = datetime.now() - timedelta(minutes=60)
    return [
        {
            "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
            "patient_id": "TEST-PATIENT-001",
            "heart_rate": 140.0 + (i * 0.5),
            "spo2": 96.0 - (i * 0.15),
            "respiratory_rate": 45.0,
            "temperature": 37.0,
            "systolic_bp": 60.0,
            "diastolic_bp": 40.0,
        }
        for i in range(60)
    ]


@pytest.fixture
def normal_vital_records():
    """60 minutes of perfectly normal (non-deteriorating) vitals."""
    base_time = datetime.now() - timedelta(minutes=60)
    return [
        {
            "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
            "patient_id": "TEST-NORMAL-002",
            "heart_rate": 140.0,
            "spo2": 96.0,
            "respiratory_rate": 45.0,
            "temperature": 37.0,
            "systolic_bp": 65.0,
            "diastolic_bp": 42.0,
        }
        for i in range(60)
    ]

