"""
Unit tests for CollectLogs use case.

Tests for collecting and storing log entries.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.endpoints.log_collector.application.collect_logs import CollectLogs
from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_collector.domain.repositories import LogRepository


class TestCollectLogs:
    """Test suite for CollectLogs use case."""

    def test_collect_logs_parses_and_stores_entry(self):
        """Test that collecting logs parses and stores entries."""
        # Arrange
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'
        mock_repository = Mock(spec=LogRepository)
        mock_entry = LogEntry(
            id=1,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.0,
        )
        mock_repository.create.return_value = mock_entry

        use_case = CollectLogs(repository=mock_repository)

        # Act
        result = use_case.execute(log_line)

        # Assert
        assert result == mock_entry
        mock_repository.create.assert_called_once()
        created_entry = mock_repository.create.call_args[0][0]
        assert isinstance(created_entry, LogEntry)
        assert created_entry.client_ip == "192.168.1.1"

    def test_collect_logs_with_multiple_lines(self):
        """Test collecting multiple log lines."""
        # Arrange
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]
        mock_repository = Mock(spec=LogRepository)
        mock_repository.create.return_value = Mock(spec=LogEntry)

        use_case = CollectLogs(repository=mock_repository)

        # Act
        results = use_case.execute_batch(log_lines)

        # Assert
        assert len(results) == 2
        assert mock_repository.create.call_count == 2

    def test_collect_logs_with_invalid_line_raises_error(self):
        """Test that collecting logs with invalid line raises error."""
        # Arrange
        invalid_line = "not a valid log line"
        mock_repository = Mock(spec=LogRepository)
        use_case = CollectLogs(repository=mock_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Unable to parse log line"):
            use_case.execute(invalid_line)

        mock_repository.create.assert_not_called()
