"""
Unit tests for QueryLogs use case.
"""

from collections.abc import Sequence
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_viewer.application.query_logs import QueryLogs
from src.endpoints.log_viewer.domain.repositories import LogQueryRepository


class TestQueryLogs:
    """Test suite for QueryLogs use case."""

    @pytest.mark.unit
    def test_execute_returns_logs_with_filters(self):
        """Test that execute returns logs matching the filters."""
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
        )
        mock_entry2 = LogEntry(
            id=2,
            timestamp_utc=now - timedelta(minutes=15),
            client_ip="192.168.1.2",
            http_method="POST",
            request_uri="/test",
            status_code=201,
            response_time=0.1,
        )

        mock_repository.find_by_filters.return_value = [mock_entry1, mock_entry2]
        mock_repository.count_by_filters.return_value = 2

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            page=1,
            page_size=50,
        )

        # Assert
        assert result.total_count == 2
        assert len(result.logs) == 2
        assert result.logs[0] == mock_entry1
        assert result.logs[1] == mock_entry2
        mock_repository.find_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            limit=50,
            offset=0,
            order_by="timestamp_utc",
            order_desc=True,
        )
        mock_repository.count_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
        )

    @pytest.mark.unit
    def test_execute_filters_by_status_code(self):
        """Test that execute filters logs by status code."""
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
        mock_repository.count_by_filters.return_value = 1

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=500,
            uri=None,
            client_ip=None,
            page=1,
            page_size=50,
        )

        # Assert
        assert result.total_count == 1
        assert len(result.logs) == 1
        assert result.logs[0].status_code == 500
        mock_repository.find_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=500,
            uri=None,
            client_ip=None,
            limit=50,
            offset=0,
            order_by="timestamp_utc",
            order_desc=True,
        )

    @pytest.mark.unit
    def test_execute_filters_by_uri(self):
        """Test that execute filters logs by URI."""
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
            request_uri="/api/test",
            status_code=200,
            response_time=0.05,
        )

        mock_repository.find_by_filters.return_value = [mock_entry]
        mock_repository.count_by_filters.return_value = 1

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri="/api/test",
            client_ip=None,
            page=1,
            page_size=50,
        )

        # Assert
        assert result.total_count == 1
        assert len(result.logs) == 1
        assert result.logs[0].request_uri == "/api/test"
        mock_repository.find_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri="/api/test",
            client_ip=None,
            limit=50,
            offset=0,
            order_by="timestamp_utc",
            order_desc=True,
        )

    @pytest.mark.unit
    def test_execute_filters_by_client_ip(self):
        """Test that execute filters logs by client IP."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_entry = LogEntry(
            id=1,
            timestamp_utc=now - timedelta(minutes=30),
            client_ip="192.168.1.100",
            http_method="GET",
            request_uri="/test",
            status_code=200,
            response_time=0.05,
        )

        mock_repository.find_by_filters.return_value = [mock_entry]
        mock_repository.count_by_filters.return_value = 1

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip="192.168.1.100",
            page=1,
            page_size=50,
        )

        # Assert
        assert result.total_count == 1
        assert len(result.logs) == 1
        assert result.logs[0].client_ip == "192.168.1.100"
        mock_repository.find_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip="192.168.1.100",
            limit=50,
            offset=0,
            order_by="timestamp_utc",
            order_desc=True,
        )

    @pytest.mark.unit
    def test_execute_handles_pagination(self):
        """Test that execute handles pagination correctly."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_entries = [
            LogEntry(
                id=i,
                timestamp_utc=now - timedelta(minutes=60 - i),
                client_ip=f"192.168.1.{i}",
                http_method="GET",
                request_uri="/test",
                status_code=200,
                response_time=0.05,
            )
            for i in range(1, 51)
        ]

        mock_repository.find_by_filters.return_value = mock_entries[10:20]
        mock_repository.count_by_filters.return_value = 50

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            page=2,
            page_size=10,
        )

        # Assert
        assert result.total_count == 50
        assert len(result.logs) == 10
        mock_repository.find_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            limit=10,
            offset=10,
            order_by="timestamp_utc",
            order_desc=True,
        )

    @pytest.mark.unit
    def test_execute_handles_empty_results(self):
        """Test that execute handles empty results correctly."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_repository.find_by_filters.return_value = []
        mock_repository.count_by_filters.return_value = 0

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            page=1,
            page_size=50,
        )

        # Assert
        assert result.total_count == 0
        assert len(result.logs) == 0

    @pytest.mark.unit
    def test_execute_handles_invalid_page_number(self):
        """Test that execute handles invalid page number (page < 1)."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_repository.find_by_filters.return_value = []
        mock_repository.count_by_filters.return_value = 0

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            page=0,  # Invalid page
            page_size=50,
        )

        # Assert
        assert result.page == 1  # Should default to 1
        mock_repository.find_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            limit=50,
            offset=0,  # (1-1) * 50 = 0
            order_by="timestamp_utc",
            order_desc=True,
        )

    @pytest.mark.unit
    def test_execute_handles_invalid_page_size(self):
        """Test that execute handles invalid page size (page_size < 1)."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_repository.find_by_filters.return_value = []
        mock_repository.count_by_filters.return_value = 0

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            page=1,
            page_size=0,  # Invalid page size
        )

        # Assert
        assert result.page_size == 50  # Should default to 50
        mock_repository.find_by_filters.assert_called_once_with(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            limit=50,  # Should default to 50
            offset=0,
            order_by="timestamp_utc",
            order_desc=True,
        )

    @pytest.mark.unit
    def test_query_logs_result_properties(self):
        """Test QueryLogsResult properties (total_pages, has_next_page, has_previous_page)."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_repository.find_by_filters.return_value = []
        mock_repository.count_by_filters.return_value = 100

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            page=2,
            page_size=25,
        )

        # Assert
        assert result.total_count == 100
        assert result.total_pages == 4  # 100 / 25 = 4
        assert result.has_next_page is True  # page 2 < 4
        assert result.has_previous_page is True  # page 2 > 1

    @pytest.mark.unit
    def test_query_logs_result_no_next_page(self):
        """Test QueryLogsResult when there's no next page."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_repository.find_by_filters.return_value = []
        mock_repository.count_by_filters.return_value = 100

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            page=4,  # Last page
            page_size=25,
        )

        # Assert
        assert result.total_pages == 4
        assert result.has_next_page is False  # page 4 == 4
        assert result.has_previous_page is True  # page 4 > 1

    @pytest.mark.unit
    def test_query_logs_result_no_previous_page(self):
        """Test QueryLogsResult when there's no previous page."""
        # Arrange
        mock_repository = Mock(spec=LogQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now

        mock_repository.find_by_filters.return_value = []
        mock_repository.count_by_filters.return_value = 100

        use_case = QueryLogs(repository=mock_repository)

        # Act
        result = use_case.execute(
            start_time=start_time,
            end_time=end_time,
            status_code=None,
            uri=None,
            client_ip=None,
            page=1,  # First page
            page_size=25,
        )

        # Assert
        assert result.has_next_page is True  # page 1 < 4
        assert result.has_previous_page is False  # page 1 == 1

    @pytest.mark.unit
    def test_query_logs_result_zero_page_size(self):
        """Test QueryLogsResult when page_size is zero."""
        # Arrange
        from src.endpoints.log_viewer.application.query_logs import QueryLogsResult

        result = QueryLogsResult(logs=[], total_count=100, page=1, page_size=0)

        # Act & Assert
        assert result.total_pages == 0  # Should handle division by zero

