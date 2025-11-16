"""
Regression tests for log_viewer main module.

Ensures startup, shutdown, and migration logic don't regress.
"""

import os
import subprocess
from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_viewer.main import create_app, lifespan, run_migrations


class TestRunMigrationsRegression:
    """Regression tests for run_migrations function."""

    @pytest.mark.regression
    def test_run_migrations_success_case(self):
        """Test that run_migrations executes successfully."""
        # Test lines 30-95: Full migration execution
        with patch("os.path.exists", return_value=True):
            with patch("os.chdir") as mock_chdir:
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
                    with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                        run_migrations()

                        mock_chdir.assert_called()
                        mock_run.assert_called_once()
                        mock_logger.info.assert_called_with(
                            "Database migrations completed successfully"
                        )

    @pytest.mark.regression
    def test_run_migrations_handles_file_not_found(self):
        """Test that run_migrations handles FileNotFoundError."""
        # Test line 79: except FileNotFoundError
        with patch("os.path.exists", return_value=True):
            with patch("os.chdir"):
                with patch("subprocess.run", side_effect=FileNotFoundError()):
                    with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                        run_migrations()

                        mock_logger.warning.assert_called_with(
                            "Alembic not found, skipping migrations"
                        )

    @pytest.mark.regression
    def test_run_migrations_handles_general_exception(self):
        """Test that run_migrations handles general exceptions."""
        # Test line 81: except Exception
        with patch("os.path.exists", return_value=True):
            with patch("os.chdir"):
                with patch("subprocess.run", side_effect=Exception("Test error")):
                    with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                        run_migrations()

                        mock_logger.error.assert_called()

    @pytest.mark.regression
    def test_run_migrations_handles_missing_log_collector_dir(self):
        """Test that run_migrations handles missing log_collector directory."""
        # Test lines 47-49: Directory not found check
        with patch("os.path.exists", side_effect=lambda path: "log_collector" not in path):
            with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                run_migrations()

                mock_logger.warning.assert_called()
                assert "not found" in mock_logger.warning.call_args[0][0]

    @pytest.mark.regression
    def test_run_migrations_restores_original_directory(self):
        """Test that run_migrations restores original directory."""
        # Test lines 84-88: Directory restoration
        original_dir = os.getcwd()
        with patch("os.path.exists", return_value=True):
            with patch("os.chdir") as mock_chdir:
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
                    run_migrations()

                    # Verify chdir was called to restore
                    assert mock_chdir.call_count >= 2  # At least change and restore

    @pytest.mark.regression
    def test_run_migrations_handles_pythonpath_restoration(self):
        """Test that run_migrations handles PYTHONPATH restoration."""
        # Test lines 90-93: PYTHONPATH restoration
        original_pythonpath = os.environ.get("PYTHONPATH")
        try:
            os.environ["PYTHONPATH"] = "/original/path"
            with patch("os.path.exists", return_value=True):
                with patch("os.chdir"):
                    with patch("subprocess.run") as mock_run:
                        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
                        run_migrations()

                        # Verify PYTHONPATH was restored
                        assert os.environ.get("PYTHONPATH") == "/original/path"
        finally:
            if original_pythonpath is not None:
                os.environ["PYTHONPATH"] = original_pythonpath
            elif "PYTHONPATH" in os.environ:
                del os.environ["PYTHONPATH"]

    @pytest.mark.regression
    def test_run_migrations_deletes_pythonpath_when_did_not_exist(self):
        """Test that run_migrations deletes PYTHONPATH when it didn't exist."""
        # Test line 93: del os.environ["PYTHONPATH"]
        original_pythonpath = os.environ.get("PYTHONPATH")
        try:
            if "PYTHONPATH" in os.environ:
                del os.environ["PYTHONPATH"]

            with patch("os.path.exists", return_value=True):
                with patch("os.chdir"):
                    with patch("subprocess.run") as mock_run:
                        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
                        run_migrations()

                        # Verify PYTHONPATH was deleted if it didn't exist
                        assert "PYTHONPATH" not in os.environ or os.environ.get("PYTHONPATH") == ""
        finally:
            if original_pythonpath is not None:
                os.environ["PYTHONPATH"] = original_pythonpath


class TestLifespanRegression:
    """Regression tests for lifespan function."""

    @pytest.mark.regression
    def test_lifespan_startup_initializes_database(self):
        """Test that lifespan startup initializes database."""
        # Test lines 109-124: Database initialization
        import asyncio

        with patch("src.endpoints.log_viewer.main.init_database") as mock_init:
            with patch("src.endpoints.log_viewer.main.run_migrations") as mock_migrations:
                with patch("os.getenv", return_value="development"):
                    app = Mock()

                    async def run_lifespan():
                        async with lifespan(app):
                            pass  # Context manager handles startup/shutdown

                    asyncio.run(run_lifespan())

                    mock_init.assert_called_once()
                    mock_migrations.assert_called_once()

    @pytest.mark.regression
    def test_lifespan_startup_skips_migrations_in_production(self):
        """Test that lifespan startup skips migrations in production."""
        # Test lines 109-124: Production mode check
        import asyncio

        with patch("src.endpoints.log_viewer.main.init_database"):
            with patch("src.endpoints.log_viewer.main.run_migrations") as mock_migrations:
                with patch("os.getenv", return_value="production"):
                    app = Mock()

                    async def run_lifespan():
                        async with lifespan(app):
                            pass  # Context manager handles startup/shutdown

                    asyncio.run(run_lifespan())

                    mock_migrations.assert_not_called()

    @pytest.mark.regression
    def test_lifespan_shutdown_cleans_up(self):
        """Test that lifespan shutdown cleans up resources."""
        # Test lines 121-124: Shutdown logic
        import asyncio

        with patch("src.endpoints.log_viewer.main.init_database"):
            app = Mock()

            async def run_lifespan():
                async with lifespan(app):
                    pass  # Context manager handles startup/shutdown
                # Shutdown is handled automatically by context manager

            asyncio.run(run_lifespan())


class TestCreateAppRegression:
    """Regression tests for create_app function."""

    @pytest.mark.regression
    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        from fastapi import FastAPI

        app = create_app()
        assert isinstance(app, FastAPI)

    @pytest.mark.regression
    def test_create_app_registers_routes(self):
        """Test that create_app registers routes."""
        app = create_app()
        # Check that routes are registered
        route_paths = [route.path for route in app.routes]
        assert "/log-viewer/login" in route_paths
        assert "/log-viewer/access-logs" in route_paths

