"""
tests/test_api_predict.py
--------------------------
Integration tests for the POST /api/v1/predict/ endpoint.

Why do we test predictions?
  The predict endpoint is the HEART of the whole application.
  We need to make sure it:
    1. Accepts properly formed requests and returns a risk score
    2. Rejects bad/incomplete data with a clear error message
    3. Always returns risk scores between 0.0 and 1.0
    4. Always assigns a valid risk level (LOW / WATCH / HIGH)
    5. Returns scores from all four individual models
"""

import pytest


class TestPredictEndpoint:

    # ------------------------------------------------------------------
    # Happy-path tests (valid input)
    # ------------------------------------------------------------------

    def test_predict_returns_200_on_valid_input(self, client, vital_records):
        """A complete set of 60 vital records must return HTTP 200."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        assert response.status_code == 200

    def test_predict_response_has_required_fields(self, client, vital_records):
        """Response must contain patient_id, timestamp, risk_score, risk_level, individual_models."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        data = response.json()
        required_fields = ["patient_id", "timestamp", "risk_score", "risk_level", "individual_models"]
        for field in required_fields:
            assert field in data, f"Missing required field: '{field}'"

    def test_predict_risk_score_is_between_0_and_1(self, client, vital_records):
        """The Fusion risk score must always be a probability between 0.0 and 1.0."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        score = response.json()["risk_score"]
        assert 0.0 <= score <= 1.0, f"Risk score out of range: {score}"

    def test_predict_risk_level_is_valid(self, client, vital_records):
        """Risk level must be one of LOW, WATCH, or HIGH — nothing else."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        level = response.json()["risk_level"]
        assert level in ["LOW", "WATCH", "HIGH"], f"Unknown risk level: '{level}'"

    def test_predict_individual_models_are_present(self, client, vital_records):
        """All four model scores must be present in the response."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        models = response.json()["individual_models"]
        assert "xgboost" in models
        assert "cnn_lstm" in models
        assert "autoencoder" in models
        assert "transformer" in models

    def test_predict_individual_scores_in_range(self, client, vital_records):
        """Every individual model score must also be between 0.0 and 1.0."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        models = response.json()["individual_models"]
        for model_name, score in models.items():
            assert 0.0 <= score <= 1.0, f"{model_name} score out of range: {score}"

    def test_predict_patient_id_matches_input(self, client, vital_records):
        """The patient_id in the response must match what we sent."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        assert response.json()["patient_id"] == "TEST-PATIENT-001"

    def test_predict_normal_vitals_produces_lower_risk(self, client, vital_records, normal_vital_records):
        """
        A patient with stable, normal vitals should receive a lower risk score
        than a patient with a clear deteriorating trend.
        This is a sanity check on the AI's direction of learning.
        """
        deteriorating = client.post("/api/v1/predict/", json={"records": vital_records}).json()
        normal = client.post("/api/v1/predict/", json={"records": normal_vital_records}).json()
        assert normal["risk_score"] <= deteriorating["risk_score"], (
            f"Expected normal score ({normal['risk_score']}) <= "
            f"deteriorating score ({deteriorating['risk_score']})"
        )

    # ------------------------------------------------------------------
    # Error / validation tests (bad input)
    # ------------------------------------------------------------------

    def test_predict_rejects_empty_payload(self, client):
        """Sending an empty body must return HTTP 422 (Unprocessable Entity)."""
        response = client.post("/api/v1/predict/", json={})
        assert response.status_code == 422

    def test_predict_rejects_too_few_records(self, client, vital_records):
        """
        Sending fewer than 60 records must fail — the AI needs a full hour of data.
        (The feature engineering requires 60 rows to compute 60-minute rolling stats.)
        """
        # Send only 30 records — not enough for feature engineering
        short_records = vital_records[:30]
        response = client.post("/api/v1/predict/", json={"records": short_records})
        # Should return either 422 (validation) or 400 (application error)
        assert response.status_code in [400, 422]

    def test_predict_rejects_missing_heart_rate(self, client, vital_records):
        """A record missing the heart_rate field must trigger a validation error."""
        bad_records = [r.copy() for r in vital_records]
        del bad_records[0]["heart_rate"]  # remove a required field
        response = client.post("/api/v1/predict/", json={"records": bad_records})
        assert response.status_code == 422

    def test_predict_rejects_non_numeric_vital(self, client, vital_records):
        """A non-numeric value in heart_rate must be rejected by Pydantic validation."""
        bad_records = [r.copy() for r in vital_records]
        bad_records[0]["heart_rate"] = "not-a-number"
        response = client.post("/api/v1/predict/", json={"records": bad_records})
        assert response.status_code == 422

    def test_predict_message_field_present(self, client, vital_records):
        """Success response must include a 'message' field for front-end display."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        assert "message" in response.json()

