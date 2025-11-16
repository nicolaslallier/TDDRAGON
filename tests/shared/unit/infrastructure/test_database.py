"""
Unit tests for database infrastructure.

Tests for database connection management functions.
"""

import os
from unittest.mock import patch

import pytest

from src.shared.infrastructure.database import (
    get_database_url,
    get_engine,
    get_session,
    init_database,
)


class TestGetDatabaseUrl:
    """Test suite for get_database_url function."""

    @pytest.mark.unit
    def test_get_database_url_from_env_returns_env_value(self):
        """Test that get_database_url returns DATABASE_URL from environment."""
        # Arrange
        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"

        try:
            # Act
            result = get_database_url()

            # Assert
            assert result == "postgresql://user:pass@localhost/db"
        finally:
            del os.environ["DATABASE_URL"]

    @pytest.mark.unit
    def test_get_database_url_fallback_to_components(self):
        """Test that get_database_url constructs URL from components."""
        # Arrange
        if "DATABASE_URL" in os.environ:
            original_url = os.environ.pop("DATABASE_URL")

        try:
            os.environ["POSTGRES_USER"] = "testuser"
            os.environ["POSTGRES_PASSWORD"] = "testpass"
            os.environ["POSTGRES_HOST"] = "testhost"
            os.environ["POSTGRES_PORT"] = "5433"
            os.environ["POSTGRES_DB"] = "testdb"

            # Act
            result = get_database_url()

            # Assert
            assert result == "postgresql://testuser:testpass@testhost:5433/testdb"
        finally:
            for key in [
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
                "POSTGRES_HOST",
                "POSTGRES_PORT",
                "POSTGRES_DB",
            ]:
                os.environ.pop(key, None)
            if "original_url" in locals():
                os.environ["DATABASE_URL"] = original_url

    @pytest.mark.unit
    def test_get_database_url_uses_defaults(self):
        """Test that get_database_url uses default values when components not set."""
        # Arrange
        if "DATABASE_URL" in os.environ:
            original_url = os.environ.pop("DATABASE_URL")

        try:
            # Remove all postgres env vars
            for key in [
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
                "POSTGRES_HOST",
                "POSTGRES_PORT",
                "POSTGRES_DB",
            ]:
                os.environ.pop(key, None)

            # Act
            result = get_database_url()

            # Assert
            assert result == "postgresql://postgres:postgres@localhost:5432/tddragon"
        finally:
            if "original_url" in locals():
                os.environ["DATABASE_URL"] = original_url


class TestInitDatabase:
    """Test suite for init_database function."""

    @pytest.mark.unit
    def test_init_database_with_url_initializes_engine(self):
        """Test that init_database initializes engine with provided URL."""
        # Arrange
        test_url = "sqlite:///:memory:"

        # Act
        init_database(test_url)

        # Assert
        engine = get_engine()
        assert engine is not None

    @pytest.mark.unit
    def test_init_database_idempotent_same_url(self):
        """Test that init_database is idempotent with same URL."""
        # Arrange
        test_url = "sqlite:///:memory:"
        init_database(test_url)
        first_engine = get_engine()

        # Act
        init_database(test_url)
        second_engine = get_engine()

        # Assert
        assert first_engine is second_engine

    @pytest.mark.unit
    def test_init_database_postgresql_uses_pool_parameters(self):
        """Test that init_database uses pool parameters for PostgreSQL."""
        # Arrange
        test_url = "postgresql://user:pass@localhost/db"

        # Act
        with patch(
            "src.shared.infrastructure.database.create_engine"
        ) as mock_create_engine:
            init_database(test_url)

            # Assert
            mock_create_engine.assert_called_once()
            call_kwargs = mock_create_engine.call_args[1]
            assert "pool_size" in call_kwargs
            assert "max_overflow" in call_kwargs

    @pytest.mark.unit
    def test_init_database_with_none_calls_get_database_url(self):
        """Test that init_database with None calls get_database_url."""
        # Arrange
        # Reset database state first
        import src.shared.infrastructure.database as db_module

        original_engine = db_module._engine
        original_factory = db_module._session_factory
        original_url = db_module._initialized_url

        db_module._engine = None
        db_module._session_factory = None
        db_module._initialized_url = None

        try:
            # Act
            with patch(
                "src.shared.infrastructure.database.get_database_url",
                return_value="sqlite:///:memory:",
            ) as mock_get_url:
                with patch("src.shared.infrastructure.database.create_engine"):
                    init_database(None)

                # Assert
                mock_get_url.assert_called_once()
        finally:
            # Restore original state
            db_module._engine = original_engine
            db_module._session_factory = original_factory
            db_module._initialized_url = original_url


class TestGetSession:
    """Test suite for get_session function."""

    @pytest.mark.unit
    def test_get_session_before_init_raises_runtime_error(self):
        """Test that get_session raises RuntimeError if database not initialized."""
        # Arrange
        # Reset database state
        import src.shared.infrastructure.database as db_module

        original_factory = db_module._session_factory
        db_module._session_factory = None

        try:
            # Act & Assert
            with pytest.raises(RuntimeError, match="Database not initialized"):
                next(get_session())
        finally:
            db_module._session_factory = original_factory

    @pytest.mark.unit
    def test_get_session_after_init_returns_session(self):
        """Test that get_session returns session after initialization."""
        # Arrange
        init_database("sqlite:///:memory:")

        # Act
        session_gen = get_session()
        session = next(session_gen)

        try:
            # Assert
            assert session is not None
        finally:
            from contextlib import suppress

            with suppress(Exception):
                session.close()


class TestGetEngine:
    """Test suite for get_engine function."""

    @pytest.mark.unit
    def test_get_engine_before_init_raises_runtime_error(self):
        """Test that get_engine raises RuntimeError if database not initialized."""
        # Arrange
        # Reset database state
        import src.shared.infrastructure.database as db_module

        original_engine = db_module._engine
        db_module._engine = None

        try:
            # Act & Assert
            with pytest.raises(RuntimeError, match="Database not initialized"):
                get_engine()
        finally:
            db_module._engine = original_engine

    @pytest.mark.unit
    def test_get_engine_after_init_returns_engine(self):
        """Test that get_engine returns engine after initialization."""
        # Arrange
        init_database("sqlite:///:memory:")

        # Act
        engine = get_engine()

        # Assert
        assert engine is not None
