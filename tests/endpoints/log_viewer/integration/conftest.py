"""
Pytest configuration for log_viewer integration tests.
"""

import os

import pytest
from fastapi.testclient import TestClient

from src.endpoints.log_viewer.main import create_app
from src.endpoints.log_collector.infrastructure.models import (  # noqa: F401
    NginxAccessLogModel,
    NginxUptimeModel,
)
from src.shared.infrastructure.database import init_database, get_engine
from src.shared.models.base import Base as SharedBase


@pytest.fixture
def test_database_url() -> str:
    """
    Provide a test database URL.

    Returns:
        SQLite in-memory database URL for testing.
    """
    return "sqlite:///:memory:"


@pytest.fixture
def test_app(test_database_url: str):
    """
    Provide a test FastAPI application.

    Args:
        test_database_url: Database URL for testing.

    Yields:
        FastAPI application instance.
    """
    # Set DATABASE_URL environment variable
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = test_database_url

    try:
        # Initialize database with test URL
        init_database(test_database_url)
        app = create_app()
        # Create all tables for testing
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


@pytest.fixture
def client(test_app):
    """
    Provide a test client.

    Args:
        test_app: FastAPI application instance.

    Yields:
        TestClient instance.
    """
    return TestClient(test_app)

