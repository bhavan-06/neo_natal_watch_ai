"""
tests/test_schemas.py
----------------------
Tests for our Pydantic data validation schemas.

Why test schemas?
  Pydantic schemas are the FRONT DOOR of our API — they decide what data
  is allowed in. If they are too strict, valid data gets rejected.
  If they are too lenient, garbage data reaches the AI models and causes crashes.
  
  These tests are "unit tests" — they test tiny, isolated pieces of logic
  without touching the database or the network at all.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from backend.app.schemas.predict_schema import (
    VitalSignRecord,
    PredictionRequest,
    PredictionResponse,
)


class TestVitalSignRecord:
    """Tests for the VitalSignRecord Pydantic model."""

    def _valid_record(self, **overrides):
        """Helper that returns a dict of valid vital signs, with optional overrides."""
        base = {
            "timestamp": datetime.now().isoformat(),
            "patient_id": "SCHEMA-TEST-001",
            "heart_rate": 145.0,
            "spo2": 95.0,
            "respiratory_rate": 45.0,
            "temperature": 37.0,
            "systolic_bp": 62.0,
            "diastolic_bp": 41.0,
        }
        base.update(overrides)
        return base

    def test_valid_record_accepted(self):
        """A complete, correct vital record must be accepted without error."""
        record = VitalSignRecord(**self._valid_record())
        assert record.heart_rate == 145.0

    def test_missing_heart_rate_raises_validation_error(self):
        """heart_rate is a required field — omitting it must raise ValidationError."""
        data = self._valid_record()
        del data["heart_rate"]
        with pytest.raises(ValidationError):
            VitalSignRecord(**data)

    def test_missing_spo2_raises_validation_error(self):
        """spo2 is a required field — omitting it must raise ValidationError."""
        data = self._valid_record()
        del data["spo2"]
        with pytest.raises(ValidationError):
            VitalSignRecord(**data)

    def test_string_heart_rate_raises_validation_error(self):
        """heart_rate must be a number — a string must be rejected."""
        with pytest.raises(ValidationError):
            VitalSignRecord(**self._valid_record(heart_rate="fast"))

    def test_missing_patient_id_raises_validation_error(self):
        """patient_id is required — it identifies whose data this is."""
        data = self._valid_record()
        del data["patient_id"]
        with pytest.raises(ValidationError):
            VitalSignRecord(**data)

    def test_missing_timestamp_raises_validation_error(self):
        """timestamp is required — we need to know when each reading was taken."""
        data = self._valid_record()
        del data["timestamp"]
        with pytest.raises(ValidationError):
            VitalSignRecord(**data)

    def test_float_values_are_stored_as_float(self):
        """Numeric vitals must be stored as floats, not strings or ints."""
        record = VitalSignRecord(**self._valid_record(heart_rate=140))
        assert isinstance(record.heart_rate, float)


class TestPredictionRequest:
    """Tests for the PredictionRequest Pydantic model (the full /predict payload)."""

    def _make_records(self, n=60):
        base = datetime.now()
        from datetime import timedelta
        return [
            {
                "timestamp": (base - timedelta(minutes=60 - i)).isoformat(),
                "patient_id": "SCHEMA-TEST-002",
                "heart_rate": 140.0 + i,
                "spo2": 96.0,
                "respiratory_rate": 45.0,
                "temperature": 37.0,
                "systolic_bp": 62.0,
                "diastolic_bp": 41.0,
            }
            for i in range(n)
        ]

    def test_valid_request_accepted(self):
        """60 valid records must form a valid PredictionRequest."""
        req = PredictionRequest(records=self._make_records(60))
        assert len(req.records) == 60

    def test_empty_records_list_raises_validation_error(self):
        """An empty records list must be rejected."""
        with pytest.raises(ValidationError):
            PredictionRequest(records=[])

    def test_missing_records_field_raises_validation_error(self):
        """A payload with no 'records' key at all must fail validation."""
        with pytest.raises(ValidationError):
            PredictionRequest()


class TestPredictionResponse:
    """Tests for the PredictionResponse schema (what we send back to the client)."""

    def _valid_response(self, **overrides):
        base = {
            "patient_id": "SCHEMA-TEST-003",
            "timestamp": datetime.now().isoformat(),
            "risk_score": 0.67,
            "risk_level": "WATCH",
            "individual_models": {
                "xgboost": 0.15,
                "cnn_lstm": 0.99,
                "autoencoder": 0.98,
                "transformer": 0.82,
            },
            "message": "Prediction successful",
        }
        base.update(overrides)
        return base

    def test_valid_response_accepted(self):
        """A complete, correct response must be accepted without error."""
        resp = PredictionResponse(**self._valid_response())
        assert resp.risk_level == "WATCH"

    def test_missing_risk_score_raises_error(self):
        """risk_score is required — the frontend displays it prominently."""
        data = self._valid_response()
        del data["risk_score"]
        with pytest.raises(ValidationError):
            PredictionResponse(**data)

    def test_missing_individual_models_raises_error(self):
        """individual_models is required — it powers the model breakdown panel."""
        data = self._valid_response()
        del data["individual_models"]
        with pytest.raises(ValidationError):
            PredictionResponse(**data)

