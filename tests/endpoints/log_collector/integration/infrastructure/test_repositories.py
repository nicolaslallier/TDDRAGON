"""
Integration tests for repository implementations.

Tests the SQLAlchemy repository implementations against a real database.
"""

from datetime import datetime, timedelta

import pytest

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord
from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyLogRepository,
    SQLAlchemyUptimeRepository,
)


class TestSQLAlchemyLogRepository:
    """Integration test suite for SQLAlchemyLogRepository."""

    @pytest.mark.integration
    def test_create_log_entry_persists_to_database(self, test_session):
        """Test that creating a log entry persists it to the database."""
        # Arrange
        repository = SQLAlchemyLogRepository(test_session)
        entry = LogEntry(
            id=0,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )

        # Act
        created_entry = repository.create(entry)

        # Assert
        assert created_entry.id is not None
        assert created_entry.client_ip == "192.168.1.1"
        test_session.commit()

    @pytest.mark.integration
    def test_find_by_time_range_returns_entries_in_range(self, test_session):
        """Test that find_by_time_range returns entries within time range."""
        # Arrange
        repository = SQLAlchemyLogRepository(test_session)
        now = datetime.now()
        entry1 = LogEntry(
            id=0,
            timestamp_utc=now - timedelta(minutes=30),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )
        entry2 = LogEntry(
            id=0,
            timestamp_utc=now - timedelta(minutes=10),
            client_ip="192.168.1.2",
            http_method="POST",
            request_uri="/demo-items",
            status_code=201,
            response_time=0.1,
        )
        repository.create(entry1)
        repository.create(entry2)
        test_session.commit()

        # Act
        start_time = now - timedelta(hours=1)
        end_time = now
        entries = repository.find_by_time_range(start_time, end_time)

        # Assert
        assert len(entries) == 2

    @pytest.mark.integration
    def test_find_by_status_code_returns_matching_entries(self, test_session):
        """Test that find_by_status_code returns entries with matching status code."""
        # Arrange
        repository = SQLAlchemyLogRepository(test_session)
        entry1 = LogEntry(
            id=0,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )
        entry2 = LogEntry(
            id=0,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.2",
            http_method="GET",
            request_uri="/invalid",
            status_code=404,
            response_time=0.02,
        )
        repository.create(entry1)
        repository.create(entry2)
        test_session.commit()

        # Act
        entries = repository.find_by_status_code(404)

        # Assert
        assert len(entries) == 1
        assert entries[0].status_code == 404


class TestSQLAlchemyUptimeRepository:
    """Integration test suite for SQLAlchemyUptimeRepository."""

    @pytest.mark.integration
    def test_create_uptime_record_persists_to_database(self, test_session):
        """Test that creating an uptime record persists it to the database."""
        # Arrange
        repository = SQLAlchemyUptimeRepository(test_session)
        record = UptimeRecord(
            id=0,
            timestamp_utc=datetime.now(),
            status="UP",
            source="healthcheck",
        )

        # Act
        created_record = repository.create(record)

        # Assert
        assert created_record.id is not None
        assert created_record.status == "UP"
        test_session.commit()

    @pytest.mark.integration
    def test_calculate_uptime_percentage_with_all_up_returns_100(self, test_session):
        """Test that calculating uptime with all UP records returns 100%."""
        # Arrange
        repository = SQLAlchemyUptimeRepository(test_session)
        now = datetime.now()
        for i in range(10):
            record = UptimeRecord(
                id=0,
                timestamp_utc=now - timedelta(minutes=10 - i),
                status="UP",
                source="healthcheck",
            )
            repository.create(record)
        test_session.commit()

        # Act
        start_time = now - timedelta(hours=1)
        end_time = now
        percentage = repository.calculate_uptime_percentage(start_time, end_time)

        # Assert
        assert percentage == 100.0

    @pytest.mark.integration
    def test_calculate_uptime_percentage_with_mixed_status(self, test_session):
        """Test that calculating uptime with mixed status returns correct percentage."""
        # Arrange
        repository = SQLAlchemyUptimeRepository(test_session)
        now = datetime.now()
        # Create 8 UP and 2 DOWN records
        for i in range(8):
            record = UptimeRecord(
                id=0,
                timestamp_utc=now - timedelta(minutes=10 - i),
                status="UP",
                source="healthcheck",
            )
            repository.create(record)
        for i in range(2):
            record = UptimeRecord(
                id=0,
                timestamp_utc=now - timedelta(minutes=2 - i),
                status="DOWN",
                source="healthcheck",
            )
            repository.create(record)
        test_session.commit()

        # Act
        start_time = now - timedelta(hours=1)
        end_time = now
        percentage = repository.calculate_uptime_percentage(start_time, end_time)

        # Assert
        assert percentage == 80.0  # 8 out of 10 = 80%

    @pytest.mark.integration
    def test_calculate_uptime_percentage_with_no_records_returns_100(
        self, test_session
    ):
        """Test that calculating uptime with no records returns 100%."""
        # Arrange
        repository = SQLAlchemyUptimeRepository(test_session)
        now = datetime.now()

        # Act - Query a time range with no records
        start_time = now - timedelta(hours=1)
        end_time = now
        percentage = repository.calculate_uptime_percentage(start_time, end_time)

        # Assert - No records means no downtime detected, so 100% uptime
        assert percentage == 100.0
