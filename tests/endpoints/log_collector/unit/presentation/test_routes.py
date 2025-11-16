"""
Unit tests for log_collector routes.

Tests HTTP endpoints for querying logs and uptime.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord
from src.endpoints.log_collector.main import create_app
from src.endpoints.log_collector.presentation.dependencies import (
    get_calculate_uptime_use_case,
    get_log_repository,
    get_uptime_repository,
)


class TestRoutes:
    """Test suite for log_collector routes."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        app = create_app()
        return TestClient(app)

    @pytest.mark.unit
    def test_health_check_returns_ok(self, client):
        """Test that health check endpoint returns status ok."""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

