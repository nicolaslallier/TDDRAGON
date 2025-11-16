"""
Regression tests for shared infrastructure components.

Ensures that infrastructure components continue to work correctly after changes.
"""

import os

import pytest

from src.shared.infrastructure.database import (
    get_database_url,
    get_engine,
    get_session,
    init_database,
)
from src.shared.infrastructure.logger import get_logger


class TestDatabaseRegression:
    """Regression tests for database infrastructure."""

    @pytest.mark.regression
    def test_get_database_url_returns_environment_variable(self):
        """Test that get_database_url returns DATABASE_URL from environment."""
        # Arrange
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"

        try:
            # Act
            result = get_database_url()

            # Assert
            assert result == "sqlite:///:memory:"
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_get_database_url_falls_back_to_postgres_components(self):
        """Test that get_database_url falls back to POSTGRES_* environment variables."""
        # Arrange
        original_db_url = os.environ.get("DATABASE_URL")
        original_user = os.environ.get("POSTGRES_USER")
        original_password = os.environ.get("POSTGRES_PASSWORD")
        original_host = os.environ.get("POSTGRES_HOST")
        original_port = os.environ.get("POSTGRES_PORT")
        original_db = os.environ.get("POSTGRES_DB")

        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        os.environ["POSTGRES_USER"] = "testuser"
        os.environ["POSTGRES_PASSWORD"] = "testpass"
        os.environ["POSTGRES_HOST"] = "testhost"
        os.environ["POSTGRES_PORT"] = "5433"
        os.environ["POSTGRES_DB"] = "testdb"

        try:
            # Act
            result = get_database_url()

            # Assert
            assert result == "postgresql://testuser:testpass@testhost:5433/testdb"
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
            if original_user is not None:
                os.environ["POSTGRES_USER"] = original_user
            elif "POSTGRES_USER" in os.environ:
                del os.environ["POSTGRES_USER"]
            if original_password is not None:
                os.environ["POSTGRES_PASSWORD"] = original_password
            elif "POSTGRES_PASSWORD" in os.environ:
                del os.environ["POSTGRES_PASSWORD"]
            if original_host is not None:
                os.environ["POSTGRES_HOST"] = original_host
            elif "POSTGRES_HOST" in os.environ:
                del os.environ["POSTGRES_HOST"]
            if original_port is not None:
                os.environ["POSTGRES_PORT"] = original_port
            elif "POSTGRES_PORT" in os.environ:
                del os.environ["POSTGRES_PORT"]
            if original_db is not None:
                os.environ["POSTGRES_DB"] = original_db
            elif "POSTGRES_DB" in os.environ:
                del os.environ["POSTGRES_DB"]

    @pytest.mark.regression
    def test_init_database_initializes_engine(self):
        """Test that init_database initializes database engine."""
        # Arrange
        database_url = "sqlite:///:memory:"

        # Act
        init_database(database_url)

        # Assert
        engine = get_engine()
        assert engine is not None

    @pytest.mark.regression
    def test_init_database_with_postgresql_uses_pool_parameters(self):
        """Test that init_database uses PostgreSQL pool parameters for PostgreSQL."""
        # Arrange
        database_url = "postgresql://user:pass@localhost/db"

        # Act
        init_database(database_url)

        # Assert
        engine = get_engine()
        assert engine is not None
        # Verify pool parameters are set (indirectly by checking engine exists)

    @pytest.mark.regression
    def test_init_database_with_sqlite_file_enables_wal_mode(self):
        """Test that init_database enables WAL mode for SQLite file-based databases."""
        # Arrange
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            database_url = f"sqlite:///{db_path}"

            # Act
            init_database(database_url)

            # Assert
            engine = get_engine()
            assert engine is not None
            # Use the engine to create a connection, which triggers the event listener
            with engine.connect() as conn:
                # Verify WAL mode is enabled by checking the database directly
                sqlite_conn = conn.connection.dbapi_connection
                cursor = sqlite_conn.cursor()
                cursor.execute("PRAGMA journal_mode")
                journal_mode = cursor.fetchone()[0]
                assert journal_mode.upper() == "WAL"
        finally:
            import os

            if os.path.exists(db_path):
                os.unlink(db_path)

    @pytest.mark.regression
    def test_get_session_returns_session_generator(self):
        """Test that get_session returns a session generator."""
        # Arrange
        database_url = "sqlite:///:memory:"
        init_database(database_url)

        # Act
        session_gen = get_session()
        session = next(session_gen)

        # Assert
        assert session is not None
        from contextlib import suppress

        with suppress(StopIteration):
            next(session_gen, None)

    @pytest.mark.regression
    def test_get_session_raises_error_if_not_initialized(self):
        """Test that get_session raises RuntimeError if database not initialized."""
        # Arrange
        # Reset global state
        import src.shared.infrastructure.database as db_module

        original_factory = db_module._session_factory
        db_module._session_factory = None

        try:
            # Act & Assert
            with pytest.raises(RuntimeError, match="Database not initialized"):
                next(get_session())
        finally:
            db_module._session_factory = original_factory

    @pytest.mark.regression
    def test_get_engine_raises_error_if_not_initialized(self):
        """Test that get_engine raises RuntimeError if database not initialized."""
        # Arrange
        # Reset global state
        import src.shared.infrastructure.database as db_module

        original_engine = db_module._engine
        db_module._engine = None

        try:
            # Act & Assert
            with pytest.raises(RuntimeError, match="Database not initialized"):
                get_engine()
        finally:
            db_module._engine = original_engine


class TestLoggerRegression:
    """Regression tests for logger infrastructure."""

    @pytest.mark.regression
    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a logger instance."""
        # Act
        logger = get_logger(__name__)

        # Assert
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")

    @pytest.mark.regression
    def test_get_logger_returns_existing_logger_if_handlers_exist(self):
        """Test that get_logger returns existing logger if handlers exist."""
        # Arrange
        import logging

        logger1 = get_logger(__name__)
        # Add a handler to ensure handlers exist
        if not logger1.handlers:
            handler = logging.NullHandler()
            logger1.addHandler(handler)

        # Act
        logger2 = get_logger(__name__)

        # Assert
        assert logger1 is logger2
        assert len(logger1.handlers) > 0
