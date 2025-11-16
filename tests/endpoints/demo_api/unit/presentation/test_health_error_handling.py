"""
Unit tests for health endpoint error handling.

Tests error handling paths in the health check endpoint.
"""

from unittest.mock import Mock

import pytest

from src.endpoints.demo_api.presentation.health import health_check


class TestHealthCheckErrorHandling:
    """Test suite for health check error handling."""

    @pytest.mark.unit
    def test_health_check_with_database_error_returns_disconnected(self):
        """Test that health check returns disconnected when database query fails."""
        # Arrange
        mock_session = Mock()
        mock_session.execute.side_effect = Exception("Database connection failed")

        # Act
        response = health_check(session=mock_session)

        # Assert
        assert response.status == "DOWN"
        assert response.database == "disconnected"
