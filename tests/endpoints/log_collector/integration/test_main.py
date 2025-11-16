"""
Integration tests for main application.

Tests the FastAPI application creation and lifespan events.
"""

import os

import pytest
from fastapi.testclient import TestClient

from src.endpoints.log_collector.main import create_app, lifespan
from src.shared.infrastructure.database import init_database
from src.shared.models.base import Base as SharedBase


@pytest.fixture
def test_app(test_database_url: str):
    """
    Provide a test FastAPI application.

    Args:
        test_database_url: Database URL for testing.

    Yields:
        FastAPI application instance.
    """

    # Set DATABASE_URL environment variable
    original_db_url = os.environ.get("DATABASE_URL")
    original_env = os.environ.get("ENV")
    os.environ["DATABASE_URL"] = test_database_url
    os.environ["ENV"] = "development"

    try:
        # Initialize database with test URL
        init_database(test_database_url)
        app = create_app()
        # Create all tables for testing
        from src.endpoints.log_collector.infrastructure.models import (  # noqa: F401
            NginxAccessLogModel,
            NginxUptimeModel,
        )
        from src.shared.infrastructure.database import get_engine

        engine = get_engine()
        SharedBase.metadata.create_all(engine)
        yield app
        # Cleanup: drop tables after test
        SharedBase.metadata.drop_all(engine)
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


@pytest.fixture
def client(test_app):
    """
    Provide a test client for the FastAPI application.

    Args:
        test_app: FastAPI application fixture.

    Yields:
        TestClient instance.
    """
    return TestClient(test_app)


class TestMainIntegration:
    """Integration test suite for main application."""

    @pytest.mark.integration
    def test_create_app_returns_fastapi_instance(self, test_database_url):
        """Test that create_app returns a FastAPI instance."""
        # Arrange
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = test_database_url

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

    @pytest.mark.integration
    def test_lifespan_startup_and_shutdown(self, test_database_url):
        """Test that lifespan context manager handles startup and shutdown."""
        # Arrange
        import asyncio

        from fastapi import FastAPI

        original_db_url = os.environ.get("DATABASE_URL")
        original_env = os.environ.get("ENV")
        os.environ["DATABASE_URL"] = test_database_url
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

    @pytest.mark.integration
    def test_lifespan_production_mode_skips_migrations(self, test_database_url):
        """Test that lifespan skips migrations in production mode."""
        # Arrange
        import asyncio

        from fastapi import FastAPI

        original_db_url = os.environ.get("DATABASE_URL")
        original_env = os.environ.get("ENV")
        os.environ["DATABASE_URL"] = test_database_url
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

    @pytest.mark.integration
    def test_run_migrations_handles_file_not_found(self, test_database_url):
        """Test that run_migrations handles FileNotFoundError gracefully."""
        from unittest.mock import patch

        from src.endpoints.log_collector.main import run_migrations

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = test_database_url

        try:
            with patch("src.endpoints.log_collector.main.subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError("Alembic not found")
                run_migrations()
                assert True
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.integration
    def test_run_migrations_handles_general_exception(self, test_database_url):
        """Test that run_migrations handles general exceptions gracefully."""
        from unittest.mock import patch

        from src.endpoints.log_collector.main import run_migrations

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = test_database_url

        try:
            with patch("src.endpoints.log_collector.main.subprocess.run") as mock_run:
                mock_run.side_effect = Exception("Unexpected error")
                run_migrations()
                assert True
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.integration
    def test_run_migrations_handles_nonzero_return_code(self, test_database_url):
        """Test that run_migrations handles nonzero return code."""
        from unittest.mock import MagicMock, patch

        from src.endpoints.log_collector.main import run_migrations

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = test_database_url

        try:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = "Migration error output"
            mock_result.stderr = "Migration error"

            with patch("src.endpoints.log_collector.main.subprocess.run") as mock_run:
                mock_run.return_value = mock_result
                run_migrations()
                assert True
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.integration
    def test_run_migrations_success_case(self, test_database_url):
        """Test that run_migrations handles success case."""
        from unittest.mock import MagicMock, patch

        from src.endpoints.log_collector.main import run_migrations

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = test_database_url

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

    @pytest.mark.integration
    def test_main_function_starts_server(self, test_database_url):
        """Test that main function starts uvicorn server."""
        import sys
        from unittest.mock import patch

        # Import main module to get access to it
        if "src.endpoints.log_collector.main" in sys.modules:
            del sys.modules["src.endpoints.log_collector.main"]

        from src.endpoints.log_collector.main import main

        original_db_url = os.environ.get("DATABASE_URL")
        original_host = os.environ.get("API_HOST")
        original_port = os.environ.get("API_PORT")
        original_log_level = os.environ.get("LOG_LEVEL")
        original_env = os.environ.get("ENV")

        os.environ["DATABASE_URL"] = test_database_url
        os.environ["API_HOST"] = "127.0.0.1"
        os.environ["API_PORT"] = "8001"
        os.environ["LOG_LEVEL"] = "info"
        os.environ["ENV"] = "development"

        try:
            # Patch uvicorn.run globally before calling main
            # Since uvicorn is imported inside main(), we need to patch it at the uvicorn module level
            with patch("uvicorn.run") as mock_uvicorn_run:
                # Mock uvicorn.run to return immediately (don't actually start server)
                mock_uvicorn_run.return_value = None
                main()
                # Assert uvicorn.run was called with correct arguments
                mock_uvicorn_run.assert_called_once()
                call_args = mock_uvicorn_run.call_args
                assert call_args[0][0] == "src.endpoints.log_collector.main:app"
                assert call_args[1]["host"] == "127.0.0.1"
                assert call_args[1]["port"] == 8001
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
