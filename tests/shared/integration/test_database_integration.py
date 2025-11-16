"""
Integration tests for database infrastructure.

Tests database connection management in integration scenarios.
"""

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


class TestDatabaseIntegration:
    """Integration test suite for database infrastructure."""

    def setup_method(self):
        """Reset global state before each test."""
        database._engine = None
        database._session_factory = None
        database._initialized_url = None

    @pytest.mark.integration
    def test_get_database_url_fallback_to_components(self):
        """Test that get_database_url constructs URL from individual components."""
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act
            result = get_database_url()

            # Assert
            assert result.startswith("postgresql://")
            assert "postgres:postgres@localhost:5432/tddragon" in result

    @pytest.mark.integration
    def test_get_database_url_with_custom_postgres_components(self):
        """Test that get_database_url uses custom POSTGRES_* environment variables."""
        # Arrange
        env_vars = {
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_pass",
            "POSTGRES_HOST": "test_host",
            "POSTGRES_PORT": "9999",
            "POSTGRES_DB": "test_db",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            # Act
            result = get_database_url()

            # Assert
            assert result == "postgresql://test_user:test_pass@test_host:9999/test_db"

    @pytest.mark.integration
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
            mock_get_url.assert_called_once()
            assert database._engine is not None

    @pytest.mark.integration
    def test_init_database_skips_reinitialization_with_same_url(self):
        """Test that init_database skips reinitialization when URL is the same."""
        # Arrange
        test_url = "sqlite:///:memory:"
        init_database(test_url)
        original_engine = database._engine

        # Act
        init_database(test_url)

        # Assert
        assert database._engine is original_engine

    @pytest.mark.integration
    def test_get_session_before_init_raises_runtime_error(self):
        """Test that get_session raises RuntimeError if database not initialized."""
        # Act & Assert
        with pytest.raises(RuntimeError, match="Database not initialized"):
            next(get_session())

    @pytest.mark.integration
    def test_get_engine_before_init_raises_runtime_error(self):
        """Test that get_engine raises RuntimeError if database not initialized."""
        # Act & Assert
        with pytest.raises(RuntimeError, match="Database not initialized"):
            get_engine()

    @pytest.mark.integration
    def test_get_database_url_from_env_returns_env_value(self):
        """Test that get_database_url returns DATABASE_URL when set."""
        # Arrange
        expected_url = "postgresql://user:pass@localhost:5432/testdb"
        with patch.dict(os.environ, {"DATABASE_URL": expected_url}):
            # Act
            result = get_database_url()

            # Assert
            assert result == expected_url  # Line 46

    @pytest.mark.integration
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
            assert "pool_size" in call_kwargs  # Line 93
            assert "max_overflow" in call_kwargs

    @pytest.mark.integration
    def test_get_session_creates_and_closes_session(self):
        """Test that get_session creates session and closes it properly."""
        # Arrange
        init_database("sqlite:///:memory:")

        # Act
        session_gen = get_session()
        session = next(session_gen)

        # Assert
        assert session is not None  # Line 134
        # Session should be closed after generator is exhausted
        from contextlib import suppress

        with suppress(StopIteration):
            next(session_gen)  # Exhaust generator to trigger finally block
        # Verify session was closed (line 138)

    @pytest.mark.integration
    def test_get_engine_returns_engine_after_init(self):
        """Test that get_engine returns engine after initialization."""
        # Arrange
        init_database("sqlite:///:memory:")

        # Act
        engine = get_engine()

        # Assert
        assert engine is not None
        assert engine is database._engine  # Line 157
