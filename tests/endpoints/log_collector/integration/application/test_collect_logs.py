"""
Integration tests for CollectLogs use case.

Tests the CollectLogs use case with a real database.
"""

import pytest

from src.endpoints.log_collector.application.collect_logs import CollectLogs
from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyLogRepository,
)


class TestCollectLogsIntegration:
    """Integration test suite for CollectLogs use case."""

    @pytest.mark.integration
    def test_execute_parses_and_stores_single_log_line(self, test_session):
        """Test that execute parses and stores a single log line."""
        # Arrange
        repository = SQLAlchemyLogRepository(test_session)
        use_case = CollectLogs(repository=repository)
        log_line = '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"'

        # Act
        entry = use_case.execute(log_line)

        # Assert
        assert entry.id is not None
        assert entry.client_ip == "192.168.1.1"
        assert entry.http_method == "GET"
        assert entry.request_uri == "/health"
        assert entry.status_code == 200
        test_session.commit()

    @pytest.mark.integration
    def test_execute_batch_parses_and_stores_multiple_log_lines(self, test_session):
        """Test that execute_batch parses and stores multiple log lines."""
        # Arrange
        repository = SQLAlchemyLogRepository(test_session)
        use_case = CollectLogs(repository=repository)
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
            '192.168.1.3 - - [16/Nov/2024:10:00:02 +0000] "GET /demo-items HTTP/1.1" 200 789 "-" "Mozilla/5.0"',
        ]

        # Act
        entries = use_case.execute_batch(log_lines)

        # Assert
        assert len(entries) == 3
        assert entries[0].client_ip == "192.168.1.1"
        assert entries[1].client_ip == "192.168.1.2"
        assert entries[2].client_ip == "192.168.1.3"
        test_session.commit()

    @pytest.mark.integration
    def test_execute_with_invalid_log_line_raises_error(self, test_session):
        """Test that execute raises ValueError for invalid log line."""
        # Arrange
        repository = SQLAlchemyLogRepository(test_session)
        use_case = CollectLogs(repository=repository)
        invalid_log_line = "invalid log line format"

        # Act & Assert
        with pytest.raises(ValueError, match="Unable to parse log line"):
            use_case.execute(invalid_log_line)
