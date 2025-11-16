"""
Integration tests for ParseLogs use case.

Tests the ParseLogs use case with various log formats.
"""

import pytest

from src.endpoints.log_collector.application.parse_logs import ParseLogs


class TestParseLogsIntegration:
    """Integration test suite for ParseLogs use case."""

    @pytest.mark.integration
    def test_parse_extended_format_with_response_time(self):
        """Test parsing extended Nginx log format with response time."""
        # Arrange
        parser = ParseLogs()
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 0.05 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.client_ip == "192.168.1.1"
        assert entry.http_method == "GET"
        assert entry.request_uri == "/health"
        assert entry.status_code == 200
        assert entry.response_time == 0.05

    @pytest.mark.integration
    def test_parse_standard_format_without_response_time(self):
        """Test parsing standard Nginx log format without response time."""
        # Arrange
        parser = ParseLogs()
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.client_ip == "192.168.1.1"
        assert entry.http_method == "GET"
        assert entry.request_uri == "/health"
        assert entry.status_code == 200
        assert entry.response_time == 0.0

    @pytest.mark.integration
    def test_parse_log_with_different_timezone(self):
        """Test parsing log with different timezone."""
        # Arrange
        parser = ParseLogs()
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 -0500] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.client_ip == "192.168.1.1"
        assert entry.timestamp_utc is not None

    @pytest.mark.integration
    def test_parse_log_with_invalid_response_time_falls_back_to_zero(self):
        """Test parsing log with invalid response time falls back to zero."""
        # Arrange
        parser = ParseLogs()
        # Extended format with response time that matches regex but fails float conversion
        # Using multiple dots which matches [\d.]+ but fails float() conversion
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 1.2.3 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.client_ip == "192.168.1.1"
        assert entry.response_time == 0.0

    @pytest.mark.integration
    def test_parse_log_with_post_method(self):
        """Test parsing log with POST method."""
        # Arrange
        parser = ParseLogs()
        log_line = '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.http_method == "POST"
        assert entry.request_uri == "/demo-items"
        assert entry.status_code == 201

    @pytest.mark.integration
    def test_parse_log_with_error_status(self):
        """Test parsing log with error status code."""
        # Arrange
        parser = ParseLogs()
        log_line = '192.168.1.3 - - [16/Nov/2024:10:00:02 +0000] "GET /invalid HTTP/1.1" 404 0 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.status_code == 404
        assert entry.request_uri == "/invalid"

    @pytest.mark.integration
    def test_parse_log_with_invalid_timestamp_falls_back_to_current_time(self):
        """Test parsing log with invalid timestamp falls back to current time."""
        # Arrange
        parser = ParseLogs()
        # Log line with invalid timestamp format
        log_line = '192.168.1.1 - - [invalid-date] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.client_ip == "192.168.1.1"
        assert entry.timestamp_utc is not None

    @pytest.mark.integration
    def test_parse_log_with_naive_timestamp_handles_correctly(self):
        """Test parsing log when timestamp has no timezone info."""
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
            assert entry.timestamp_utc.tzinfo is None
