"""
Unit tests for GetStatistics use case.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord
from src.endpoints.log_viewer.application.get_statistics import GetStatistics
from src.endpoints.log_viewer.domain.repositories import (
    LogQueryRepository,
    UptimeQueryRepository,
)


class TestGetStatistics:
    """Test suite for GetStatistics use case."""

    @pytest.mark.unit
    def test_get_http_code_histogram_returns_correct_counts(self):
        """Test that get_http_code_histogram returns correct status code counts."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_entries = [
            LogEntry(
                id=1,
                timestamp_utc=now - timedelta(minutes=30),
                client_ip="192.168.1.1",
                http_method="GET",
                request_uri="/test",
                status_code=200,
                response_time=0.05,
            ),
            LogEntry(
                id=2,
                timestamp_utc=now - timedelta(minutes=25),
                client_ip="192.168.1.2",
                http_method="GET",
                request_uri="/test",
                status_code=200,
                response_time=0.05,
            ),
            LogEntry(
                id=3,
                timestamp_utc=now - timedelta(minutes=20),
                client_ip="192.168.1.3",
                http_method="POST",
                request_uri="/api/test",
                status_code=201,
                response_time=0.1,
            ),
            LogEntry(
                id=4,
                timestamp_utc=now - timedelta(minutes=15),
                client_ip="192.168.1.4",
                http_method="GET",
                request_uri="/error",
                status_code=500,
                response_time=0.2,
            ),
        ]

        mock_repository.find_by_filters.return_value = mock_entries

        use_case = GetStatistics(log_repository=mock_repository)

        # Act
        histogram = use_case.get_http_code_histogram(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
        )

        # Assert
        assert histogram[200] == 2
        assert histogram[201] == 1
        assert histogram[500] == 1
        assert len(histogram) == 3

    @pytest.mark.unit
    def test_get_http_code_histogram_applies_filters(self):
        """Test that get_http_code_histogram applies filters."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_entries = [
            LogEntry(
                id=1,
                timestamp_utc=now - timedelta(minutes=30),
                client_ip="192.168.1.1",
                http_method="GET",
                request_uri="/test",
                status_code=500,
                response_time=0.05,
            ),
        ]

        mock_repository.find_by_filters.return_value = mock_entries

        use_case = GetStatistics(log_repository=mock_repository)

        # Act
        histogram = use_case.get_http_code_histogram(
            start_time=start_time,
            end_time=end_time,
            status_code=500,
            uri="/test",
            client_ip=None,
        )

        # Assert
        mock_repository.find_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=500,
            uri="/test",
            client_ip=None,
            limit=None,
            offset=0,
            order_by="timestamp_utc",
            order_desc=True,
        )
        assert histogram[500] == 1

    @pytest.mark.unit
    def test_get_uptime_timeline_returns_correct_data(self):
        """Test that get_uptime_timeline returns correct timeline data."""
        # Arrange
        mock_repository = Mock(spec=UptimeQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=24)
        end_time = now

        mock_records = [
            UptimeRecord(
                id=1,
                timestamp_utc=now - timedelta(hours=20),
                status="UP",
                source="healthcheck",
            ),
            UptimeRecord(
                id=2,
                timestamp_utc=now - timedelta(hours=18),
                status="DOWN",
                source="healthcheck",
                details="Connection timeout",
            ),
            UptimeRecord(
                id=3,
                timestamp_utc=now - timedelta(hours=16),
                status="UP",
                source="healthcheck",
            ),
        ]

        mock_repository.find_by_time_range.return_value = mock_records

        use_case = GetStatistics(uptime_repository=mock_repository)

        # Act
        timeline = use_case.get_uptime_timeline(
            start_time=start_time, end_time=end_time
        )

        # Assert
        assert len(timeline) == 3
        # Timestamp is returned as ISO format string for JSON serialization
        assert timeline[0]["timestamp"] == mock_records[0].timestamp_utc.isoformat()
        assert timeline[0]["status"] == "UP"
        assert timeline[0]["source"] == "healthcheck"
        assert timeline[1]["status"] == "DOWN"
        assert timeline[1]["details"] == "Connection timeout"
        assert timeline[2]["status"] == "UP"

    @pytest.mark.unit
    def test_get_uptime_timeline_handles_empty_results(self):
        """Test that get_uptime_timeline handles empty results correctly."""
        # Arrange
        mock_repository = Mock(spec=UptimeQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=24)
        end_time = now

        mock_repository.find_by_time_range.return_value = []

        use_case = GetStatistics(uptime_repository=mock_repository)

        # Act
        timeline = use_case.get_uptime_timeline(
            start_time=start_time, end_time=end_time
        )

        # Assert
        assert len(timeline) == 0

    @pytest.mark.unit
    def test_get_http_code_histogram_raises_error_when_repository_missing(self):
        """Test that get_http_code_histogram raises ValueError when repository is None."""
        # Arrange
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        use_case = GetStatistics(log_repository=None)

        # Act & Assert
        with pytest.raises(ValueError, match="log_repository is required"):
            use_case.get_http_code_histogram(
                start_time=start_time,
                end_time=end_time,
                status_code=None,
                uri=None,
                client_ip=None,
            )

    @pytest.mark.unit
    def test_get_uptime_timeline_raises_error_when_repository_missing(self):
        """Test that get_uptime_timeline raises ValueError when repository is None."""
        # Arrange
        now = datetime.now()
        start_time = now - timedelta(hours=24)
        end_time = now

        use_case = GetStatistics(uptime_repository=None)

        # Act & Assert
        with pytest.raises(ValueError, match="uptime_repository is required"):
            use_case.get_uptime_timeline(start_time=start_time, end_time=end_time)

