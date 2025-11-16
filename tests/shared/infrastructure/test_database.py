"""
Unit tests for database infrastructure.

Tests for database connection management and session handling.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.shared.infrastructure import database
from src.shared.infrastructure.database import (
    get_database_url,
    get_engine,
    get_session,
    init_database,
)


class TestGetDatabaseURL:
    """Test suite for get_database_url function."""

    def test_get_database_url_from_env_returns_env_value(self):
        """Test that get_database_url returns DATABASE_URL from environment."""
        # Arrange
        expected_url = "postgresql://user:pass@localhost:5432/testdb"
        with patch.dict(os.environ, {"DATABASE_URL": expected_url}):
            # Act
            result = get_database_url()

            # Assert
            assert result == expected_url

    def test_get_database_url_without_env_constructs_from_components(self):
        """Test that get_database_url constructs URL from individual components."""
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act
            result = get_database_url()

            # Assert
            assert result.startswith("postgresql://")
            assert "postgres:postgres@localhost:5432/tddragon" in result

    def test_get_database_url_with_custom_components(self):
        """Test that get_database_url uses custom environment variables."""
        # Arrange
        env_vars = {
            "POSTGRES_USER": "custom_user",
            "POSTGRES_PASSWORD": "custom_pass",
            "POSTGRES_HOST": "custom_host",
            "POSTGRES_PORT": "9999",
            "POSTGRES_DB": "custom_db",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            # Act
            result = get_database_url()

            # Assert
            assert (
                result
                == "postgresql://custom_user:custom_pass@custom_host:9999/custom_db"
            )


class TestInitDatabase:
    """Test suite for init_database function."""

    def setup_method(self):
        """Reset global state before each test."""
        database._engine = None
        database._session_factory = None
        database._initialized_url = None

    def test_init_database_with_url_initializes_engine(self):
        """Test that init_database creates engine and session factory."""
        # Arrange
        test_url = "sqlite:///:memory:"

        # Act
        init_database(test_url)

        # Assert
        assert database._engine is not None
        assert database._session_factory is not None
        assert database._initialized_url == test_url

    def test_init_database_with_none_uses_get_database_url(self):
        """Test that init_database calls get_database_url when url is None."""
        # Arrange
        with patch(
            "src.shared.infrastructure.database.get_database_url"
        ) as mock_get_url:
            mock_get_url.return_value = "sqlite:///:memory:"

            # Act
            init_database(None)

            # Assert
            mock_get_url.assert_called_once()
            assert database._engine is not None

    def test_init_database_skips_reinitialization_with_same_url(self):
        """Test that init_database skips reinitialization with same URL."""
        # Arrange
        test_url = "sqlite:///:memory:"
        init_database(test_url)
        original_engine = database._engine

        # Act
        init_database(test_url)

        # Assert
        assert database._engine is original_engine  # Same engine instance

    def test_init_database_postgresql_uses_pool_parameters(self):
        """Test that PostgreSQL URLs get pool_size and max_overflow parameters."""
        # Arrange
        test_url = "postgresql://user:pass@localhost/db"
        with patch("src.shared.infrastructure.database.create_engine") as mock_create:
            # Act
            init_database(test_url)

            # Assert
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert "pool_size" in call_kwargs
            assert "max_overflow" in call_kwargs

    def test_init_database_sqlite_does_not_use_pool_parameters(self):
        """Test that SQLite URLs don't get pool_size and max_overflow parameters."""
        # Arrange
        test_url = "sqlite:///:memory:"
        with patch("src.shared.infrastructure.database.create_engine") as mock_create:
            # Act
            init_database(test_url)

            # Assert
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert "pool_size" not in call_kwargs
            assert "max_overflow" not in call_kwargs


class TestGetSession:
    """Test suite for get_session function."""

    def setup_method(self):
        """Reset global state before each test."""
        database._engine = None
        database._session_factory = None
        database._initialized_url = None

    def test_get_session_before_init_raises_runtime_error(self):
        """Test that get_session raises RuntimeError if database not initialized."""
        # Act & Assert
        with pytest.raises(RuntimeError, match="Database not initialized"):
            next(get_session())

    def test_get_session_after_init_returns_session(self):
        """Test that get_session returns a session after initialization."""
        # Arrange
        init_database("sqlite:///:memory:")

        # Act
        session = next(get_session())

        # Assert
        assert session is not None
        session.close()  # Cleanup

    def test_get_session_closes_session_after_use(self):
        """Test that get_session closes session after use."""
        # Arrange
        init_database("sqlite:///:memory:")
        mock_session = MagicMock()
        original_session_factory = database._session_factory
        database._session_factory = MagicMock(return_value=mock_session)

        try:
            # Act
            list(get_session())  # Consume generator

            # Assert
            mock_session.close.assert_called_once()
        finally:
            database._session_factory = original_session_factory


class TestGetEngine:
    """Test suite for get_engine function."""

    def setup_method(self):
        """Reset global state before each test."""
        database._engine = None
        database._session_factory = None
        database._initialized_url = None

    def test_get_engine_before_init_raises_runtime_error(self):
        """Test that get_engine raises RuntimeError if database not initialized."""
        # Act & Assert
        with pytest.raises(RuntimeError, match="Database not initialized"):
            get_engine()

    def test_get_engine_after_init_returns_engine(self):
        """Test that get_engine returns engine after initialization."""
        # Arrange
        init_database("sqlite:///:memory:")

        # Act
        engine = get_engine()

        # Assert
        assert engine is not None
        assert engine is database._engine
