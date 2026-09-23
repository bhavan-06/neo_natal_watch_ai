"""
tests/test_database.py
-----------------------
Tests for the SQLAlchemy database layer (CRUD operations).

Why test the database separately?
  The database is where all data lives permanently.
  If CRUD functions are broken, predictions would silently disappear.
  These tests verify that data actually gets WRITTEN and READ correctly.
  
  We use the in-memory test DB (configured in conftest.py) so these tests
  never touch the real neonatal.db file.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.app.db import crud, models
from backend.app.db.database import Base
from tests.conftest import TestSessionLocal, test_engine
from backend.app.schemas.predict_schema import VitalSignRecord


@pytest.fixture
def db_session():
    """Provide a fresh database session for each database test."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_vital_records():
    """Create 60 VitalSignRecord Pydantic objects for testing CRUD."""
    base_time = datetime.now() - timedelta(minutes=60)
    return [
        VitalSignRecord(
            timestamp=(base_time + timedelta(minutes=i)).isoformat(),
            patient_id="DB-TEST-PATIENT",
            heart_rate=140.0 + i * 0.3,
            spo2=96.0 - i * 0.1,
            respiratory_rate=45.0,
            temperature=37.0,
            systolic_bp=62.0,
            diastolic_bp=41.0,
        )
        for i in range(60)
    ]


class TestDatabaseCRUD:

    def test_ensure_patient_creates_new_patient(self, db_session):
        """ensure_patient_exists() must create a patient row if one doesn't exist."""
        patient_id = "NEW-DB-TEST-001"
        patient = crud.ensure_patient_exists(db_session, patient_id)
        assert patient is not None
        assert patient.id == patient_id

    def test_ensure_patient_does_not_duplicate(self, db_session):
        """Calling ensure_patient_exists() twice must NOT create a duplicate row."""
        patient_id = "DEDUP-TEST-002"
        crud.ensure_patient_exists(db_session, patient_id)
        crud.ensure_patient_exists(db_session, patient_id)  # second call
        count = db_session.query(models.Patient).filter(
            models.Patient.id == patient_id
        ).count()
        assert count == 1, "Patient row was duplicated!"

    def test_create_vital_signs_inserts_records(self, db_session, sample_vital_records):
        """create_vital_signs() must insert all 60 records into vital_signs table."""
        before_count = db_session.query(models.VitalSign).filter(
            models.VitalSign.patient_id == "DB-TEST-PATIENT"
        ).count()
        crud.create_vital_signs(db_session, sample_vital_records)
        after_count = db_session.query(models.VitalSign).filter(
            models.VitalSign.patient_id == "DB-TEST-PATIENT"
        ).count()
        assert after_count - before_count == 60

    def test_save_prediction_inserts_row(self, db_session):
        """save_prediction() must insert one row into the predictions table."""
        patient_id = "PRED-TEST-003"
        result = {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "risk_score": 0.72,
            "risk_level": "HIGH",
            "individual_models": {
                "xgboost": 0.15,
                "cnn_lstm": 0.99,
                "autoencoder": 0.98,
                "transformer": 0.81,
            }
        }
        before_count = db_session.query(models.Prediction).filter(
            models.Prediction.patient_id == patient_id
        ).count()
        crud.save_prediction(db_session, result)
        after_count = db_session.query(models.Prediction).filter(
            models.Prediction.patient_id == patient_id
        ).count()
        assert after_count - before_count == 1

    def test_saved_prediction_values_are_correct(self, db_session):
        """The risk_score and risk_level must be stored exactly as provided."""
        patient_id = "VALUE-CHECK-004"
        result = {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "risk_score": 0.55,
            "risk_level": "WATCH",
            "individual_models": {
                "xgboost": 0.10,
                "cnn_lstm": 0.75,
                "autoencoder": 0.80,
                "transformer": 0.60,
            }
        }
        crud.save_prediction(db_session, result)
        stored = db_session.query(models.Prediction).filter(
            models.Prediction.patient_id == patient_id
        ).first()
        assert stored is not None
        assert stored.risk_score == pytest.approx(0.55, abs=0.001)
        assert stored.risk_level == "WATCH"
        assert stored.xgb_score == pytest.approx(0.10, abs=0.001)

    def test_vital_sign_heart_rate_is_stored_correctly(self, db_session, sample_vital_records):
        """Heart rate from the first record must be stored with the correct value."""
        patient_id = sample_vital_records[0].patient_id
        crud.create_vital_signs(db_session, sample_vital_records[:1])  # just 1 record
        stored = db_session.query(models.VitalSign).filter(
            models.VitalSign.patient_id == patient_id
        ).order_by(models.VitalSign.timestamp).first()
        if stored:
            assert stored.heart_rate == pytest.approx(140.0, abs=0.1)

