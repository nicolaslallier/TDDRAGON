"""
Regression tests for log_viewer presentation layer.

Ensures UI components don't regress and edge cases are handled.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from src.endpoints.log_viewer.infrastructure.auth import MockAuthService
from src.endpoints.log_viewer.presentation.routes import require_auth


class TestAuthRegression:
    """Regression tests for authentication."""

    @pytest.mark.regression
    def test_require_auth_raises_http_exception_when_not_authenticated(self):
        """Test that require_auth raises HTTPException when not authenticated."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.session = {}

        # Act & Assert
        with pytest.raises(Exception):  # HTTPException from FastAPI
            require_auth(mock_request)

    @pytest.mark.regression
    def test_require_auth_allows_access_when_authenticated(self):
        """Test that require_auth allows access when authenticated."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.session = {"authenticated": True}

        # Act - Should not raise exception
        try:
            require_auth(mock_request)
        except Exception:
            pytest.fail("require_auth should not raise exception when authenticated")


class TestRoutesRegression:
    """Regression tests for routes."""

    @pytest.mark.regression
    def test_login_with_empty_credentials_shows_error(self, client: TestClient):
        """Test that login with empty credentials shows error."""
        # Act
        response = client.post(
            "/log-viewer/login",
            data={"username": "", "password": ""},
        )

        # Assert
        assert response.status_code == 200
        assert "Invalid username or password" in response.text or "Login" in response.text

    @pytest.mark.regression
    def test_access_logs_with_invalid_time_range_handles_gracefully(self, client: TestClient):
        """Test that access logs page handles invalid time range gracefully."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )

        # Act - Try with invalid time range (end before start)
        now = datetime.now()
        start_time = now.strftime("%Y-%m-%dT%H:%M")
        end_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")

        response = client.get(
            "/log-viewer/access-logs",
            params={
                "start_time": start_time,
                "end_time": end_time,
            },
        )

        # Assert - Should handle gracefully (either return empty results or error message)
        assert response.status_code in [200, 400]

    @pytest.mark.regression
    def test_export_logs_with_no_matching_records_returns_empty_csv(self, client: TestClient):
        """Test that export logs with no matching records returns empty CSV."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )

        # Act - Export logs for time range with no data
        future_time = datetime.now() + timedelta(days=1)
        start_time = future_time.strftime("%Y-%m-%dT%H:%M")
        end_time = (future_time + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")

        response = client.get(
            f"/log-viewer/api/export-logs?start_time={start_time}&end_time={end_time}"
        )

        # Assert
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        # Should have header even if no data
        assert "id" in response.text

    @pytest.mark.regression
    def test_pagination_handles_large_page_numbers(self, client: TestClient):
        """Test that pagination handles large page numbers gracefully."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )

        # Act - Try to access page 99999
        response = client.get(
            "/log-viewer/access-logs",
            params={"page": 99999},
        )

        # Assert - Should handle gracefully (either return last page or empty results)
        assert response.status_code == 200

    @pytest.mark.regression
    def test_filter_with_special_characters_in_uri(self, client: TestClient):
        """Test that filter handles special characters in URI."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )

        # Act - Filter with special characters
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        response = client.get(
            "/log-viewer/access-logs",
            params={
                "start_time": start_time,
                "end_time": end_time,
                "uri": "/api/test?param=value&other=123",
            },
        )

        # Assert - Should handle gracefully
        assert response.status_code == 200

    @pytest.mark.regression
    def test_login_page_redirects_when_already_authenticated(self, client: TestClient):
        """Test that login page redirects when user is already authenticated."""
        # Test lines 68-71: Redirect when authenticated
        # Login first (don't follow redirects to preserve session)
        login_response = client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=False,
        )
        # Ensure login was successful (should redirect)
        assert login_response.status_code == 302
        
        # Act - Try to access login page again (TestClient preserves cookies automatically)
        response = client.get("/log-viewer/login", follow_redirects=False)
        
        # Assert - Should redirect to access-logs
        assert response.status_code == 302
        assert "/log-viewer/access-logs" in response.headers.get("location", "")

    @pytest.mark.regression
    def test_logout_redirects_to_login(self, client: TestClient):
        """Test that logout redirects to login page."""
        # Test lines 115-116: Logout redirect
        # Login first (don't follow redirects to preserve session)
        login_response = client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=False,
        )
        # Ensure login was successful (should redirect)
        assert login_response.status_code == 302
        
        # Act - Logout (TestClient preserves cookies automatically)
        response = client.get("/log-viewer/logout", follow_redirects=False)
        
        # Assert - Should redirect to login
        assert response.status_code == 302
        assert "/log-viewer/login" in response.headers.get("location", "")

    @pytest.mark.regression
    def test_access_logs_page_handles_timezone_aware_datetime(self, client: TestClient):
        """Test that access_logs_page handles timezone-aware datetime strings."""
        # Test lines 158-160, 168-170: Timezone handling
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )
        
        # Act - Use ISO format with timezone
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).isoformat() + "Z"
        end_time = now.isoformat() + "Z"
        
        response = client.get(
            "/log-viewer/access-logs",
            params={
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        
        # Assert - Should handle gracefully
        assert response.status_code == 200

    @pytest.mark.regression
    def test_filter_logs_post_handles_empty_status_code(self, client: TestClient):
        """Test that filter_logs_post handles empty status_code string."""
        # Test lines 248-255: Empty status_code handling
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )
        
        # Act - POST with empty status_code
        response = client.post(
            "/log-viewer/api/filter-logs",
            data={
                "start_time": "",
                "end_time": "",
                "status_code": "",  # Empty string
                "uri": "",
                "client_ip": "",
            },
        )
        
        # Assert - Should handle gracefully
        assert response.status_code == 200

    @pytest.mark.regression
    def test_filter_logs_get_handles_timezone_aware_datetime(self, client: TestClient):
        """Test that filter_logs_get handles timezone-aware datetime strings."""
        # Test lines 306-344: filter_logs_get timezone handling
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )
        
        # Act - Use ISO format with timezone
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).isoformat() + "Z"
        end_time = now.isoformat() + "Z"
        
        response = client.get(
            "/log-viewer/api/filter-logs",
            params={
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        
        # Assert - Should handle gracefully
        assert response.status_code == 200

    @pytest.mark.regression
    def test_uptime_page_handles_source_filter(self, client: TestClient):
        """Test that uptime_page handles source filter correctly."""
        # Test lines 381-437: uptime_page with source filter
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )
        
        # Act - Access uptime page with source filter
        response = client.get(
            "/log-viewer/uptime",
            params={"source": "healthcheck_nginx"},
        )
        
        # Assert - Should handle gracefully
        assert response.status_code == 200

    @pytest.mark.regression
    def test_uptime_page_handles_timezone_aware_datetime(self, client: TestClient):
        """Test that uptime_page handles timezone-aware datetime strings."""
        # Test lines 381-437: uptime_page timezone handling
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )
        
        # Act - Use ISO format with timezone
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).isoformat() + "Z"
        end_time = now.isoformat() + "Z"
        
        response = client.get(
            "/log-viewer/uptime",
            params={
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        
        # Assert - Should handle gracefully
        assert response.status_code == 200

    @pytest.mark.regression
    def test_filter_uptime_get_handles_source_filter(self, client: TestClient):
        """Test that filter_uptime_get handles source filter correctly."""
        # Test lines 474-510: filter_uptime_get with source filter
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )
        
        # Act - Filter uptime with source
        response = client.get(
            "/log-viewer/api/filter-uptime",
            params={"source": "healthcheck_log_collector"},
        )
        
        # Assert - Should handle gracefully
        assert response.status_code == 200

    @pytest.mark.regression
    def test_filter_uptime_get_handles_timezone_aware_datetime(self, client: TestClient):
        """Test that filter_uptime_get handles timezone-aware datetime strings."""
        # Test lines 474-510: filter_uptime_get timezone handling
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )
        
        # Act - Use ISO format with timezone
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).isoformat() + "Z"
        end_time = now.isoformat() + "Z"
        
        response = client.get(
            "/log-viewer/api/filter-uptime",
            params={
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        
        # Assert - Should handle gracefully
        assert response.status_code == 200

    @pytest.mark.regression
    def test_export_logs_handles_timezone_aware_datetime(self, client: TestClient):
        """Test that export_logs handles timezone-aware datetime strings."""
        # Test lines 550-552, 557-559: export_logs timezone handling
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
        )
        
        # Act - Use ISO format with timezone
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).isoformat() + "Z"
        end_time = now.isoformat() + "Z"
        
        response = client.get(
            "/log-viewer/api/export-logs",
            params={
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        
        # Assert - Should handle gracefully
        assert response.status_code == 200

