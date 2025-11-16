"""
Integration tests for health check endpoint.

Tests the /health endpoint with database connectivity checks.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(test_app):
    """
    Provide a test client for the FastAPI application.

    Args:
        test_app: FastAPI application fixture from conftest.

    Returns:
        TestClient instance.
    """
    return TestClient(test_app)


class TestHealthEndpoint:
    """Integration test suite for health check endpoint."""

    @pytest.mark.integration
    def test_health_check_returns_200(self, client):
        """Test that health check returns 200 OK."""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert "database" in data

    @pytest.mark.integration
    def test_health_check_includes_database_status(self, client):
        """Test that health check includes database connection status."""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["database"] in ["connected", "disconnected"]
