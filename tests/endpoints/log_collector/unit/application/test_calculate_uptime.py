"""
Unit tests for CalculateUptime use case.

Tests for calculating uptime percentage from uptime records.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

from src.endpoints.log_collector.application.calculate_uptime import CalculateUptime
from src.endpoints.log_collector.domain.models import UptimeRecord
from src.endpoints.log_collector.domain.repositories import UptimeRepository


class TestCalculateUptime:
    """Test suite for CalculateUptime use case."""

    def test_calculate_uptime_with_all_up_returns_100(self):
        """Test that calculating uptime with all UP records returns 100%."""
        # Arrange
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        mock_repository = Mock(spec=UptimeRepository)
        mock_repository.calculate_uptime_percentage.return_value = 100.0

        use_case = CalculateUptime(repository=mock_repository)

        # Act
        result = use_case.execute(start_time, end_time)

        # Assert
        assert result == 100.0
        mock_repository.calculate_uptime_percentage.assert_called_once_with(
            start_time, end_time
        )

    def test_calculate_uptime_with_mixed_status_returns_percentage(self):
        """Test that calculating uptime with mixed status returns correct percentage."""
        # Arrange
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        mock_repository = Mock(spec=UptimeRepository)
        mock_repository.calculate_uptime_percentage.return_value = 75.5

        use_case = CalculateUptime(repository=mock_repository)

        # Act
        result = use_case.execute(start_time, end_time)

        # Assert
        assert result == 75.5

    def test_record_uptime_creates_uptime_record(self):
        """Test that recording uptime creates an UptimeRecord."""
        # Arrange
        mock_repository = Mock(spec=UptimeRepository)
        mock_record = UptimeRecord(
            id=1,
            timestamp_utc=datetime.now(),
            status="UP",
            source="healthcheck",
        )
        mock_repository.create.return_value = mock_record

        use_case = CalculateUptime(repository=mock_repository)

        # Act
        result = use_case.record_uptime("UP", "healthcheck", "Health check passed")

        # Assert
        assert result == mock_record
        mock_repository.create.assert_called_once()
        created_record = mock_repository.create.call_args[0][0]
        assert isinstance(created_record, UptimeRecord)
        assert created_record.status == "UP"
        assert created_record.source == "healthcheck"
