"""
Unit tests for ParseLogs use case.

Tests for parsing Nginx access log lines into LogEntry domain models.
"""

from datetime import datetime

import pytest

from src.endpoints.log_collector.application.parse_logs import ParseLogs
from src.endpoints.log_collector.domain.models import LogEntry


class TestParseLogs:
    """Test suite for ParseLogs use case."""

    def test_parse_nginx_combined_log_format_returns_log_entry(self):
        """Test parsing Nginx combined log format."""
        # Arrange
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'
        parser = ParseLogs()

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert isinstance(entry, LogEntry)
        assert entry.client_ip == "192.168.1.1"
        assert entry.http_method == "GET"
        assert entry.request_uri == "/health"
        assert entry.status_code == 200
        assert entry.user_agent == "Mozilla/5.0"
        assert entry.raw_line == log_line

    def test_parse_nginx_log_with_response_time(self):
        """Test parsing Nginx log with response time."""
        # Arrange
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /demo-items HTTP/1.1" 200 456 0.05 "-" "Mozilla/5.0"'
        parser = ParseLogs()

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.status_code == 200
        assert entry.response_time == 0.05

    def test_parse_nginx_log_with_post_method(self):
        """Test parsing Nginx log with POST method."""
        # Arrange
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "POST /demo-items HTTP/1.1" 201 789 "-" "curl/7.0"'
        parser = ParseLogs()

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.http_method == "POST"
        assert entry.status_code == 201

    def test_parse_nginx_log_with_error_status(self):
        """Test parsing Nginx log with error status code."""
        # Arrange
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /invalid HTTP/1.1" 404 123 "-" "Mozilla/5.0"'
        parser = ParseLogs()

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert entry.status_code == 404
        assert entry.request_uri == "/invalid"

    def test_parse_nginx_log_with_invalid_format_raises_error(self):
        """Test parsing invalid log format raises ValueError."""
        # Arrange
        invalid_line = "not a valid log line"
        parser = ParseLogs()

        # Act & Assert
        with pytest.raises(ValueError, match="Unable to parse log line"):
            parser.execute(invalid_line)

    def test_parse_nginx_log_preserves_timestamp(self):
        """Test that timestamp is correctly parsed and preserved."""
        # Arrange
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'
        parser = ParseLogs()

        # Act
        entry = parser.execute(log_line)

        # Assert
        assert isinstance(entry.timestamp_utc, datetime)
        assert entry.timestamp_utc.year == 2024
        assert entry.timestamp_utc.month == 11
        assert entry.timestamp_utc.day == 16
