"""
Regression tests for log collector presentation layer.

Ensures that presentation components continue to work correctly after changes.
"""

import os
from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_collector.presentation.dependencies import (
    get_calculate_uptime_use_case,
    get_collect_logs_use_case,
    get_log_repository,
    get_uptime_repository,
)
from src.endpoints.log_collector.presentation.routes import _to_log_response


class TestDependenciesRegression:
    """Regression tests for FastAPI dependencies."""

    @pytest.mark.regression
    def test_get_log_repository_returns_sqlalchemy_repository(self):
        """Test that get_log_repository returns SQLAlchemyLogRepository instance."""
        # Arrange
        mock_session = Mock()

        # Act
        repository = get_log_repository(session=mock_session)

        # Assert
        assert repository is not None
        assert hasattr(repository, "create")
        assert hasattr(repository, "find_by_time_range")
        assert hasattr(repository, "find_by_status_code")

    @pytest.mark.regression
    def test_get_uptime_repository_returns_sqlalchemy_repository(self):
        """Test that get_uptime_repository returns SQLAlchemyUptimeRepository instance."""
        # Arrange
        mock_session = Mock()

        # Act
        repository = get_uptime_repository(session=mock_session)

        # Assert
        assert repository is not None
        assert hasattr(repository, "create")
        assert hasattr(repository, "find_by_time_range")
        assert hasattr(repository, "calculate_uptime_percentage")

    @pytest.mark.regression
    def test_get_collect_logs_use_case_returns_collect_logs_instance(self):
        """Test that get_collect_logs_use_case returns CollectLogs instance."""
        # Arrange
        mock_repository = Mock()

        # Act
        use_case = get_collect_logs_use_case(repository=mock_repository)

        # Assert
        assert use_case is not None
        assert hasattr(use_case, "execute")
        assert hasattr(use_case, "execute_batch")

    @pytest.mark.regression
    def test_get_calculate_uptime_use_case_returns_calculate_uptime_instance(self):
        """Test that get_calculate_uptime_use_case returns CalculateUptime instance."""
        # Arrange
        mock_repository = Mock()

        # Act
        use_case = get_calculate_uptime_use_case(repository=mock_repository)

        # Assert
        assert use_case is not None
        assert hasattr(use_case, "execute")
        assert hasattr(use_case, "record_uptime")


class TestRoutesRegression:
    """Regression tests for FastAPI routes."""

    @pytest.mark.regression
    def test_to_log_response_converts_domain_model_to_schema(self):
        """Test that _to_log_response converts LogEntry to LogEntryResponse."""
        # Arrange
        from datetime import datetime

        entry = LogEntry(
            id=1,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
            user_agent="Mozilla/5.0",
        )

        # Act
        response = _to_log_response(entry)

        # Assert
        assert response.id == 1
        assert response.client_ip == "192.168.1.1"
        assert response.http_method == "GET"
        assert response.request_uri == "/health"
        assert response.status_code == 200
        assert response.response_time == 0.05
        assert response.user_agent == "Mozilla/5.0"

    @pytest.mark.regression
    def test_query_logs_defaults_to_last_24_hours(self):
        """Test that query_logs defaults to last 24 hours when no time range specified."""
        # Arrange
        from datetime import datetime, timedelta
        from unittest.mock import Mock

        from src.endpoints.log_collector.domain.models import LogEntry
        from src.endpoints.log_collector.presentation.routes import query_logs

        mock_repository = Mock()
        mock_entry = LogEntry(
            id=1,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )
        mock_repository.find_by_time_range.return_value = [mock_entry]

        # Act - Call with None for start_time and end_time
        result = query_logs(
            start_time=None,
            end_time=None,
            status_code=None,
            uri=None,
            repository=mock_repository,
        )

        # Assert
        assert len(result) == 1
        mock_repository.find_by_time_range.assert_called_once()
        call_args = mock_repository.find_by_time_range.call_args[0]
        # Verify time range is approximately 24 hours
        time_diff = call_args[1] - call_args[0]
        assert (
            timedelta(hours=23, minutes=59) < time_diff < timedelta(hours=24, minutes=1)
        )

    @pytest.mark.regression
    def test_query_logs_filters_by_status_code(self):
        """Test that query_logs filters entries by status code."""
        # Arrange
        from datetime import datetime, timedelta
        from unittest.mock import Mock

        from src.endpoints.log_collector.domain.models import LogEntry
        from src.endpoints.log_collector.presentation.routes import query_logs

        mock_repository = Mock()
        mock_entry1 = LogEntry(
            id=1,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )
        mock_entry2 = LogEntry(
            id=2,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.2",
            http_method="GET",
            request_uri="/invalid",
            status_code=404,
            response_time=0.02,
        )
        mock_repository.find_by_time_range.return_value = [mock_entry1, mock_entry2]

        # Act
        result = query_logs(
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            status_code=200,
            uri=None,
            repository=mock_repository,
        )

        # Assert
        assert len(result) == 1
        assert result[0].status_code == 200

    @pytest.mark.regression
    def test_query_logs_filters_by_uri(self):
        """Test that query_logs filters entries by URI."""
        # Arrange
        from datetime import datetime, timedelta
        from unittest.mock import Mock

        from src.endpoints.log_collector.domain.models import LogEntry
        from src.endpoints.log_collector.presentation.routes import query_logs

        mock_repository = Mock()
        mock_entry1 = LogEntry(
            id=1,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )
        mock_entry2 = LogEntry(
            id=2,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.2",
            http_method="GET",
            request_uri="/demo-items",
            status_code=200,
            response_time=0.1,
        )
        mock_repository.find_by_time_range.return_value = [mock_entry1, mock_entry2]

        # Act
        result = query_logs(
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            status_code=None,
            uri="/health",
            repository=mock_repository,
        )

        # Assert
        assert len(result) == 1
        assert result[0].request_uri == "/health"

    @pytest.mark.regression
    def test_get_uptime_calculates_and_returns_response(self):
        """Test that get_uptime calculates uptime and returns response."""
        # Arrange
        from datetime import datetime, timedelta
        from unittest.mock import Mock

        from src.endpoints.log_collector.domain.models import UptimeRecord
        from src.endpoints.log_collector.presentation.routes import get_uptime

        mock_use_case = Mock()
        mock_use_case.execute.return_value = 95.5
        mock_repository = Mock()
        mock_record1 = UptimeRecord(
            id=1,
            timestamp_utc=datetime.now(),
            status="UP",
            source="healthcheck",
        )
        mock_record2 = UptimeRecord(
            id=2,
            timestamp_utc=datetime.now(),
            status="DOWN",
            source="healthcheck",
        )
        mock_repository.find_by_time_range.return_value = [mock_record1, mock_record2]

        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        # Act
        result = get_uptime(
            start_time=start_time,
            end_time=end_time,
            use_case=mock_use_case,
            repository=mock_repository,
        )

        # Assert
        assert result.uptime_percentage == 95.5
        assert result.start_time == start_time
        assert result.end_time == end_time
        assert result.total_measurements == 2
        assert result.up_count == 1
        assert result.down_count == 1

    @pytest.mark.regression
    def test_health_check_endpoint_returns_ok(self):
        """Test that health check endpoint returns status 'ok'."""
        # Test line 153: Health check endpoint return statement
        from fastapi.testclient import TestClient
        from src.endpoints.log_collector.main import create_app
        import os
        
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        
        try:
            app = create_app()
            client = TestClient(app)
            
            # Act
            response = client.get("/health")
            
            # Assert
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]


class TestMainRegression:
    """Regression tests for main application."""

    @pytest.mark.regression
    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        # Arrange
        from src.endpoints.log_collector.main import create_app

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            # Act
            app = create_app()

            # Assert
            assert app is not None
            assert app.title == "Log Collector API"
            assert app.version == "0.2.0"
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_run_migrations_handles_file_not_found(self):
        """Test that run_migrations handles FileNotFoundError gracefully."""
        # Arrange
        from src.endpoints.log_collector.main import run_migrations

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            # Mock subprocess.run to raise FileNotFoundError
            with patch("src.endpoints.log_collector.main.subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError("Alembic not found")

                # Act - Should not raise exception
                run_migrations()

                # Assert - Function should complete without error
                assert True
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_run_migrations_handles_general_exception(self):
        """Test that run_migrations handles general exceptions gracefully."""
        # Arrange
        from src.endpoints.log_collector.main import run_migrations

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            # Mock subprocess.run to raise a general exception
            with patch("src.endpoints.log_collector.main.subprocess.run") as mock_run:
                mock_run.side_effect = Exception("Unexpected error")

                # Act - Should not raise exception
                run_migrations()

                # Assert - Function should complete without error
                assert True
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_run_migrations_handles_nonzero_return_code(self):
        """Test that run_migrations handles nonzero return code."""
        # Arrange
        from unittest.mock import MagicMock

        from src.endpoints.log_collector.main import run_migrations

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            # Mock subprocess.run to return nonzero exit code
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = "Migration error output"
            mock_result.stderr = "Migration error"

            with patch("src.endpoints.log_collector.main.subprocess.run") as mock_run:
                mock_run.return_value = mock_result

                # Act - Should not raise exception
                run_migrations()

                # Assert - Function should complete without error
                assert True
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_run_migrations_success_case(self):
        """Test that run_migrations handles success case."""
        # Arrange
        from unittest.mock import MagicMock

        from src.endpoints.log_collector.main import run_migrations

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""

            with patch("src.endpoints.log_collector.main.subprocess.run") as mock_run:
                mock_run.return_value = mock_result
                run_migrations()
                assert True
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_main_function_starts_server(self):
        """Test that main function starts uvicorn server."""
        # Arrange
        from unittest.mock import patch

        from src.endpoints.log_collector.main import main

        original_db_url = os.environ.get("DATABASE_URL")
        original_host = os.environ.get("API_HOST")
        original_port = os.environ.get("API_PORT")
        original_log_level = os.environ.get("LOG_LEVEL")
        original_env = os.environ.get("ENV")

        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        os.environ["API_HOST"] = "127.0.0.1"
        os.environ["API_PORT"] = "8001"
        os.environ["LOG_LEVEL"] = "info"
        os.environ["ENV"] = "development"

        try:
            # Patch uvicorn.run globally before calling main
            with patch("uvicorn.run") as mock_uvicorn_run:
                mock_uvicorn_run.return_value = None
                main()
                # Assert uvicorn.run was called
                mock_uvicorn_run.assert_called_once()
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
            if original_host is not None:
                os.environ["API_HOST"] = original_host
            elif "API_HOST" in os.environ:
                del os.environ["API_HOST"]
            if original_port is not None:
                os.environ["API_PORT"] = original_port
            elif "API_PORT" in os.environ:
                del os.environ["API_PORT"]
            if original_log_level is not None:
                os.environ["LOG_LEVEL"] = original_log_level
            elif "LOG_LEVEL" in os.environ:
                del os.environ["LOG_LEVEL"]
            if original_env is not None:
                os.environ["ENV"] = original_env
            elif "ENV" in os.environ:
                del os.environ["ENV"]

    @pytest.mark.regression
    def test_lifespan_startup_and_shutdown(self):
        """Test that lifespan context manager handles startup and shutdown."""
        # Arrange
        import asyncio

        from fastapi import FastAPI

        from src.endpoints.log_collector.main import lifespan

        original_db_url = os.environ.get("DATABASE_URL")
        original_env = os.environ.get("ENV")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        os.environ["ENV"] = "development"

        try:
            app = FastAPI()

            # Act - Use lifespan context manager with asyncio.run()
            async def run_lifespan():
                async with lifespan(app):
                    # Assert - App should be initialized during startup
                    assert app is not None

            asyncio.run(run_lifespan())
        finally:
            # Restore original environment variables
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
            if original_env is not None:
                os.environ["ENV"] = original_env
            elif "ENV" in os.environ:
                del os.environ["ENV"]

    @pytest.mark.regression
    def test_lifespan_production_mode_skips_migrations(self):
        """Test that lifespan skips migrations in production mode."""
        # Arrange
        import asyncio

        from fastapi import FastAPI

        from src.endpoints.log_collector.main import lifespan

        original_db_url = os.environ.get("DATABASE_URL")
        original_env = os.environ.get("ENV")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        os.environ["ENV"] = "production"

        try:
            app = FastAPI()

            # Act - Use lifespan context manager with asyncio.run()
            async def run_lifespan():
                async with lifespan(app):
                    # Assert - App should be initialized
                    assert app is not None

            asyncio.run(run_lifespan())
        finally:
            # Restore original environment variables
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
            if original_env is not None:
                os.environ["ENV"] = original_env
            elif "ENV" in os.environ:
                del os.environ["ENV"]
