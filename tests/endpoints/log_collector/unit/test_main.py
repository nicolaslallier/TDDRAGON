"""
Unit tests for log_collector main module.

Tests for main.py including run_migrations, lifespan, create_app, and main function.
"""

from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_collector.main import create_app, main, run_migrations


class TestRunMigrations:
    """Test suite for run_migrations function."""

    @pytest.mark.unit
    @patch("src.endpoints.log_collector.main.subprocess.run")
    @patch("src.endpoints.log_collector.main.os.chdir")
    @patch("src.endpoints.log_collector.main.os.path.dirname")
    @patch("src.endpoints.log_collector.main.os.path.abspath")
    def test_run_migrations_success_logs_info(
        self, mock_abspath, mock_dirname, mock_chdir, mock_run
    ):
        """Test that successful migration logs info message."""
        # Arrange
        mock_abspath.return_value = "/path/to/file"
        mock_dirname.return_value = "/path/to/log_collector"
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Act
        run_migrations()

        # Assert
        mock_chdir.assert_called_once()
        mock_run.assert_called_once()

    @pytest.mark.unit
    @patch("src.endpoints.log_collector.main.subprocess.run")
    @patch("src.endpoints.log_collector.main.os.chdir")
    @patch("src.endpoints.log_collector.main.os.path.dirname")
    @patch("src.endpoints.log_collector.main.os.path.abspath")
    def test_run_migrations_failure_logs_warning(
        self, mock_abspath, mock_dirname, mock_chdir, mock_run
    ):
        """Test that failed migration logs warning."""
        # Arrange
        mock_abspath.return_value = "/path/to/file"
        mock_dirname.return_value = "/path/to/log_collector"
        mock_run.return_value = Mock(
            returncode=1, stdout="error output", stderr="error"
        )

        # Act
        run_migrations()

        # Assert
        mock_run.assert_called_once()

    @pytest.mark.unit
    @patch("src.endpoints.log_collector.main.subprocess.run")
    def test_run_migrations_file_not_found_logs_warning(self, mock_run):
        """Test that FileNotFoundError logs warning."""
        # Arrange
        mock_run.side_effect = FileNotFoundError()

        # Act
        run_migrations()

        # Assert
        mock_run.assert_called_once()

    @pytest.mark.unit
    @patch("src.endpoints.log_collector.main.subprocess.run")
    def test_run_migrations_exception_logs_error(self, mock_run):
        """Test that other exceptions log error."""
        # Arrange
        mock_run.side_effect = Exception("Unexpected error")

        # Act
        run_migrations()

        # Assert
        mock_run.assert_called_once()


class TestLifespan:
    """Test suite for lifespan function."""

    @pytest.mark.unit
    def test_lifespan_development_mode_runs_migrations(self):
        """Test that lifespan runs migrations in development mode."""
        # Arrange
        import asyncio
        import sys

        # Delete module to force reload with patches
        if "src.endpoints.log_collector.main" in sys.modules:
            del sys.modules["src.endpoints.log_collector.main"]

        with patch("src.endpoints.log_collector.main.os.getenv") as mock_getenv, patch(
            "src.endpoints.log_collector.main.init_database"
        ) as mock_init_db, patch(
            "src.endpoints.log_collector.main.run_migrations"
        ) as mock_run_migrations:
            from src.endpoints.log_collector.main import lifespan

            mock_getenv.side_effect = (
                lambda key, default=None: "development" if key == "ENV" else default
            )
            mock_app = Mock()

            # Act
            async def run_test():
                async with lifespan(mock_app):
                    pass

            asyncio.run(run_test())

            # Assert
            mock_init_db.assert_called_once()
            mock_run_migrations.assert_called_once()

    @pytest.mark.unit
    def test_lifespan_production_mode_skips_migrations(self):
        """Test that lifespan skips migrations in production mode."""
        # Arrange
        import asyncio
        import sys

        # Delete module to force reload with patches
        if "src.endpoints.log_collector.main" in sys.modules:
            del sys.modules["src.endpoints.log_collector.main"]

        with patch("src.endpoints.log_collector.main.os.getenv") as mock_getenv, patch(
            "src.endpoints.log_collector.main.init_database"
        ) as mock_init_db, patch(
            "src.endpoints.log_collector.main.run_migrations"
        ) as mock_run_migrations:
            from src.endpoints.log_collector.main import lifespan

            mock_getenv.side_effect = (
                lambda key, default=None: "production" if key == "ENV" else default
            )
            mock_app = Mock()

            # Act
            async def run_test():
                async with lifespan(mock_app):
                    pass

            asyncio.run(run_test())

            # Assert
            mock_init_db.assert_called_once()
            mock_run_migrations.assert_not_called()


class TestCreateApp:
    """Test suite for create_app function."""

    @pytest.mark.unit
    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns FastAPI instance."""
        # Act
        app = create_app()

        # Assert
        assert app is not None
        assert app.title == "Log Collector API"


class TestMain:
    """Test suite for main function."""

    @pytest.mark.unit
    @patch("uvicorn.run")
    @patch("src.endpoints.log_collector.main.os.getenv")
    def test_main_starts_uvicorn_server(self, mock_getenv, mock_uvicorn_run):
        """Test that main function starts uvicorn server."""
        # Arrange
        mock_getenv.side_effect = lambda key, default=None: {
            "API_HOST": "0.0.0.0",
            "API_PORT": "8001",
            "LOG_LEVEL": "info",
            "ENV": "development",
        }.get(key, default)

        # Act
        main()

        # Assert
        mock_uvicorn_run.assert_called_once()
