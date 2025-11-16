"""
Integration tests for FastAPI dependencies.

Tests the dependency injection functions with a real database.
"""

import pytest
from fastapi.testclient import TestClient

from src.endpoints.log_collector.main import create_app
from src.endpoints.log_collector.presentation.dependencies import (
    get_collect_logs_use_case,
    get_log_repository,
)
from src.shared.infrastructure.database import get_session, init_database
from src.shared.models.base import Base as SharedBase


@pytest.fixture
def test_app(test_database_url: str):
    """
    Provide a test FastAPI application.

    Args:
        test_database_url: Database URL for testing.

    Yields:
        FastAPI application instance.
    """
    import os

    # Set DATABASE_URL environment variable
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = test_database_url

    try:
        # Initialize database with test URL
        init_database(test_database_url)
        app = create_app()
        # Create all tables for testing
        from src.endpoints.log_collector.infrastructure.models import (  # noqa: F401
            NginxAccessLogModel,
            NginxUptimeModel,
        )
        from src.shared.infrastructure.database import get_engine

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
    Provide a test client for the FastAPI application.

    Args:
        test_app: FastAPI application fixture.

    Yields:
        TestClient instance.
    """
    return TestClient(test_app)


class TestDependencies:
    """Integration test suite for dependencies."""

    @pytest.mark.integration
    def test_get_collect_logs_use_case_returns_collect_logs_instance(
        self, client, test_app, test_database_url
    ):
        """
        Test that get_collect_logs_use_case returns a CollectLogs instance.

        This test exercises the dependency function to ensure it's properly
        instantiated and can be used.
        """
        # Arrange - Get a session and repository
        session_gen = get_session()
        session = next(session_gen)

        try:
            # Act - Get the repository and use case through dependencies
            repository = get_log_repository(session=session)
            use_case = get_collect_logs_use_case(repository=repository)

            # Assert - Verify the use case is properly instantiated
            assert use_case is not None
            assert hasattr(use_case, "execute")
            assert hasattr(use_case, "execute_batch")
        finally:
            # Ensure session is properly closed
            try:
                session.close()
                next(session_gen, None)
            except StopIteration:
                pass
            except Exception:
                pass
