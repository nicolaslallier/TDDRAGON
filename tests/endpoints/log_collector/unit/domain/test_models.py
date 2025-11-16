"""
Unit tests for log collector domain models.

Tests for LogEntry and UptimeRecord domain models.
"""

from datetime import datetime

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord


class TestLogEntry:
    """Test suite for LogEntry domain model."""

    def test_create_log_entry_with_valid_data_returns_instance(self):
        """Test that creating a LogEntry with valid data returns an instance."""
        # Arrange
        timestamp = datetime.now()
        client_ip = "192.168.1.1"
        http_method = "GET"
        request_uri = "/health"
        status_code = 200
        response_time = 0.05

        # Act
        entry = LogEntry(
            id=1,
            timestamp_utc=timestamp,
            client_ip=client_ip,
            http_method=http_method,
            request_uri=request_uri,
            status_code=status_code,
            response_time=response_time,
        )

        # Assert
        assert entry.id == 1
        assert entry.timestamp_utc == timestamp
        assert entry.client_ip == client_ip
        assert entry.http_method == http_method
        assert entry.request_uri == request_uri
        assert entry.status_code == status_code
        assert entry.response_time == response_time

    def test_create_log_entry_with_optional_fields(self):
        """Test that creating a LogEntry with optional fields works."""
        # Arrange
        timestamp = datetime.now()
        user_agent = "Mozilla/5.0"
        raw_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123'

        # Act
        entry = LogEntry(
            id=1,
            timestamp_utc=timestamp,
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
            user_agent=user_agent,
            raw_line=raw_line,
        )

        # Assert
        assert entry.user_agent == user_agent
        assert entry.raw_line == raw_line


class TestUptimeRecord:
    """Test suite for UptimeRecord domain model."""

    def test_create_uptime_record_with_valid_data_returns_instance(self):
        """Test that creating an UptimeRecord with valid data returns an instance."""
        # Arrange
        timestamp = datetime.now()
        status = "UP"
        source = "healthcheck_nginx"

        # Act
        record = UptimeRecord(
            id=1,
            timestamp_utc=timestamp,
            status=status,
            source=source,
        )

        # Assert
        assert record.id == 1
        assert record.timestamp_utc == timestamp
        assert record.status == status
        assert record.source == source

    def test_create_uptime_record_with_details(self):
        """Test that creating an UptimeRecord with details works."""
        # Arrange
        timestamp = datetime.now()
        details = "Health check passed"

        # Act
        record = UptimeRecord(
            id=1,
            timestamp_utc=timestamp,
            status="UP",
            source="healthcheck",
            details=details,
        )

        # Assert
        assert record.details == details

    def test_create_uptime_record_with_down_status(self):
        """Test that creating an UptimeRecord with DOWN status works."""
        # Arrange
        timestamp = datetime.now()

        # Act
        record = UptimeRecord(
            id=1,
            timestamp_utc=timestamp,
            status="DOWN",
            source="healthcheck",
            details="Connection timeout",
        )

        # Assert
        assert record.status == "DOWN"
        assert record.details == "Connection timeout"
