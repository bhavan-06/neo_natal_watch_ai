"""
tests/test_api_chatbot.py
--------------------------
Tests for the POST /api/v1/chat/ endpoint.

Why test the chatbot?
  The chatbot reads live data from the database and does pattern-matching.
  We need to verify:
    1. It responds to every question with something (never crashes)
    2. It provides a fallback for unknown questions
    3. After a prediction is stored, it correctly reads and reports that data
    4. The response schema is always valid
"""

import pytest


class TestChatbotEndpoint:

    def _chat(self, client, message, patient_id="TEST-PATIENT-001"):
        """Helper: sends a chat message and returns the response dict."""
        return client.post(
            "/api/v1/chat/",
            json={"message": message, "patient_id": patient_id}
        )

    # ------------------------------------------------------------------
    # Basic structural tests
    # ------------------------------------------------------------------

    def test_chat_returns_200(self, client):
        """Any message must return HTTP 200."""
        response = self._chat(client, "hello")
        assert response.status_code == 200

    def test_chat_response_has_reply_field(self, client):
        """The response must always contain a 'reply' key."""
        response = self._chat(client, "hello")
        assert "reply" in response.json()

    def test_chat_reply_is_non_empty_string(self, client):
        """The reply must never be an empty string."""
        response = self._chat(client, "hello")
        reply = response.json()["reply"]
        assert isinstance(reply, str)
        assert len(reply) > 0

    # ------------------------------------------------------------------
    # Greeting tests
    # ------------------------------------------------------------------

    def test_chat_responds_to_hello(self, client):
        """The bot must greet the user when they say hello."""
        response = self._chat(client, "hello")
        reply = response.json()["reply"].lower()
        assert "hello" in reply or "assistant" in reply or "ask" in reply

    def test_chat_responds_to_help(self, client):
        """Asking for help must return a list of available topics."""
        response = self._chat(client, "help")
        reply = response.json()["reply"].lower()
        assert "risk" in reply or "heart" in reply or "spo2" in reply

    # ------------------------------------------------------------------
    # Fallback / unknown-question test
    # ------------------------------------------------------------------

    def test_chat_handles_unknown_question(self, client):
        """A completely unrecognized question must return the fallback message."""
        response = self._chat(client, "tell me about dinosaurs")
        reply = response.json()["reply"].lower()
        # Should fall back to suggesting known topics
        assert "risk" in reply or "heart" in reply or "didn't understand" in reply

    # ------------------------------------------------------------------
    # Data-aware tests (run AFTER a prediction has been stored in DB)
    # ------------------------------------------------------------------

    def test_chat_reports_risk_score_after_prediction(self, client, vital_records):
        """
        If a prediction has been stored, asking about risk score must
        return the actual score — not a 'no data' message.
        """
        # First, create a prediction so the DB has something to report
        client.post("/api/v1/predict/", json={"records": vital_records})

        # Now ask the chatbot
        response = self._chat(client, "what is the risk score?")
        reply = response.json()["reply"]
        assert "%" in reply, f"Expected a percentage in reply, got: {reply}"

    def test_chat_reports_heart_rate_after_prediction(self, client, vital_records):
        """After storing vitals, asking about heart rate must return a bpm value."""
        client.post("/api/v1/predict/", json={"records": vital_records})
        response = self._chat(client, "heart rate")
        reply = response.json()["reply"]
        assert "bpm" in reply.lower(), f"Expected 'bpm' in reply, got: {reply}"

    def test_chat_reports_spo2_after_prediction(self, client, vital_records):
        """After storing vitals, asking about SpO2 must return a percentage value."""
        client.post("/api/v1/predict/", json={"records": vital_records})
        response = self._chat(client, "spo2")
        reply = response.json()["reply"]
        assert "%" in reply, f"Expected '%' in reply, got: {reply}"

    def test_chat_reports_model_breakdown_after_prediction(self, client, vital_records):
        """After storing a prediction, asking about models must return XGBoost score."""
        client.post("/api/v1/predict/", json={"records": vital_records})
        response = self._chat(client, "model breakdown")
        reply = response.json()["reply"]
        assert "xgboost" in reply.lower(), f"Expected 'XGBoost' in reply, got: {reply}"

    # ------------------------------------------------------------------
    # Validation tests
    # ------------------------------------------------------------------

    def test_chat_rejects_missing_message(self, client):
        """Sending a payload with no 'message' field must return HTTP 422."""
        response = client.post("/api/v1/chat/", json={"patient_id": "TEST-PATIENT-001"})
        assert response.status_code == 422

    def test_chat_works_with_different_patient_ids(self, client):
        """Chatbot must work for any patient_id, even one with no DB records."""
        response = self._chat(client, "risk score", patient_id="NON-EXISTENT-PATIENT-999")
        assert response.status_code == 200
        # Should get a 'no data' message, not a crash
        reply = response.json()["reply"]
        assert isinstance(reply, str) and len(reply) > 0

