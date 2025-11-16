"""
Regression tests for log_viewer application layer.

Ensures use cases don't regress and edge cases are handled.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_viewer.application.export_logs import ExportLogs
from src.endpoints.log_viewer.application.get_statistics import GetStatistics
from src.endpoints.log_viewer.application.query_logs import QueryLogs, QueryLogsResult


class TestQueryLogsRegression:
    """Regression tests for QueryLogs use case."""

    @pytest.mark.regression
    def test_query_logs_result_total_pages_with_zero_page_size(self):
        """Test that QueryLogsResult.total_pages returns 0 when page_size is 0."""
        # Test line 40-42: page_size == 0 returns 0
        from src.endpoints.log_collector.domain.models import LogEntry
        result = QueryLogsResult(
            logs=[],
            total_count=100,
            page=1,
            page_size=0,
        )
        assert result.total_pages == 0

    @pytest.mark.regression
    def test_query_logs_execute_sets_page_to_one_when_less_than_one(self):
        """Test that execute sets page to 1 when less than 1."""
        # Test line 112-113: page < 1 sets page = 1
        mock_repository = Mock()
        mock_repository.find_by_filters.return_value = []
        mock_repository.count_by_filters.return_value = 0
        use_case = QueryLogs(repository=mock_repository)
        result = use_case.execute(
            start_time=datetime.now(),
            end_time=datetime.now(),
            page=0,
            page_size=50,
        )
        assert result.page == 1

    @pytest.mark.regression
    def test_query_logs_execute_sets_page_size_to_fifty_when_less_than_one(self):
        """Test that execute sets page_size to 50 when less than 1."""
        # Test line 116-117: page_size < 1 sets page_size = 50
        mock_repository = Mock()
        mock_repository.find_by_filters.return_value = []
        mock_repository.count_by_filters.return_value = 0
        use_case = QueryLogs(repository=mock_repository)
        result = use_case.execute(
            start_time=datetime.now(),
            end_time=datetime.now(),
            page=1,
            page_size=0,
        )
        assert result.page_size == 50


class TestGetStatisticsRegression:
    """Regression tests for GetStatistics use case."""

    @pytest.mark.regression
    def test_get_http_code_histogram_raises_error_when_log_repository_is_none(self):
        """Test that get_http_code_histogram raises ValueError when log_repository is None."""
        # Test line 65: raise ValueError when log_repository is None
        use_case = GetStatistics(log_repository=None, uptime_repository=Mock())
        with pytest.raises(ValueError, match="log_repository is required"):
            use_case.get_http_code_histogram(
                start_time=datetime.now() - timedelta(hours=1),
                end_time=datetime.now(),
            )

    @pytest.mark.regression
    def test_get_http_code_histogram_counts_status_codes_correctly(self):
        """Test that get_http_code_histogram counts status codes correctly."""
        # Test line 85: histogram[log.status_code] += 1
        from src.endpoints.log_collector.domain.models import LogEntry

        mock_repository = Mock()
        mock_repository.find_by_filters.return_value = [
            LogEntry(
                id=1,
                timestamp_utc=datetime.now(),
                client_ip="127.0.0.1",
                http_method="GET",
                request_uri="/test",
                status_code=200,
                response_time=0.1,
            ),
            LogEntry(
                id=2,
                timestamp_utc=datetime.now(),
                client_ip="127.0.0.1",
                http_method="GET",
                request_uri="/test2",
                status_code=404,
                response_time=0.2,
            ),
            LogEntry(
                id=3,
                timestamp_utc=datetime.now(),
                client_ip="127.0.0.1",
                http_method="GET",
                request_uri="/test3",
                status_code=200,
                response_time=0.3,
            ),
        ]

        use_case = GetStatistics(log_repository=mock_repository, uptime_repository=Mock())
        histogram = use_case.get_http_code_histogram(
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
        )

        assert histogram[200] == 2
        assert histogram[404] == 1

    @pytest.mark.regression
    def test_get_uptime_timeline_handles_missing_uptime_repository(self):
        """Test that get_uptime_timeline raises ValueError when uptime_repository is None."""
        # Test line 105-106: uptime_repository is None check raises ValueError
        use_case = GetStatistics(log_repository=Mock(), uptime_repository=None)
        with pytest.raises(ValueError, match="uptime_repository is required"):
            use_case.get_uptime_timeline(
                start_time=datetime.now() - timedelta(hours=1),
                end_time=datetime.now(),
            )

    @pytest.mark.regression
    def test_get_uptime_timeline_handles_exception_gracefully(self):
        """Test that get_uptime_timeline propagates exceptions from repository."""
        # Test line 109-113: Repository exceptions are propagated
        mock_repository = Mock()
        mock_repository.find_by_time_range.side_effect = Exception("Database error")

        use_case = GetStatistics(log_repository=Mock(), uptime_repository=mock_repository)
        with pytest.raises(Exception, match="Database error"):
            use_case.get_uptime_timeline(
                start_time=datetime.now() - timedelta(hours=1),
                end_time=datetime.now(),
            )


class TestExportLogsRegression:
    """Regression tests for ExportLogs use case."""

    @pytest.mark.regression
    def test_export_logs_writes_csv_rows_correctly(self):
        """Test that export_logs writes CSV rows correctly."""
        # Test line 88: writer.writerow() call
        from io import StringIO

        from src.endpoints.log_collector.domain.models import LogEntry

        mock_repository = Mock()
        mock_repository.find_by_filters.return_value = [
            LogEntry(
                id=1,
                timestamp_utc=datetime(2024, 1, 1, 12, 0, 0),
                client_ip="127.0.0.1",
                http_method="GET",
                request_uri="/test",
                status_code=200,
                response_time=0.1,
            ),
        ]

        use_case = ExportLogs(repository=mock_repository)
        content = use_case.execute(
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
        )
        assert "127.0.0.1" in content
        assert "GET" in content
        assert "/test" in content
        assert "200" in content

