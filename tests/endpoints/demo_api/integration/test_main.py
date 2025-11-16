"""
Integration tests for main.py.

Tests application initialization, lifespan, and migration handling.
"""

import os
from unittest.mock import MagicMock, patch

from src.endpoints.demo_api.main import create_app, lifespan, main, run_migrations


class TestRunMigrations:
    """Test suite for run_migrations function."""

    def test_run_migrations_success_logs_info(self):
        """Test that successful migration logs info message."""
        # Arrange
        with patch("subprocess.run") as mock_run, patch("os.chdir"), patch(
            "src.endpoints.demo_api.main.logger"
        ) as mock_logger:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            # Act
            run_migrations()

            # Assert
            mock_logger.info.assert_called_with(
                "Database migrations completed successfully"
            )

    def test_run_migrations_failure_logs_warning(self):
        """Test that failed migration logs warning."""
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
            mock_logger.warning.assert_called()

    def test_run_migrations_file_not_found_logs_warning(self):
        """Test that FileNotFoundError logs warning."""
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
            )

    def test_run_migrations_exception_logs_error(self):
        """Test that unexpected exception logs error."""
        # Arrange
        with patch("subprocess.run") as mock_run, patch("os.chdir"), patch(
            "src.endpoints.demo_api.main.logger"
        ) as mock_logger:
            mock_run.side_effect = Exception("Unexpected error")

            # Act
            run_migrations()

            # Assert
            mock_logger.error.assert_called()


class TestLifespan:
    """Test suite for lifespan function."""

    def test_lifespan_initializes_database(self):
        """Test that lifespan initializes database on startup."""
        # Arrange
        import asyncio

        app = MagicMock()
        with patch("src.endpoints.demo_api.main.init_database") as mock_init, patch(
            "src.endpoints.demo_api.main.logger"
        ), patch.dict(os.environ, {"ENV": "development"}):
            mock_run_migrations = MagicMock()
            with patch(
                "src.endpoints.demo_api.main.run_migrations", mock_run_migrations
            ):
                # Act
                async def run_lifespan():
                    async with lifespan(app):
                        pass

                asyncio.run(run_lifespan())

                # Assert
                mock_init.assert_called()

    def test_lifespan_runs_migrations_in_development(self):
        """Test that lifespan runs migrations in development mode."""
        # Arrange
        import asyncio

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
            mock_run.assert_called()

    def test_lifespan_skips_migrations_in_production(self):
        """Test that lifespan skips migrations in production mode."""
        # Arrange
        import asyncio

        app = MagicMock()
        with patch("src.endpoints.demo_api.main.init_database"), patch(
            "src.endpoints.demo_api.main.logger"
        ), patch("src.endpoints.demo_api.main.run_migrations") as mock_run, patch.dict(
            os.environ, {"ENV": "production"}
        ):
            # Act
            async def run_lifespan():
                async with lifespan(app):
                    pass

            asyncio.run(run_lifespan())

            # Assert
            mock_run.assert_not_called()

    def test_lifespan_logs_shutdown(self):
        """Test that lifespan logs shutdown message."""
        # Arrange
        import asyncio

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
            assert len(shutdown_calls) > 0


class TestCreateApp:
    """Test suite for create_app function."""

    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        # Arrange & Act
        app = create_app()

        # Assert
        assert app is not None
        assert hasattr(app, "title")
        assert app.title == "Demo API"

    def test_create_app_registers_routers(self):
        """Test that create_app registers health and demo-items routers."""
        # Arrange
        app = create_app()

        # Assert
        routes = [route.path for route in app.routes]
        assert "/health" in routes
        assert "/demo-items" in routes


class TestMain:
    """Test suite for main function."""

    def test_main_calls_uvicorn_run(self):
        """Test that main function calls uvicorn.run with correct parameters."""
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
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["host"] == "127.0.0.1"
            assert call_kwargs["port"] == 9000
            assert call_kwargs["log_level"] == "debug"
            assert call_kwargs["reload"] is False

    def test_main_uses_default_values(self):
        """Test that main uses default values when env vars not set."""
        # Arrange
        with patch("uvicorn.run") as mock_run, patch(
            "src.endpoints.demo_api.main.logger"
        ), patch.dict(os.environ, {}, clear=True):
            # Act
            main()

            # Assert
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["host"] == "0.0.0.0"
            assert call_kwargs["port"] == 8000
            assert call_kwargs["log_level"] == "info"
            assert call_kwargs["reload"] is True  # development mode default
