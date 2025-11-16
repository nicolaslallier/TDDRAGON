"""
Integration tests for health check error handling.

Tests health check behavior when database connection fails.
"""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.shared.infrastructure.database import get_session


@pytest.fixture
def client(test_app):
    """Provide a test client for the FastAPI app."""
    return TestClient(test_app)


class TestHealthErrorHandling:
    """Test suite for health check error handling."""

    @pytest.mark.integration
    def test_health_check_with_database_error_returns_down(self, test_app, client):
        """Test that health check returns DOWN when database connection fails."""
        # Arrange
        # Create a mock session that raises an exception
        mock_session = MagicMock(spec=Session)
        mock_session.execute = MagicMock(side_effect=Exception("Connection failed"))

        def mock_get_session():
            yield mock_session

        # Override the dependency
        test_app.dependency_overrides[get_session] = mock_get_session

        try:
            # Act
            response = client.get("/health")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "DOWN"
            assert data["database"] == "disconnected"
        finally:
            # Cleanup: remove the override
            test_app.dependency_overrides.pop(get_session, None)
