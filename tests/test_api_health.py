"""
tests/test_api_health.py
-------------------------
Tests for the basic health-check endpoint.

Why do we test this?
  The health endpoint is the simplest possible thing to test — if this fails,
  it means the entire server failed to start (missing imports, config errors, etc.)
  It is the "canary in the coal mine" test.
"""

class TestHealthCheck:

    def test_root_returns_200(self, client):
        """Server must respond with HTTP 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_has_status_field(self, client):
        """Response JSON must contain a 'status' field."""
        response = client.get("/")
        data = response.json()
        assert "status" in data

    def test_root_reports_online(self, client):
        """The status field must say 'online'."""
        response = client.get("/")
        assert response.json()["status"] == "online"

    def test_root_has_message(self, client):
        """Response must contain a human-readable message."""
        response = client.get("/")
        assert "message" in response.json()

    def test_models_loaded_flag_is_bool(self, client):
        """The 'models_loaded' field must be a boolean."""
        response = client.get("/")
        data = response.json()
        assert isinstance(data.get("models_loaded"), bool)

