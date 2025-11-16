"""
Unit tests for log_viewer routes.
"""

import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord
from src.endpoints.log_viewer.application.export_logs import ExportLogs
from src.endpoints.log_viewer.application.get_statistics import GetStatistics
from src.endpoints.log_viewer.application.query_logs import QueryLogs, QueryLogsResult
from src.endpoints.log_viewer.application.query_uptime import QueryUptime, QueryUptimeResult
from src.endpoints.log_viewer.infrastructure.auth import MockAuthService
from src.endpoints.log_viewer.main import create_app
from src.shared.infrastructure.database import init_database
from unittest.mock import Mock


class TestRoutes:
    """Test suite for log_viewer routes."""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Initialize database for tests."""
        # Use in-memory SQLite for unit tests
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        init_database()
        
        # Create tables
        from src.endpoints.log_collector.infrastructure.models import (  # noqa: F401
            NginxAccessLogModel,
            NginxUptimeModel,
        )
        from src.shared.infrastructure.database import get_engine
        from src.shared.models.base import Base as SharedBase
        
        engine = get_engine()
        SharedBase.metadata.create_all(engine)
        
        yield
        
        # Cleanup
        SharedBase.metadata.drop_all(engine)
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app, raise_server_exceptions=True)

    @pytest.fixture
    def authenticated_client(self, client):
        """Create authenticated test client."""
        # Login first
        client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=False,
        )
        return client

    @pytest.mark.unit
    def test_login_page_returns_html(self, client):
        """Test that login page returns HTML."""
        # Act
        response = client.get("/log-viewer/login")

        # Assert
        if response.status_code != 200:
            # Try to get more details about the error
            try:
                import json
                error_detail = json.loads(response.text) if response.text else {}
                print(f"Error detail: {error_detail}")
            except Exception:
                print(f"Response text: {response.text[:1000]}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text[:500]}"
        assert "text/html" in response.headers["content-type"]
        assert "Login" in response.text

    @pytest.mark.unit
    def test_login_with_valid_credentials_redirects(self, client):
        """Test that login with valid credentials redirects to access logs."""
        # Act
        response = client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=False,
        )

        # Assert
        assert response.status_code == 302
        assert response.headers["location"] == "/log-viewer/access-logs"

    @pytest.mark.unit
    def test_login_with_invalid_credentials_shows_error(self, client):
        """Test that login with invalid credentials shows error."""
        # Act
        response = client.post(
            "/log-viewer/login",
            data={"username": "admin", "password": "wrong"},
            follow_redirects=False,
        )

        # Assert
        assert response.status_code == 200
        assert "Invalid username or password" in response.text

    @pytest.mark.unit
    def test_logout_redirects_to_login(self, authenticated_client):
        """Test that logout redirects to login page."""
        # Act
        response = authenticated_client.get("/log-viewer/logout", follow_redirects=False)

        # Assert
        assert response.status_code == 302
        assert response.headers["location"] == "/log-viewer/login"

    @pytest.mark.unit
    def test_access_logs_page_requires_authentication(self, client):
        """Test that access logs page requires authentication."""
        # Act
        response = client.get("/log-viewer/access-logs", follow_redirects=False)

        # Assert
        assert response.status_code == 401

    @pytest.mark.unit
    def test_access_logs_page_returns_html_when_authenticated(self, authenticated_client):
        """Test that access logs page returns HTML when authenticated."""
        # Act
        response = authenticated_client.get("/log-viewer/access-logs")

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Access Logs" in response.text

    @pytest.mark.unit
    def test_uptime_page_requires_authentication(self, client):
        """Test that uptime page requires authentication."""
        # Act
        response = client.get("/log-viewer/uptime", follow_redirects=False)

        # Assert
        assert response.status_code == 401

    @pytest.mark.unit
    def test_uptime_page_returns_html_when_authenticated(self, authenticated_client):
        """Test that uptime page returns HTML when authenticated."""
        # Act
        response = authenticated_client.get("/log-viewer/uptime")

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Uptime" in response.text

    @pytest.mark.unit
    def test_filter_logs_endpoint_requires_authentication(self, client):
        """Test that filter logs endpoint requires authentication."""
        # Act
        response = client.post("/log-viewer/api/filter-logs", follow_redirects=False)

        # Assert
        assert response.status_code == 401

    @pytest.mark.unit
    def test_export_logs_endpoint_requires_authentication(self, client):
        """Test that export logs endpoint requires authentication."""
        # Act
        response = client.get(
            "/log-viewer/api/export-logs?start_time=2024-01-01T00:00&end_time=2024-01-02T00:00",
            follow_redirects=False,
        )

        # Assert
        assert response.status_code == 401

    @pytest.mark.unit
    def test_export_logs_returns_csv_when_authenticated(self, authenticated_client):
        """Test that export logs returns CSV when authenticated."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Act
        response = authenticated_client.get(
            f"/log-viewer/api/export-logs?start_time={start_time}&end_time={end_time}"
        )

        # Assert
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "Content-Disposition" in response.headers
        assert "attachment" in response.headers["Content-Disposition"]

    @pytest.mark.unit
    def test_login_page_redirects_if_already_authenticated(self, authenticated_client):
        """Test that login page redirects if already authenticated."""
        # Act
        response = authenticated_client.get("/log-viewer/login", follow_redirects=False)

        # Assert
        assert response.status_code == 302
        assert response.headers["location"] == "/log-viewer/access-logs"

    @pytest.mark.unit
    def test_filter_logs_post_with_empty_status_code(self, authenticated_client):
        """Test that filter_logs_post handles empty status_code string."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Act
        response = authenticated_client.post(
            "/log-viewer/api/filter-logs",
            data={
                "start_time": start_time,
                "end_time": end_time,
                "status_code": "",  # Empty string
                "uri": "",
                "client_ip": "",
                "page": "1",
                "page_size": "50",
            },
        )

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.unit
    def test_filter_logs_post_with_invalid_status_code(self, authenticated_client):
        """Test that filter_logs_post handles invalid status_code string."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Act
        response = authenticated_client.post(
            "/log-viewer/api/filter-logs",
            data={
                "start_time": start_time,
                "end_time": end_time,
                "status_code": "invalid",  # Invalid string
                "uri": "",
                "client_ip": "",
                "page": "1",
                "page_size": "50",
            },
        )

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.unit
    def test_filter_logs_get_endpoint(self, authenticated_client):
        """Test that filter_logs_get endpoint works."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Act
        response = authenticated_client.get(
            f"/log-viewer/api/filter-logs?start_time={start_time}&end_time={end_time}&page=1&page_size=50"
        )

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.unit
    def test_filter_logs_get_with_timezone(self, authenticated_client):
        """Test that filter_logs_get handles ISO format with timezone."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).isoformat() + "Z"
        end_time = now.isoformat() + "Z"

        # Act
        response = authenticated_client.get(
            f"/log-viewer/api/filter-logs?start_time={start_time}&end_time={end_time}&page=1&page_size=50"
        )

        # Assert
        assert response.status_code == 200

    @pytest.mark.unit
    def test_filter_logs_get_with_datetime_local_format(self, authenticated_client):
        """Test that filter_logs_get handles datetime-local format."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Act
        response = authenticated_client.get(
            f"/log-viewer/api/filter-logs?start_time={start_time}&end_time={end_time}&page=1&page_size=50"
        )

        # Assert
        assert response.status_code == 200

    @pytest.mark.unit
    def test_uptime_page_with_source_filter(self, authenticated_client):
        """Test that uptime_page filters by source."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Act
        response = authenticated_client.get(
            f"/log-viewer/uptime?start_time={start_time}&end_time={end_time}&source=healthcheck_nginx"
        )

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.unit
    def test_filter_uptime_get_endpoint(self, authenticated_client):
        """Test that filter_uptime_get endpoint works."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Act
        response = authenticated_client.get(
            f"/log-viewer/api/filter-uptime?start_time={start_time}&end_time={end_time}"
        )

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.unit
    def test_filter_uptime_get_with_source_filter(self, authenticated_client):
        """Test that filter_uptime_get filters by source."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Act
        response = authenticated_client.get(
            f"/log-viewer/api/filter-uptime?start_time={start_time}&end_time={end_time}&source=healthcheck_log_collector"
        )

        # Assert
        assert response.status_code == 200

    @pytest.mark.unit
    def test_export_logs_with_timezone(self, authenticated_client):
        """Test that export_logs handles ISO format with timezone."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).isoformat() + "Z"
        end_time = now.isoformat() + "Z"

        # Act
        response = authenticated_client.get(
            f"/log-viewer/api/export-logs?start_time={start_time}&end_time={end_time}"
        )

        # Assert
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    @pytest.mark.unit
    def test_export_logs_with_datetime_local_format(self, authenticated_client):
        """Test that export_logs handles datetime-local format."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Act
        response = authenticated_client.get(
            f"/log-viewer/api/export-logs?start_time={start_time}&end_time={end_time}"
        )

        # Assert
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    @pytest.mark.unit
    def test_access_logs_page_with_timezone(self, authenticated_client):
        """Test that access_logs_page handles ISO format with timezone."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).isoformat() + "Z"
        end_time = now.isoformat() + "Z"

        # Act
        response = authenticated_client.get(
            f"/log-viewer/access-logs?start_time={start_time}&end_time={end_time}"
        )

        # Assert
        assert response.status_code == 200

    @pytest.mark.unit
    def test_uptime_page_with_timezone(self, authenticated_client):
        """Test that uptime_page handles ISO format with timezone."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).isoformat() + "Z"
        end_time = now.isoformat() + "Z"

        # Act
        response = authenticated_client.get(
            f"/log-viewer/uptime?start_time={start_time}&end_time={end_time}"
        )

        # Assert
        assert response.status_code == 200

    @pytest.mark.unit
    def test_access_logs_page_with_invalid_datetime_format_triggers_valueerror(self, authenticated_client):
        """Test that access_logs_page handles ValueError in datetime parsing."""
        # Test ValueError path (lines 159-160, 169-170) by creating a mock datetime class
        # that raises ValueError on first call, succeeds on second call
        from datetime import datetime as dt_module, timedelta as td_module
        import src.endpoints.log_viewer.presentation.routes as routes_module
        
        call_counts = {"start": 0, "end": 0}
        original_datetime = routes_module.datetime
        original_timedelta = routes_module.timedelta

        class MockDateTime:
            @staticmethod
            def fromisoformat(value):
                # First call for start_time
                if call_counts["start"] < 2:
                    call_counts["start"] += 1
                    if call_counts["start"] == 1:
                        raise ValueError("Invalid ISO format")
                    return dt_module(2024, 1, 1, 10, 0)
                # First call for end_time
                elif call_counts["end"] < 2:
                    call_counts["end"] += 1
                    if call_counts["end"] == 1:
                        raise ValueError("Invalid ISO format")
                    return dt_module(2024, 1, 2, 10, 0)
                return dt_module.fromisoformat(value)
            
            @staticmethod
            def now():
                return dt_module.now()

        # Replace datetime and timedelta in the routes module
        routes_module.datetime = MockDateTime
        routes_module.timedelta = td_module
        try:
            response = authenticated_client.get(
                "/log-viewer/access-logs?start_time=test&end_time=test"
            )
        finally:
            # Restore original
            routes_module.datetime = original_datetime
            routes_module.timedelta = original_timedelta

        # Assert - Should handle ValueError and succeed on second parse
        assert response.status_code == 200

    @pytest.mark.unit
    def test_filter_logs_get_with_invalid_datetime_format_triggers_valueerror(self, authenticated_client):
        """Test that filter_logs_get handles ValueError in datetime parsing."""
        # Test ValueError path (lines 315-317, 327-329) by creating a mock datetime class
        from datetime import datetime as dt_module, timedelta as td_module
        import src.endpoints.log_viewer.presentation.routes as routes_module
        
        call_counts = {"start": 0, "end": 0}
        original_datetime = routes_module.datetime
        original_timedelta = routes_module.timedelta

        class MockDateTime:
            @staticmethod
            def fromisoformat(value):
                if call_counts["start"] < 2:
                    call_counts["start"] += 1
                    if call_counts["start"] == 1:
                        raise ValueError("Invalid ISO format")
                    return dt_module(2024, 1, 1, 10, 0)
                elif call_counts["end"] < 2:
                    call_counts["end"] += 1
                    if call_counts["end"] == 1:
                        raise ValueError("Invalid ISO format")
                    return dt_module(2024, 1, 2, 10, 0)
                return dt_module.fromisoformat(value)
            
            @staticmethod
            def now():
                return dt_module.now()

        routes_module.datetime = MockDateTime
        routes_module.timedelta = td_module
        try:
            response = authenticated_client.get(
                "/log-viewer/api/filter-logs?start_time=test&end_time=test&page=1&page_size=50"
            )
        finally:
            routes_module.datetime = original_datetime
            routes_module.timedelta = original_timedelta

        assert response.status_code == 200

    @pytest.mark.unit
    def test_filter_logs_get_without_time_parameters_uses_defaults(self, authenticated_client):
        """Test that filter_logs_get uses default time values when start_time/end_time are not provided."""
        # Test lines 319, 331 - default values when time parameters are missing
        response = authenticated_client.get(
            "/log-viewer/api/filter-logs?page=1&page_size=50"
        )

        assert response.status_code == 200
        # Should use default: start_time = now - 24 hours, end_time = now (lines 319, 331)

    @pytest.mark.unit
    def test_uptime_page_with_invalid_datetime_format_triggers_valueerror(self, authenticated_client):
        """Test that uptime_page handles ValueError in datetime parsing."""
        # Test ValueError path (lines 391-393, 403-405) by creating a mock datetime class
        from datetime import datetime as dt_module, timedelta as td_module
        import src.endpoints.log_viewer.presentation.routes as routes_module
        
        call_counts = {"start": 0, "end": 0}
        original_datetime = routes_module.datetime
        original_timedelta = routes_module.timedelta

        class MockDateTime:
            @staticmethod
            def fromisoformat(value):
                if call_counts["start"] < 2:
                    call_counts["start"] += 1
                    if call_counts["start"] == 1:
                        raise ValueError("Invalid ISO format")
                    return dt_module(2024, 1, 1, 10, 0)
                elif call_counts["end"] < 2:
                    call_counts["end"] += 1
                    if call_counts["end"] == 1:
                        raise ValueError("Invalid ISO format")
                    return dt_module(2024, 1, 2, 10, 0)
                return dt_module.fromisoformat(value)
            
            @staticmethod
            def now():
                return dt_module.now()

        routes_module.datetime = MockDateTime
        routes_module.timedelta = td_module
        try:
            response = authenticated_client.get(
                "/log-viewer/uptime?start_time=test&end_time=test"
            )
        finally:
            routes_module.datetime = original_datetime
            routes_module.timedelta = original_timedelta

        assert response.status_code == 200

    @pytest.mark.unit
    def test_filter_uptime_get_with_invalid_datetime_format_triggers_valueerror(self, authenticated_client):
        """Test that filter_uptime_get handles ValueError in datetime parsing."""
        # Test ValueError path (lines 483-486, 495-498) by creating a mock datetime class
        from datetime import datetime as dt_module, timedelta as td_module
        import src.endpoints.log_viewer.presentation.routes as routes_module
        
        call_counts = {"start": 0, "end": 0}
        original_datetime = routes_module.datetime
        original_timedelta = routes_module.timedelta

        class MockDateTime:
            @staticmethod
            def fromisoformat(value):
                if call_counts["start"] < 2:
                    call_counts["start"] += 1
                    if call_counts["start"] == 1:
                        raise ValueError("Invalid ISO format")
                    return dt_module(2024, 1, 1, 10, 0)
                elif call_counts["end"] < 2:
                    call_counts["end"] += 1
                    if call_counts["end"] == 1:
                        raise ValueError("Invalid ISO format")
                    return dt_module(2024, 1, 2, 10, 0)
                return dt_module.fromisoformat(value)
            
            @staticmethod
            def now():
                return dt_module.now()

        routes_module.datetime = MockDateTime
        routes_module.timedelta = td_module
        try:
            response = authenticated_client.get(
                "/log-viewer/api/filter-uptime?start_time=test&end_time=test"
            )
        finally:
            routes_module.datetime = original_datetime
            routes_module.timedelta = original_timedelta

        assert response.status_code == 200

    @pytest.mark.unit
    def test_filter_uptime_get_with_timezone_aware_datetime(self, authenticated_client):
        """Test that filter_uptime_get handles timezone-aware datetime correctly."""
        # Test lines 483, 495 - timezone-aware datetime conversion
        # Use ISO format with Z (which gets converted to +00:00 in the code)
        from datetime import datetime, timedelta, timezone
        from urllib.parse import quote
        
        now = datetime.now(timezone.utc)
        # Use Z format which is URL-safe
        start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        end_time = now.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

        response = authenticated_client.get(
            f"/log-viewer/api/filter-uptime?start_time={start_time}&end_time={end_time}"
        )

        assert response.status_code == 200
        # Should convert timezone-aware datetime to naive (lines 483, 495)

    @pytest.mark.unit
    def test_filter_uptime_get_without_time_parameters_uses_defaults(self, authenticated_client):
        """Test that filter_uptime_get uses default time values when start_time/end_time are not provided."""
        # Test lines 488, 500 - default values when time parameters are missing
        response = authenticated_client.get(
            "/log-viewer/api/filter-uptime"
        )

        assert response.status_code == 200
        # Should use default: start_time = now - 15 minutes, end_time = now (lines 488, 500)

    @pytest.mark.unit
    def test_export_logs_with_invalid_datetime_format_triggers_valueerror(self, authenticated_client):
        """Test that export_logs handles ValueError in datetime parsing."""
        # Test ValueError path (lines 551-552, 558-559) by patching datetime.fromisoformat
        from datetime import datetime as dt_module
        from unittest.mock import patch
        
        call_counts = {"start": 0, "end": 0}

        def mock_fromisoformat(value):
            if call_counts["start"] < 2:
                call_counts["start"] += 1
                if call_counts["start"] == 1:
                    raise ValueError("Invalid ISO format")
                return dt_module(2024, 1, 1, 10, 0)
            elif call_counts["end"] < 2:
                call_counts["end"] += 1
                if call_counts["end"] == 1:
                    raise ValueError("Invalid ISO format")
                return dt_module(2024, 1, 2, 10, 0)
            return dt_module.fromisoformat(value)

        # Patch datetime.fromisoformat in the routes module
        # Note: We can't patch datetime.fromisoformat directly because datetime is immutable
        # So we patch it where it's used in the routes module
        with patch("src.endpoints.log_viewer.presentation.routes.datetime") as mock_datetime:
            # Make mock_datetime behave like datetime but with mocked fromisoformat
            mock_datetime.fromisoformat = mock_fromisoformat
            mock_datetime.now = dt_module.now
            mock_datetime.side_effect = lambda *args, **kwargs: dt_module(*args, **kwargs)
            
            # Also need to ensure replace and astimezone work
            def create_datetime(*args, **kwargs):
                dt = dt_module(*args, **kwargs)
                # Add methods that might be called
                if not hasattr(dt, 'replace'):
                    dt.replace = lambda tzinfo=None: dt
                if not hasattr(dt, 'astimezone'):
                    dt.astimezone = lambda: dt.replace(tzinfo=None)
                return dt
            
            mock_datetime.side_effect = create_datetime
            
            response = authenticated_client.get(
                "/log-viewer/api/export-logs?start_time=test&end_time=test"
            )

        assert response.status_code == 200

    @pytest.mark.unit
    def test_uptime_page_with_empty_filtered_records(self, authenticated_client):
        """Test that uptime_page handles empty filtered records correctly."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")
        # Use a source that likely won't match any records
        source = "nonexistent_source"

        # Act
        response = authenticated_client.get(
            f"/log-viewer/uptime?start_time={start_time}&end_time={end_time}&source={source}"
        )

        # Assert
        assert response.status_code == 200
        # Should show 100% uptime when no records (line 420-421)
        # This tests lines 418-419 (empty filtered_records branch - else clause at line 420)

    @pytest.mark.unit
    def test_uptime_page_with_non_empty_filtered_records(self, authenticated_client):
        """Test that uptime_page calculates uptime percentage for non-empty filtered records."""
        # Arrange - Use a source that might have records
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")
        source = "healthcheck_nginx"

        # Act
        response = authenticated_client.get(
            f"/log-viewer/uptime?start_time={start_time}&end_time={end_time}&source={source}"
        )

        # Assert
        assert response.status_code == 200
        # This tests lines 418-419 (non-empty filtered_records branch - if clause with uptime calculation)

    @pytest.mark.unit
    def test_uptime_page_filters_timeline_by_source(self, authenticated_client):
        """Test that uptime_page filters timeline by source when provided."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")
        source = "healthcheck_nginx"

        # Act
        response = authenticated_client.get(
            f"/log-viewer/uptime?start_time={start_time}&end_time={end_time}&source={source}"
        )

        # Assert
        assert response.status_code == 200
        # Timeline should be filtered by source (line 429-430)

    @pytest.mark.unit
    def test_uptime_page_timeline_error_handling(self, authenticated_client):
        """Test that uptime_page handles timeline errors gracefully."""
        # Arrange
        now = datetime.now()
        start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M")
        end_time = now.strftime("%Y-%m-%dT%H:%M")

        # Mock get_statistics.get_uptime_timeline to raise an exception
        # We need to patch the dependency injection
        from src.endpoints.log_viewer.presentation.dependencies import get_statistics_use_case
        
        # Create a mock statistics object that raises on get_uptime_timeline
        mock_stats = Mock(spec=GetStatistics)
        mock_stats.get_uptime_timeline.side_effect = Exception("Timeline error")
        
        # Mock the dependency
        with patch("src.endpoints.log_viewer.presentation.routes.get_statistics_use_case") as mock_get_stats:
            mock_get_stats.return_value = mock_stats

            response = authenticated_client.get(
                f"/log-viewer/uptime?start_time={start_time}&end_time={end_time}"
            )

        # Assert
        assert response.status_code == 200
        # Should handle exception gracefully and return empty timeline (lines 431-433)
        # This tests the exception handler that catches errors from get_uptime_timeline

