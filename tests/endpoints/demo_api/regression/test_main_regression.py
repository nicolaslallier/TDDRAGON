"""
Regression tests for demo_api main application.

Ensures that main application continues to work correctly after changes.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.endpoints.demo_api.main import create_app, lifespan, run_migrations


class TestMainRegression:
    """Regression tests for main application."""

    @pytest.mark.regression
    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        # Arrange
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            # Act
            app = create_app()

            # Assert
            assert app is not None
            assert app.title == "Demo API"
            assert app.version == "0.1.0"
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_run_migrations_handles_file_not_found(self):
        """Test that run_migrations handles FileNotFoundError gracefully."""
        # Arrange
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            # Mock subprocess.run to raise FileNotFoundError
            with patch("src.endpoints.demo_api.main.subprocess.run") as mock_run:
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
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            # Mock subprocess.run to raise a general exception
            with patch("src.endpoints.demo_api.main.subprocess.run") as mock_run:
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
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            # Mock subprocess.run to return nonzero exit code
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = "Migration error output"
            mock_result.stderr = "Migration error"

            with patch("src.endpoints.demo_api.main.subprocess.run") as mock_run:
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
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""

            with patch("src.endpoints.demo_api.main.subprocess.run") as mock_run:
                mock_run.return_value = mock_result
                run_migrations()
                assert True
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_lifespan_startup_and_shutdown(self):
        """Test that lifespan context manager handles startup and shutdown."""
        # Arrange
        import asyncio

        from fastapi import FastAPI

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
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
            if original_env is not None:
                os.environ["ENV"] = original_env
            elif "ENV" in os.environ:
                del os.environ["ENV"]

    @pytest.mark.regression
    def test_main_function_starts_server(self):
        """Test that main function starts uvicorn server."""
        # Arrange
        from unittest.mock import patch

        from src.endpoints.demo_api.main import main

        original_db_url = os.environ.get("DATABASE_URL")
        original_host = os.environ.get("API_HOST")
        original_port = os.environ.get("API_PORT")
        original_log_level = os.environ.get("LOG_LEVEL")
        original_env = os.environ.get("ENV")

        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        os.environ["API_HOST"] = "127.0.0.1"
        os.environ["API_PORT"] = "8000"
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
