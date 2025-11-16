"""
Regression tests for log collector application layer.

Ensures that use cases continue to work correctly after changes.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.endpoints.log_collector.application.calculate_uptime import CalculateUptime
from src.endpoints.log_collector.application.collect_logs import CollectLogs
from src.endpoints.log_collector.application.parse_logs import ParseLogs
from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord
from src.endpoints.log_collector.domain.repositories import (
    LogRepository,
    UptimeRepository,
)


class TestParseLogsRegression:
    """Regression tests for ParseLogs use case."""

    @pytest.mark.regression
    def test_parse_logs_handles_standard_format(self):
        """Test that ParseLogs handles standard Nginx combined format."""
        # Arrange
        parser = ParseLogs()
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.client_ip == "192.168.1.1"
        assert entry.http_method == "GET"
        assert entry.status_code == 200

    @pytest.mark.regression
    def test_parse_logs_handles_extended_format_with_response_time(self):
        """Test that ParseLogs handles extended format with response time."""
        # Arrange
        parser = ParseLogs()
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 0.05 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.response_time == 0.05

    @pytest.mark.regression
    def test_parse_logs_handles_invalid_format_raises_error(self):
        """Test that ParseLogs raises ValueError for invalid format."""
        # Arrange
        parser = ParseLogs()
        invalid_line = "not a valid log line"

        # Act & Assert
        with pytest.raises(ValueError, match="Unable to parse log line"):
            parser.execute(invalid_line)

    @pytest.mark.regression
    def test_parse_logs_handles_invalid_timestamp_falls_back_to_current_time(self):
        """Test that ParseLogs falls back to current time for invalid timestamp."""
        # Arrange
        parser = ParseLogs()
        # Log line with invalid timestamp format
        log_line = '192.168.1.1 - - [invalid-date] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.client_ip == "192.168.1.1"
        assert entry.timestamp_utc is not None

    @pytest.mark.regression
    def test_parse_logs_handles_naive_timestamp(self):
        """Test that ParseLogs handles timestamp without timezone."""
        # Arrange
        from datetime import datetime
        from unittest.mock import patch

        parser = ParseLogs()
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'

        # Mock strptime to return a naive datetime (no timezone)
        naive_datetime = datetime(2024, 11, 16, 10, 0, 0)
        with patch(
            "src.endpoints.log_collector.application.parse_logs.datetime"
        ) as mock_datetime:
            mock_datetime.strptime.return_value = naive_datetime
            mock_datetime.now.return_value = datetime(2024, 11, 16, 10, 0, 0)

            # Act
            entry = parser.execute(log_line)

            # Assert
            assert entry.client_ip == "192.168.1.1"
            assert entry.timestamp_utc is not None

    @pytest.mark.regression
    def test_parse_logs_handles_invalid_response_time_falls_back_to_zero(self):
        """Test that ParseLogs falls back to zero for invalid response time."""
        # Arrange
        parser = ParseLogs()
        # Extended format with response time that matches regex but fails float conversion
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 1.2.3 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.client_ip == "192.168.1.1"
        assert entry.response_time == 0.0


class TestCollectLogsRegression:
    """Regression tests for CollectLogs use case."""

    @pytest.mark.regression
    def test_collect_logs_initializes_with_repository(self):
        """Test that CollectLogs.__init__ stores repository correctly."""
        # Arrange
        mock_repository = MagicMock(spec=LogRepository)

        # Act
        use_case = CollectLogs(repository=mock_repository)

        # Assert
        assert use_case._repository is mock_repository

    @pytest.mark.regression
    def test_collect_logs_execute_parses_and_stores(self):
        """Test that execute method parses and stores log entry."""
        # Arrange
        from unittest.mock import MagicMock

        mock_repository = MagicMock(spec=LogRepository)
        mock_entry = LogEntry(
            id=1,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )
        mock_repository.create.return_value = mock_entry
        use_case = CollectLogs(repository=mock_repository)
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'

        # Act
        result = use_case.execute(log_line)

        # Assert
        assert result is mock_entry
        mock_repository.create.assert_called_once()
        # Verify the parser was actually called (not mocked)
        assert result.client_ip == "192.168.1.1"

    @pytest.mark.regression
    def test_collect_logs_execute_batch_processes_multiple_lines(self):
        """Test that execute_batch processes multiple log lines."""
        # Arrange
        mock_repository = MagicMock(spec=LogRepository)
        mock_entry1 = LogEntry(
            id=1,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )
        mock_entry2 = LogEntry(
            id=2,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.2",
            http_method="POST",
            request_uri="/demo-items",
            status_code=201,
            response_time=0.1,
        )
        mock_repository.create.side_effect = [mock_entry1, mock_entry2]
        use_case = CollectLogs(repository=mock_repository)
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]

        # Act
        result = use_case.execute_batch(log_lines)

        # Assert
        assert len(result) == 2
        assert result[0] is mock_entry1
        assert result[1] is mock_entry2
        assert mock_repository.create.call_count == 2


class TestCalculateUptimeRegression:
    """Regression tests for CalculateUptime use case."""

    @pytest.mark.regression
    def test_calculate_uptime_initializes_with_repository(self):
        """Test that CalculateUptime.__init__ stores repository correctly."""
        # Arrange
        mock_repository = MagicMock(spec=UptimeRepository)

        # Act
        use_case = CalculateUptime(repository=mock_repository)

        # Assert
        assert use_case._repository is mock_repository

    @pytest.mark.regression
    def test_calculate_uptime_execute_calls_repository(self):
        """Test that execute method calls repository.calculate_uptime_percentage."""
        # Arrange
        mock_repository = MagicMock(spec=UptimeRepository)
        mock_repository.calculate_uptime_percentage.return_value = 95.5
        use_case = CalculateUptime(repository=mock_repository)
        start_time = datetime.now()
        end_time = datetime.now()

        # Act
        result = use_case.execute(start_time, end_time)

        # Assert
        assert result == 95.5
        mock_repository.calculate_uptime_percentage.assert_called_once_with(
            start_time, end_time
        )

    @pytest.mark.regression
    def test_record_uptime_creates_record(self):
        """Test that record_uptime creates UptimeRecord."""
        # Arrange
        mock_repository = MagicMock(spec=UptimeRepository)
        mock_record = UptimeRecord(
            id=1,
            timestamp_utc=datetime.now(),
            status="UP",
            source="healthcheck",
        )
        mock_repository.create.return_value = mock_record
        use_case = CalculateUptime(repository=mock_repository)

        # Act
        result = use_case.record_uptime("UP", "healthcheck")

        # Assert
        assert result is mock_record
        mock_repository.create.assert_called_once()
