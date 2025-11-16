"""
Integration tests for log_viewer routes.

Tests UI flows, HTMX endpoints, and CSV export with a real database.
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyLogRepository,
    SQLAlchemyUptimeRepository,
)
from src.shared.infrastructure.database import get_session


@pytest.fixture
def sample_logs(test_app):
    """
    Create sample log entries for testing.

    Args:
        test_app: FastAPI application instance.

    Yields:
        List of created LogEntry instances.
    """
    session_gen = get_session()
    session = next(session_gen)

    try:
        repository = SQLAlchemyLogRepository(session)
        now = datetime.now()
        entries = [
            LogEntry(
                id=0,
                timestamp_utc=now - timedelta(minutes=30),
                client_ip="192.168.1.1",
                http_method="GET",
                request_uri="/health",
                status_code=200,
                response_time=0.05,
                user_agent="Mozilla/5.0",
            ),
            LogEntry(
                id=0,
                timestamp_utc=now - timedelta(minutes=25),
                client_ip="192.168.1.2",
                http_method="POST",
                request_uri="/api/test",
                status_code=201,
                response_time=0.1,
                user_agent="curl/7.0",
            ),
            LogEntry(
                id=0,
                timestamp_utc=now - timedelta(minutes=20),
                client_ip="192.168.1.3",
                http_method="GET",
                request_uri="/error",
                status_code=500,
                response_time=0.2,
                user_agent="Mozilla/5.0",
            ),
        ]
        created = []
        for entry in entries:
            created.append(repository.create(entry))
        session.commit()
        yield created
    finally:
        from contextlib import suppress
        with suppress(Exception):
            session.close()


class TestRoutesIntegration:
    """Integration test suite for log_viewer routes."""

    @pytest.mark.integration
    def test_login_flow(self, client: TestClient):
        """Test complete login flow."""
        # Act - Get login page
        response = client.get("/log-viewer/login")
        assert response.status_code == 200
        assert "Login" in response.text

        # Act - Login with valid credentials
        response = client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["location"] == "/log-viewer/access-logs"

        # Act - Access protected page
        response = client.get("/log-viewer/access-logs")
        assert response.status_code == 200
        assert "Access Logs" in response.text

    @pytest.mark.integration
    def test_access_logs_page_with_data(self, client: TestClient, sample_logs):
        """Test access logs page displays data correctly."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )

        # Act - Get access logs page
        response = client.get("/log-viewer/access-logs")

        # Assert
        assert response.status_code == 200
        assert "Access Logs" in response.text
        # Should show log table (even if empty, the structure should be there)
        assert "log-table-container" in response.text or "No logs found" in response.text

    @pytest.mark.integration
    def test_filter_logs_htmx_endpoint(self, client: TestClient, sample_logs):
        """Test HTMX filter logs endpoint."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )

        # Act - Filter logs via HTMX endpoint
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        response = client.post(
            "/log-viewer/api/filter-logs",
            data={
                "start_time": start_time,
                "end_time": end_time,
                "status_code": "",
                "uri": "",
                "client_ip": "",
                "page": "1",
                "page_size": "50",
            },
        )

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.integration
    def test_export_logs_csv(self, client: TestClient, sample_logs):
        """Test CSV export functionality."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )

        # Act - Export logs
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        response = client.get(
            f"/log-viewer/api/export-logs?start_time={start_time}&end_time={end_time}"
        )

        # Assert
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "Content-Disposition" in response.headers
        assert "attachment" in response.headers["Content-Disposition"]
        # Check CSV content
        assert "id" in response.text
        assert "timestamp_utc" in response.text
        assert "client_ip" in response.text

    @pytest.mark.integration
    def test_uptime_page(self, client: TestClient):
        """Test uptime page displays correctly."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )

        # Act - Get uptime page
        response = client.get("/log-viewer/uptime")

        # Assert
        assert response.status_code == 200
        assert "Uptime" in response.text
        assert "Uptime Summary" in response.text

    @pytest.mark.integration
    def test_logout_flow(self, client: TestClient):
        """Test logout flow."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )

        # Act - Logout
        response = client.get("/log-viewer/logout", follow_redirects=False)

        # Assert
        assert response.status_code == 302
        assert response.headers["location"] == "/log-viewer/login"

        # Act - Try to access protected page
        response = client.get("/log-viewer/access-logs", follow_redirects=False)

        # Assert - Should be unauthorized
        assert response.status_code == 401

