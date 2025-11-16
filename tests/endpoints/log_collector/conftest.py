"""
Pytest fixtures for log_collector endpoint tests.

Provides database fixtures and test utilities for log_collector endpoint tests.
"""

import os
import tempfile
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Import models to register them with Base.metadata
from src.endpoints.log_collector.infrastructure.models import (  # noqa: F401
    NginxAccessLogModel,
    NginxUptimeModel,
)
from src.shared.models.base import Base as SharedBase


@pytest.fixture(scope="function")
def test_database_url() -> str:
    """
    Provide test database URL.

    Uses file-based SQLite for tests.

    Returns:
        Database connection URL string.
    """
    test_db_url = os.getenv("DATABASE_URL_TEST")
    if test_db_url:
        return test_db_url
    # Use file-based SQLite for tests
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as db_file:
        db_filename = db_file.name
    db_url = f"sqlite:///{db_filename}"
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
    # Properly dispose of all connections
    engine.dispose(close=True)


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
