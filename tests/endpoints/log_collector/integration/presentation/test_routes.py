"""
Integration tests for FastAPI routes.

Tests the API routes with a test database.
"""

from contextlib import suppress
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyLogRepository,
    SQLAlchemyUptimeRepository,
)
from src.endpoints.log_collector.main import create_app
from src.shared.infrastructure.database import init_database
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


@pytest.fixture
def sample_logs(test_app, test_database_url):
    """
    Create sample log entries for testing.

    Args:
        test_app: FastAPI app fixture (to ensure tables exist).
        test_database_url: Database URL for creating entries.

    Yields:
        List of created LogEntry instances.
    """
    from src.shared.infrastructure.database import get_session

    # Use get_session() to ensure we use the same connection pool as the API endpoint
    # Properly handle the generator lifecycle to ensure cleanup
    session_gen = get_session()
    session = next(session_gen)

    try:
        repository = SQLAlchemyLogRepository(session)
        now = datetime.now()
        entries = [
            LogEntry(
                id=0,
                timestamp_utc=now - timedelta(minutes=30),
                client_ip="192.168.1.1",
                http_method="GET",
                request_uri="/health",
                status_code=200,
                response_time=0.05,
            ),
            LogEntry(
                id=0,
                timestamp_utc=now - timedelta(minutes=20),
                client_ip="192.168.1.2",
                http_method="POST",
                request_uri="/demo-items",
                status_code=201,
                response_time=0.1,
            ),
            LogEntry(
                id=0,
                timestamp_utc=now - timedelta(minutes=10),
                client_ip="192.168.1.3",
                http_method="GET",
                request_uri="/invalid",
                status_code=404,
                response_time=0.02,
            ),
        ]
        created = []
        for entry in entries:
            created.append(repository.create(entry))
        session.commit()
        yield created
    finally:
        # Ensure session is properly closed and connection is returned to pool
        # For SQLite with StaticPool, we need to ensure the connection is explicitly closed
        try:
            # Get the connection before closing the session (for SQLite cleanup)
            connection = None
            if test_database_url.startswith("sqlite"):
                with suppress(Exception):
                    connection = session.connection()

            # Complete the generator - this will trigger its finally block to close the session
            with suppress(StopIteration):
                next(session_gen, None)

            # For SQLite, explicitly close the connection to avoid ResourceWarning
            if connection and test_database_url.startswith("sqlite"):
                with suppress(Exception):
                    connection.close()
        except Exception:
            # Fallback: try to close session if generator completion failed
            with suppress(Exception):
                if session:
                    session.close()


class TestLogsRoutes:
    """Integration test suite for logs routes."""

    @pytest.mark.integration
    @pytest.mark.filterwarnings("ignore:unclosed.*:ResourceWarning")
    def test_query_logs_returns_all_logs(self, client, sample_logs):
        """Test that querying logs returns all logs in time range."""
        # Arrange
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)

        # Act
        response = client.get(
            "/logs",
            params={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.integration
    def test_query_logs_filters_by_status_code(self, client, sample_logs):
        """Test that querying logs with status_code filter returns matching logs."""
        # Act
        response = client.get("/logs", params={"status_code": 404})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status_code"] == 404

    @pytest.mark.integration
    @pytest.mark.filterwarnings("ignore:unclosed.*:ResourceWarning")
    def test_query_logs_filters_by_uri(self, client, sample_logs):
        """Test that querying logs with uri filter returns matching logs."""
        # Act
        response = client.get("/logs", params={"uri": "/health"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["request_uri"] == "/health"

    @pytest.mark.integration
    def test_get_uptime_returns_uptime_percentage(
        self, client, test_app, test_database_url
    ):
        """Test that getting uptime returns uptime percentage."""
        # Arrange

        # Use get_session() to ensure we use the same connection pool as the API endpoint
        from src.shared.infrastructure.database import get_session

        session_gen = get_session()
        session = next(session_gen)

        try:
            repository = SQLAlchemyUptimeRepository(session)
            now = datetime.now()
            # Create 10 UP records
            for i in range(10):
                from src.endpoints.log_collector.domain.models import UptimeRecord

                record = UptimeRecord(
                    id=0,
                    timestamp_utc=now - timedelta(minutes=10 - i),
                    status="UP",
                    source="healthcheck",
                )
                repository.create(record)
            session.commit()

            # Act
            start_time = now - timedelta(hours=1)
            end_time = now
            response = client.get(
                "/logs/uptime",
                params={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                },
            )

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["uptime_percentage"] == 100.0
            assert data["total_measurements"] == 10
            assert data["up_count"] == 10
            assert data["down_count"] == 0
        finally:
            # Ensure session is properly closed and connection is returned to pool
            # Complete the generator to trigger its finally block which closes the session
            try:
                # Get the connection before closing the session (for SQLite cleanup)
                connection = None
                if test_database_url.startswith("sqlite"):
                    with suppress(Exception):
                        connection = session.connection()

                # Complete the generator - this will trigger its finally block to close the session
                with suppress(StopIteration):
                    next(session_gen, None)

                # For SQLite, explicitly close the connection to avoid ResourceWarning
                if connection and test_database_url.startswith("sqlite"):
                    with suppress(Exception):
                        connection.close()
            except Exception:
                # Fallback: try to close session if generator completion failed
                with suppress(Exception):
                    if session:
                        session.close()


class TestHealthRoutes:
    """Integration test suite for health routes."""

    @pytest.mark.integration
    def test_health_check_endpoint_returns_ok(self, client):
        """Test that the /health endpoint returns status 'ok'."""
        # Test line 153: Health check endpoint return statement
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
