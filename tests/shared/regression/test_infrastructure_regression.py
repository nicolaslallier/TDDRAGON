"""
Regression tests for shared infrastructure.

Ensures that database and logger infrastructure continue to work correctly.
"""

import contextlib
import os
from unittest.mock import patch

import pytest

from src.shared.infrastructure import database
from src.shared.infrastructure.database import (
    get_database_url,
    get_engine,
    get_session,
    init_database,
)
from src.shared.infrastructure.logger import get_logger


class TestDatabaseRegression:
    """Regression tests for database infrastructure."""

    def setup_method(self):
        """Reset global state before each test."""
        database._engine = None
        database._session_factory = None
        database._initialized_url = None

    @pytest.mark.regression
    def test_get_database_url_from_env(self):
        """Test that get_database_url returns DATABASE_URL when set."""
        # Arrange
        expected_url = "postgresql://user:pass@localhost:5432/testdb"
        with patch.dict(os.environ, {"DATABASE_URL": expected_url}):
            # Act
            result = get_database_url()

            # Assert
            assert result == expected_url  # Line 43-46

    @pytest.mark.regression
    def test_get_database_url_fallback_construction(self):
        """Test that get_database_url constructs URL from components."""
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act
            result = get_database_url()

            # Assert
            assert result.startswith("postgresql://")  # Lines 48-55
            assert "postgres:postgres@localhost:5432/tddragon" in result

    @pytest.mark.regression
    def test_init_database_with_url(self):
        """Test that init_database initializes engine and session factory."""
        # Arrange
        test_url = "sqlite:///:memory:"

        # Act
        init_database(test_url)

        # Assert
        assert database._engine is not None  # Lines 98-107
        assert database._session_factory is not None

    @pytest.mark.regression
    def test_init_database_with_none_calls_get_database_url(self):
        """Test that init_database(None) calls get_database_url."""
        # Arrange
        with patch(
            "src.shared.infrastructure.database.get_database_url"
        ) as mock_get_url:
            mock_get_url.return_value = "sqlite:///:memory:"

            # Act
            init_database(None)

            # Assert
            mock_get_url.assert_called_once()  # Line 76

    @pytest.mark.regression
    def test_init_database_skips_reinitialization(self):
        """Test that init_database skips reinitialization with same URL."""
        # Arrange
        test_url = "sqlite:///:memory:"
        init_database(test_url)
        original_engine = database._engine

        # Act
        init_database(test_url)

        # Assert
        assert database._engine is original_engine  # Line 80

    @pytest.mark.regression
    def test_init_database_postgresql_uses_pool_parameters(self):
        """Test that PostgreSQL URLs get pool parameters."""
        # Arrange
        test_url = "postgresql://user:pass@localhost/db"
        with patch("src.shared.infrastructure.database.create_engine") as mock_create:
            # Act
            init_database(test_url)

            # Assert
            call_kwargs = mock_create.call_args[1]
            assert "pool_size" in call_kwargs  # Line 93

    @pytest.mark.regression
    def test_get_session_creates_and_closes(self):
        """Test that get_session creates session and closes it."""
        # Arrange
        init_database("sqlite:///:memory:")

        # Act
        session_gen = get_session()
        session = next(session_gen)

        # Assert
        assert session is not None  # Lines 134-138
        with contextlib.suppress(StopIteration):
            next(session_gen)

    @pytest.mark.regression
    def test_get_session_before_init_raises_error(self):
        """Test that get_session raises RuntimeError if not initialized."""
        # Act & Assert
        with pytest.raises(RuntimeError, match="Database not initialized"):
            next(get_session())  # Line 132

    @pytest.mark.regression
    def test_get_engine_returns_engine(self):
        """Test that get_engine returns engine after initialization."""
        # Arrange
        init_database("sqlite:///:memory:")

        # Act
        engine = get_engine()

        # Assert
        assert engine is not None
        assert engine is database._engine  # Line 157

    @pytest.mark.regression
    def test_get_engine_before_init_raises_error(self):
        """Test that get_engine raises RuntimeError if not initialized."""
        # Act & Assert
        with pytest.raises(RuntimeError, match="Database not initialized"):
            get_engine()  # Line 155


class TestLoggerRegression:
    """Regression tests for logger infrastructure."""

    @pytest.mark.regression
    def test_get_logger_returns_existing_logger_with_handlers(self):
        """Test that get_logger returns existing logger if handlers exist."""
        # Arrange
        logger_name = "test_logger_regression"
        logger1 = get_logger(logger_name)

        # Act - Get logger again (should return early)
        logger2 = get_logger(logger_name)

        # Assert
        assert logger1 is logger2
        assert len(logger1.handlers) > 0
        # Verify no duplicate handlers (line 41)
        handler_count = len(logger1.handlers)
        logger3 = get_logger(logger_name)
        assert len(logger3.handlers) == handler_count
