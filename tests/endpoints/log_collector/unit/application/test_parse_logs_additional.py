"""
Additional unit tests for ParseLogs use case.

Tests for additional edge cases and uncovered lines.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.endpoints.log_collector.application.parse_logs import ParseLogs


class TestParseLogsAdditional:
    """Additional test suite for ParseLogs use case."""

    @pytest.mark.unit
    def test_parse_logs_with_timestamp_no_timezone_replaces_tzinfo(self):
        """Test that parsing log with timestamp without timezone replaces tzinfo with None."""
        # Arrange
        parser = ParseLogs()
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'

        # Mock datetime.strptime to return a naive datetime (no timezone)
        # This tests line 93: timestamp.replace(tzinfo=None)
        naive_datetime = datetime(2024, 11, 16, 10, 0, 0)

        with patch(
            "src.endpoints.log_collector.application.parse_logs.datetime"
        ) as mock_datetime_module:
            # Mock strptime to return naive datetime
            mock_datetime_module.strptime.return_value = naive_datetime
            mock_datetime_module.now.return_value = datetime(2024, 11, 16, 10, 0, 0)

            # Act
            entry = parser.execute(log_line)

            # Assert
            assert entry.timestamp_utc is not None
            # The timestamp should have tzinfo=None after replace() (line 93)
            assert entry.timestamp_utc.tzinfo is None

    @pytest.mark.unit
    def test_parse_logs_with_invalid_response_time_handles_valueerror(self):
        """Test that parsing log with invalid response_time_str handles ValueError."""
        # Arrange
        parser = ParseLogs()
        # Use extended format log line with valid response_time_str
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 0.05 "-" "Mozilla/5.0"'

        # Mock float() to raise ValueError to test line 102-103
        with patch("builtins.float", side_effect=ValueError("invalid literal")):
            entry = parser.execute(log_line)
            # Should fall back to 0.0 (line 103)
            assert entry.response_time == 0.0

    @pytest.mark.unit
    def test_parse_logs_with_invalid_response_time_handles_typeerror(self):
        """Test that parsing log with invalid response_time_str handles TypeError."""
        # Arrange
        parser = ParseLogs()
        # Use extended format log line
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 0.05 "-" "Mozilla/5.0"'

        # Mock float() to raise TypeError to test line 102-103
        with patch("builtins.float", side_effect=TypeError("unsupported type")):
            entry = parser.execute(log_line)
            # Should fall back to 0.0 (line 103)
            assert entry.response_time == 0.0
