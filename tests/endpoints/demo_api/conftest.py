"""
Pytest fixtures for demo_api endpoint tests.

Provides database fixtures and test utilities for demo_api endpoint tests.
"""

import os
from collections.abc import Generator

import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.endpoints.demo_api.main import create_app
from src.shared.infrastructure.database import get_engine, init_database
from src.shared.models.base import Base as SharedBase


@pytest.fixture(scope="function")
def test_database_url() -> str:
    """
    Provide test database URL.

    Uses file-based SQLite for tests (in-memory doesn't work well with connection pooling),
    or PostgreSQL for integration tests if DATABASE_URL_TEST is set.

    Returns:
        Database connection URL string.
    """
    test_db_url = os.getenv("DATABASE_URL_TEST")
    if test_db_url:
        return test_db_url
    # Use file-based SQLite for tests (in-memory has connection isolation issues)
    # Use a unique file per test to avoid conflicts
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as db_file:
        db_filename = db_file.name
    db_url = f"sqlite:///{db_filename}"
    # Store the filename for cleanup
    pytest.current_db_file = db_filename
    return db_url


@pytest.fixture(scope="function")
def test_engine(test_database_url: str):
    """
    Provide a test database engine.

    Creates a SQLAlchemy engine for testing. Tables are created
    before each test and dropped after.

    Args:
        test_database_url: Database URL for testing.

    Yields:
        SQLAlchemy Engine instance.
    """
    engine = create_engine(test_database_url, echo=False)
    # Create all tables
    SharedBase.metadata.create_all(engine)
    yield engine
    # Drop all tables
    SharedBase.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine) -> Generator[Session, None, None]:
    """
    Provide a test database session.

    Creates a database session for testing. The session is automatically
    rolled back after each test to ensure test isolation.

    Args:
        test_engine: SQLAlchemy engine fixture.

    Yields:
        SQLAlchemy Session instance.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_app(test_database_url: str) -> Generator[FastAPI, None, None]:
    """
    Provide a test FastAPI application.

    Creates a FastAPI app with test database configuration.
    Tables are created automatically for testing.

    Args:
        test_database_url: Database URL for testing.

    Yields:
        FastAPI application instance.
    """
    # Set DATABASE_URL environment variable so lifespan uses the test database
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = test_database_url

    try:
        # Initialize database with test URL
        init_database(test_database_url)
        app = create_app()
        # Create all tables for testing after app is created
        # (lifespan may have reinitialized, so get engine again)
        engine = get_engine()
        SharedBase.metadata.create_all(engine)
        yield app
        # Cleanup: drop tables after test
        SharedBase.metadata.drop_all(engine)
    finally:
        # Restore original DATABASE_URL
        if original_db_url is not None:
            os.environ["DATABASE_URL"] = original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        # Clean up SQLite test database file
        if hasattr(pytest, "current_db_file") and os.path.exists(
            pytest.current_db_file
        ):
            from contextlib import suppress

            with suppress(Exception):
                os.unlink(pytest.current_db_file)
