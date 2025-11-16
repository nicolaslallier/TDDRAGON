"""
Regression tests for main.py.

Ensures that application startup, lifespan, and main function continue to work correctly.
"""

import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

from src.endpoints.demo_api.main import lifespan, main, run_migrations


class TestMainRegression:
    """Regression tests for main.py."""

    @pytest.mark.regression
    def test_run_migrations_success_path(self):
        """Test run_migrations success scenario."""
        # Arrange
        with patch("subprocess.run") as mock_run, patch("os.chdir"), patch(
            "src.endpoints.demo_api.main.logger"
        ) as mock_logger:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            # Act
            run_migrations()

            # Assert
            mock_run.assert_called_once()  # Line 35
            mock_logger.info.assert_called_with(
                "Database migrations completed successfully"
            )  # Line 43

    @pytest.mark.regression
    def test_run_migrations_failure_path(self):
        """Test run_migrations failure scenario."""
        # Arrange
        with patch("subprocess.run") as mock_run, patch("os.chdir"), patch(
            "src.endpoints.demo_api.main.logger"
        ) as mock_logger:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="Error output", stderr="Error details"
            )

            # Act
            run_migrations()

            # Assert
            mock_logger.warning.assert_called()  # Lines 45-46

    @pytest.mark.regression
    def test_run_migrations_file_not_found_path(self):
        """Test run_migrations FileNotFoundError scenario."""
        # Arrange
        with patch("subprocess.run") as mock_run, patch("os.chdir"), patch(
            "src.endpoints.demo_api.main.logger"
        ) as mock_logger:
            mock_run.side_effect = FileNotFoundError()

            # Act
            run_migrations()

            # Assert
            mock_logger.warning.assert_called_with(
                "Alembic not found, skipping migrations"
            )  # Line 49

    @pytest.mark.regression
    def test_run_migrations_exception_path(self):
        """Test run_migrations exception scenario."""
        # Arrange
        with patch("subprocess.run") as mock_run, patch("os.chdir"), patch(
            "src.endpoints.demo_api.main.logger"
        ) as mock_logger:
            mock_run.side_effect = Exception("Unexpected error")

            # Act
            run_migrations()

            # Assert
            mock_logger.error.assert_called()  # Line 51

    @pytest.mark.regression
    def test_lifespan_startup_initializes_database(self):
        """Test that lifespan startup initializes database."""
        # Arrange
        app = MagicMock()
        with patch("src.endpoints.demo_api.main.init_database") as mock_init, patch(
            "src.endpoints.demo_api.main.logger"
        ), patch("src.endpoints.demo_api.main.run_migrations"), patch.dict(
            os.environ, {"ENV": "development"}
        ):
            # Act
            async def run_lifespan():
                async with lifespan(app):
                    pass

            asyncio.run(run_lifespan())

            # Assert
            mock_init.assert_called()  # Line 68

    @pytest.mark.regression
    def test_lifespan_runs_migrations_in_development(self):
        """Test that lifespan runs migrations in development mode."""
        # Arrange
        app = MagicMock()
        with patch("src.endpoints.demo_api.main.init_database"), patch(
            "src.endpoints.demo_api.main.logger"
        ), patch("src.endpoints.demo_api.main.run_migrations") as mock_run, patch.dict(
            os.environ, {"ENV": "development"}
        ):
            # Act
            async def run_lifespan():
                async with lifespan(app):
                    pass

            asyncio.run(run_lifespan())

            # Assert
            mock_run.assert_called()  # Line 73

    @pytest.mark.regression
    def test_lifespan_logs_shutdown(self):
        """Test that lifespan logs shutdown message."""
        # Arrange
        app = MagicMock()
        with patch("src.endpoints.demo_api.main.init_database"), patch(
            "src.endpoints.demo_api.main.logger"
        ) as mock_logger, patch(
            "src.endpoints.demo_api.main.run_migrations"
        ), patch.dict(
            os.environ, {"ENV": "development"}
        ):
            # Act
            async def run_lifespan():
                async with lifespan(app):
                    pass

            asyncio.run(run_lifespan())

            # Assert
            shutdown_calls = [
                call
                for call in mock_logger.info.call_args_list
                if "Shutting down" in str(call)
            ]
            assert len(shutdown_calls) > 0  # Line 80

    @pytest.mark.regression
    def test_main_function_calls_uvicorn_run(self):
        """Test that main function calls uvicorn.run."""
        # Arrange
        with patch("uvicorn.run") as mock_run, patch(
            "src.endpoints.demo_api.main.logger"
        ), patch.dict(
            os.environ,
            {
                "API_HOST": "127.0.0.1",
                "API_PORT": "9000",
                "LOG_LEVEL": "debug",
                "ENV": "production",
            },
        ):
            # Act
            main()

            # Assert
            mock_run.assert_called_once()  # Line 132
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["host"] == "127.0.0.1"  # Line 126
            assert call_kwargs["port"] == 9000  # Line 127
            assert call_kwargs["log_level"] == "debug"  # Line 128

    @pytest.mark.regression
    def test_main_function_logs_startup(self):
        """Test that main function logs startup message."""
        # Arrange
        with patch("uvicorn.run"), patch(
            "src.endpoints.demo_api.main.logger"
        ) as mock_logger, patch.dict(os.environ, {}, clear=True):
            # Act
            main()

            # Assert
            startup_calls = [
                call
                for call in mock_logger.info.call_args_list
                if "Starting server" in str(call)
            ]
            assert len(startup_calls) > 0  # Line 130
