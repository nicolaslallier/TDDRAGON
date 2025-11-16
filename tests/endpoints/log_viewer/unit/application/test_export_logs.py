"""
Unit tests for ExportLogs use case.
"""

import csv
import io
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_viewer.application.export_logs import ExportLogs
from src.endpoints.log_viewer.domain.repositories import LogQueryRepository


class TestExportLogs:
    """Test suite for ExportLogs use case."""

    @pytest.mark.unit
    def test_execute_returns_csv_content(self):
        """Test that execute returns CSV content for logs."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_entry1 = LogEntry(
            id=1,
            timestamp_utc=now - timedelta(minutes=30),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/test",
            status_code=200,
            response_time=0.05,
            user_agent="Mozilla/5.0",
        )
        mock_entry2 = LogEntry(
            id=2,
            timestamp_utc=now - timedelta(minutes=15),
            client_ip="192.168.1.2",
            http_method="POST",
            request_uri="/api/test",
            status_code=201,
            response_time=0.1,
            user_agent="curl/7.0",
        )

        mock_repository.find_by_filters.return_value = [mock_entry1, mock_entry2]

        use_case = ExportLogs(repository=mock_repository)

        # Act
        csv_content = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
        )

        # Assert
        assert csv_content is not None
        assert isinstance(csv_content, str)
        # Verify CSV can be parsed
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        # Should have header + 2 data rows
        assert len(rows) == 3
        # Verify header
        assert rows[0] == [
            "id",
            "timestamp_utc",
            "client_ip",
            "http_method",
            "request_uri",
            "status_code",
            "response_time",
            "user_agent",
        ]
        # Verify first data row
        assert rows[1][0] == "1"
        assert rows[1][2] == "192.168.1.1"
        assert rows[1][3] == "GET"
        assert rows[1][5] == "200"

    @pytest.mark.unit
    def test_execute_applies_filters(self):
        """Test that execute applies filters when exporting."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_entry = LogEntry(
            id=1,
            timestamp_utc=now - timedelta(minutes=30),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/test",
            status_code=500,
            response_time=0.05,
        )

        mock_repository.find_by_filters.return_value = [mock_entry]

        use_case = ExportLogs(repository=mock_repository)

        # Act
        csv_content = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=500,
            uri="/test",
            client_ip="192.168.1.1",
        )

        # Assert
        mock_repository.find_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=500,
            uri="/test",
            client_ip="192.168.1.1",
            limit=None,
            offset=0,
            order_by="timestamp_utc",
            order_desc=True,
        )
        assert csv_content is not None

    @pytest.mark.unit
    def test_execute_handles_empty_results(self):
        """Test that execute handles empty results correctly."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_repository.find_by_filters.return_value = []

        use_case = ExportLogs(repository=mock_repository)

        # Act
        csv_content = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
        )

        # Assert
        assert csv_content is not None
        # Should have header only
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        assert len(rows) == 1  # Header only
        assert rows[0] == [
            "id",
            "timestamp_utc",
            "client_ip",
            "http_method",
            "request_uri",
            "status_code",
            "response_time",
            "user_agent",
        ]

