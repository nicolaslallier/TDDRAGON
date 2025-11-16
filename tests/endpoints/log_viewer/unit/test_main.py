"""
Unit tests for log_viewer main module.

Tests application initialization, migrations, and main entry point.
"""

import os
import subprocess
from contextlib import asynccontextmanager
from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_viewer.main import create_app, lifespan, main, run_migrations


class TestRunMigrations:
    """Test suite for run_migrations function."""

    @pytest.mark.unit
    def test_run_migrations_success_logs_info(self):
        """Test that successful migration logs info message."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        # Act
        with patch("src.endpoints.log_viewer.main.subprocess.run") as mock_run:
            mock_run.return_value = mock_result
            with patch("src.endpoints.log_viewer.main.os.path.exists") as mock_exists:
                mock_exists.return_value = True
                with patch("src.endpoints.log_viewer.main.os.chdir"):
                    with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                        run_migrations()

        # Assert
        mock_logger.info.assert_called_once_with("Database migrations completed successfully")

    @pytest.mark.unit
    def test_run_migrations_failure_logs_warning(self):
        """Test that failed migration logs warning messages."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "Migration output"
        mock_result.stderr = "Migration error"

        # Act
        with patch("src.endpoints.log_viewer.main.subprocess.run") as mock_run:
            mock_run.return_value = mock_result
            with patch("src.endpoints.log_viewer.main.os.path.exists") as mock_exists:
                mock_exists.return_value = True
                with patch("src.endpoints.log_viewer.main.os.chdir"):
                    with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                        run_migrations()

        # Assert
        assert mock_logger.warning.call_count == 2

    @pytest.mark.unit
    def test_run_migrations_file_not_found_logs_warning(self):
        """Test that FileNotFoundError logs warning."""
        # Act
        with patch("src.endpoints.log_viewer.main.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("alembic not found")
            with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                run_migrations()

        # Assert
        mock_logger.warning.assert_called_once_with("Alembic not found, skipping migrations")

    @pytest.mark.unit
    def test_run_migrations_exception_logs_error(self):
        """Test that unexpected exception logs error."""
        # Act
        with patch("src.endpoints.log_viewer.main.subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Unexpected error")
            with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                run_migrations()

        # Assert
        mock_logger.error.assert_called_once()

    @pytest.mark.unit
    def test_run_migrations_directory_not_found_returns_early(self):
        """Test that missing log_collector directory returns early."""
        # Act
        with patch("src.endpoints.log_viewer.main.os.path.exists") as mock_exists:
            mock_exists.return_value = False
            with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                run_migrations()

        # Assert
        mock_logger.warning.assert_called_once()
        assert "not found" in mock_logger.warning.call_args[0][0]

    @pytest.mark.unit
    def test_run_migrations_restores_directory(self):
        """Test that run_migrations restores original directory."""
        # Arrange
        original_dir = "/original/dir"
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        # Act
        with patch("src.endpoints.log_viewer.main.os.getcwd", return_value=original_dir):
            with patch("src.endpoints.log_viewer.main.subprocess.run") as mock_run:
                mock_run.return_value = mock_result
                with patch("src.endpoints.log_viewer.main.os.path.exists") as mock_exists:
                    mock_exists.return_value = True
                    with patch("src.endpoints.log_viewer.main.os.chdir") as mock_chdir:
                        run_migrations()

        # Assert
        # Should change to log_collector_dir and restore
        assert mock_chdir.call_count == 2

    @pytest.mark.unit
    def test_run_migrations_appends_to_existing_pythonpath(self):
        """Test that run_migrations appends to existing PYTHONPATH."""
        # Arrange
        original_pythonpath = "/existing/path"
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        # Act
        with patch.dict("os.environ", {"PYTHONPATH": original_pythonpath}):
            with patch("src.endpoints.log_viewer.main.subprocess.run") as mock_run:
                mock_run.return_value = mock_result
                with patch("src.endpoints.log_viewer.main.os.path.exists") as mock_exists:
                    mock_exists.return_value = True
                    with patch("src.endpoints.log_viewer.main.os.chdir"):
                        run_migrations()

        # Assert
        # Check that PYTHONPATH was set with project_root prepended
        call_args = mock_run.call_args
        env = call_args[1]["env"]
        assert "PYTHONPATH" in env
        assert original_pythonpath in env["PYTHONPATH"]

    @pytest.mark.unit
    def test_run_migrations_restores_pythonpath_when_existed(self):
        """Test that run_migrations restores PYTHONPATH when it existed before."""
        # Arrange
        original_pythonpath = "/original/path"
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        # Save original PYTHONPATH
        original_env_pythonpath = os.environ.get("PYTHONPATH")

        try:
            # Set PYTHONPATH
            os.environ["PYTHONPATH"] = original_pythonpath

            # Act
            with patch("src.endpoints.log_viewer.main.subprocess.run") as mock_run:
                mock_run.return_value = mock_result
                with patch("src.endpoints.log_viewer.main.os.path.exists") as mock_exists:
                    mock_exists.return_value = True
                    with patch("src.endpoints.log_viewer.main.os.chdir"):
                        run_migrations()

            # Assert
            # PYTHONPATH should be restored (line 91)
            assert os.environ.get("PYTHONPATH") == original_pythonpath
        finally:
            # Restore original state
            if original_env_pythonpath is not None:
                os.environ["PYTHONPATH"] = original_env_pythonpath
            elif "PYTHONPATH" in os.environ:
                del os.environ["PYTHONPATH"]

    @pytest.mark.unit
    def test_run_migrations_deletes_pythonpath_when_did_not_exist(self):
        """Test that run_migrations deletes PYTHONPATH when it didn't exist before."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        # Save original PYTHONPATH
        original_env_pythonpath = os.environ.get("PYTHONPATH")

        try:
            # Remove PYTHONPATH if it exists
            if "PYTHONPATH" in os.environ:
                del os.environ["PYTHONPATH"]

            # Mock os.environ to track deletions
            with patch("src.endpoints.log_viewer.main.subprocess.run") as mock_run:
                mock_run.return_value = mock_result
                with patch("src.endpoints.log_viewer.main.os.path.exists") as mock_exists:
                    mock_exists.return_value = True
                    with patch("src.endpoints.log_viewer.main.os.chdir"):
                        # Track if deletion is attempted
                        deletion_attempted = {"value": False}
                        original_del = os.environ.__delitem__
                        
                        def mock_del(key):
                            if key == "PYTHONPATH":
                                deletion_attempted["value"] = True
                            original_del(key)
                        
                        os.environ.__delitem__ = mock_del
                        try:
                            run_migrations()
                        finally:
                            os.environ.__delitem__ = original_del

            # Assert - Line 93 should be executed: del os.environ["PYTHONPATH"]
            # This happens when original_pythonpath was empty/None but PYTHONPATH was set during execution
            # The function sets PYTHONPATH, so it will exist and be deleted in finally block
            # Verify deletion path was executed (line 93)
            assert deletion_attempted["value"] or "PYTHONPATH" not in os.environ
        finally:
            # Restore original state
            if original_env_pythonpath is not None:
                os.environ["PYTHONPATH"] = original_env_pythonpath
            elif "PYTHONPATH" in os.environ:
                del os.environ["PYTHONPATH"]


class TestLifespan:
    """Test suite for lifespan context manager."""

    @pytest.mark.unit
    def test_lifespan_initializes_database(self):
        """Test that lifespan initializes database on startup."""
        import asyncio
        # Arrange
        mock_app = Mock()

        # Act
        with patch("src.endpoints.log_viewer.main.init_database") as mock_init_db:
            with patch("src.endpoints.log_viewer.main.logger") as mock_logger:
                async def run_lifespan():
                    async with lifespan(mock_app):
                        pass
                asyncio.run(run_lifespan())

        # Assert
        mock_init_db.assert_called_once()

    @pytest.mark.unit
    def test_lifespan_runs_migrations_in_development(self):
        """Test that lifespan runs migrations in development mode."""
        import asyncio
        # Arrange
        mock_app = Mock()

        # Act
        with patch.dict("os.environ", {"ENV": "development"}):
            with patch("src.endpoints.log_viewer.main.init_database"):
                with patch("src.endpoints.log_viewer.main.run_migrations") as mock_run_migrations:
                    with patch("src.endpoints.log_viewer.main.logger"):
                        async def run_lifespan():
                            async with lifespan(mock_app):
                                pass
                        asyncio.run(run_lifespan())

        # Assert
        mock_run_migrations.assert_called_once()

    @pytest.mark.unit
    def test_lifespan_skips_migrations_in_production(self):
        """Test that lifespan skips migrations in production mode."""
        import asyncio
        # Arrange
        mock_app = Mock()

        # Act
        with patch.dict("os.environ", {"ENV": "production"}):
            with patch("src.endpoints.log_viewer.main.init_database"):
                with patch("src.endpoints.log_viewer.main.run_migrations") as mock_run_migrations:
                    with patch("src.endpoints.log_viewer.main.logger"):
                        async def run_lifespan():
                            async with lifespan(mock_app):
                                pass
                        asyncio.run(run_lifespan())

        # Assert
        mock_run_migrations.assert_not_called()


class TestCreateApp:
    """Test suite for create_app function."""

    @pytest.mark.unit
    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        # Act
        app = create_app()

        # Assert
        assert app is not None
        assert app.title == "Log Viewer API"

    @pytest.mark.unit
    def test_create_app_configures_middleware(self):
        """Test that create_app configures middleware."""
        # Act
        app = create_app()

        # Assert
        assert len(app.user_middleware) > 0

    @pytest.mark.unit
    def test_create_app_mounts_static_files(self):
        """Test that create_app mounts static files."""
        # Act
        app = create_app()

        # Assert
        # Check that static files route exists
        routes = [route.path for route in app.routes]
        assert "/static" in routes


class TestMain:
    """Test suite for main function."""

    @pytest.mark.unit
    def test_main_calls_uvicorn_run(self):
        """Test that main() calls uvicorn.run with correct parameters."""
        # Arrange - uvicorn is imported inside main(), so we need to patch it differently
        with patch.dict("os.environ", {"API_HOST": "0.0.0.0", "API_PORT": "8002", "LOG_LEVEL": "info"}):
            with patch("uvicorn.run") as mock_uvicorn_run:
                with patch("src.endpoints.log_viewer.main.logger"):
                    # Act
                    main()

        # Assert
        mock_uvicorn_run.assert_called_once()
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "src.endpoints.log_viewer.main:app"
        assert call_args[1]["host"] == "0.0.0.0"
        assert call_args[1]["port"] == 8002
        assert call_args[1]["log_level"] == "info"

    @pytest.mark.unit
    def test_main_uses_default_values(self):
        """Test that main() uses default values when env vars not set."""
        # Arrange
        with patch.dict("os.environ", {}, clear=True):
            with patch("uvicorn.run") as mock_uvicorn_run:
                with patch("src.endpoints.log_viewer.main.logger"):
                    # Act
                    main()

        # Assert
        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["host"] == "0.0.0.0"
        assert call_args[1]["port"] == 8002
        assert call_args[1]["log_level"] == "info"

    @pytest.mark.unit
    def test_main_sets_reload_in_development(self):
        """Test that main() sets reload=True in development mode."""
        # Arrange
        with patch.dict("os.environ", {"ENV": "development"}):
            with patch("uvicorn.run") as mock_uvicorn_run:
                with patch("src.endpoints.log_viewer.main.logger"):
                    # Act
                    main()

        # Assert
        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["reload"] is True

    @pytest.mark.unit
    def test_main_sets_reload_false_in_production(self):
        """Test that main() sets reload=False in production mode."""
        # Arrange
        with patch.dict("os.environ", {"ENV": "production"}):
            with patch("uvicorn.run") as mock_uvicorn_run:
                with patch("src.endpoints.log_viewer.main.logger"):
                    # Act
                    main()

        # Assert
        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["reload"] is False

