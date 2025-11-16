"""
Unit tests for QueryUptime use case.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from src.endpoints.log_collector.domain.models import UptimeRecord
from src.endpoints.log_viewer.application.query_uptime import QueryUptime
from src.endpoints.log_viewer.domain.repositories import UptimeQueryRepository


class TestQueryUptime:
    """Test suite for QueryUptime use case."""

    @pytest.mark.unit
    def test_execute_returns_uptime_records(self):
        """Test that execute returns uptime records for the time range."""
        # Arrange
        mock_repository = Mock(spec=UptimeQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=24)
        end_time = now

        mock_record1 = UptimeRecord(
            id=1,
            timestamp_utc=now - timedelta(hours=12),
            status="UP",
            source="healthcheck",
        )
        mock_record2 = UptimeRecord(
            id=2,
            timestamp_utc=now - timedelta(hours=6),
            status="DOWN",
            source="healthcheck",
            details="Connection timeout",
        )

        mock_repository.find_by_time_range.return_value = [mock_record1, mock_record2]
        mock_repository.calculate_uptime_percentage.return_value = 95.5

        use_case = QueryUptime(repository=mock_repository)

        # Act
        result = use_case.execute(start_time=start_time, end_time=end_time)

        # Assert
        assert len(result.records) == 2
        assert result.records[0] == mock_record1
        assert result.records[1] == mock_record2
        assert result.uptime_percentage == 95.5
        mock_repository.find_by_time_range.assert_called_once_with(
            start_time=start_time, end_time=end_time
        )
        mock_repository.calculate_uptime_percentage.assert_called_once_with(
            start_time=start_time, end_time=end_time
        )

    @pytest.mark.unit
    def test_execute_handles_empty_results(self):
        """Test that execute handles empty results correctly."""
        # Arrange
        mock_repository = Mock(spec=UptimeQueryRepository)
        now = datetime.now()
        start_time = now - timedelta(hours=24)
        end_time = now

        mock_repository.find_by_time_range.return_value = []
        mock_repository.calculate_uptime_percentage.return_value = 100.0

        use_case = QueryUptime(repository=mock_repository)

        # Act
        result = use_case.execute(start_time=start_time, end_time=end_time)

        # Assert
        assert len(result.records) == 0
        assert result.uptime_percentage == 100.0

