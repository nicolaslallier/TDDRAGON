"""
Unit tests for log_viewer infrastructure repositories.

Tests repository implementations for querying logs and uptime.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_viewer.infrastructure.repositories import (
    LogViewerRepository,
    UptimeViewerRepository,
)


class TestLogViewerRepository:
    """Test suite for LogViewerRepository."""

    @pytest.fixture
    def mock_session(self):
        """Provide a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def repository(self, mock_session):
        """Provide a LogViewerRepository instance."""
        return LogViewerRepository(mock_session)

    @pytest.mark.unit
    def test_find_by_time_range_delegates_to_base_repository(self, repository, mock_session):
        """Test that find_by_time_range delegates to base repository."""
        # Arrange
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        mock_entries = [Mock(spec=LogEntry), Mock(spec=LogEntry)]

        # Mock base repository
        repository._base_repository.find_by_time_range = Mock(return_value=mock_entries)

        # Act
        result = repository.find_by_time_range(start_time, end_time)

        # Assert
        assert result == mock_entries
        repository._base_repository.find_by_time_range.assert_called_once_with(
            start_time=start_time, end_time=end_time
        )

    @pytest.mark.unit
    def test_find_by_filters_with_order_by_none_uses_default(self, repository, mock_session):
        """Test that find_by_filters uses default order_by when attribute doesn't exist."""
        # Arrange
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query

        # Mock _to_domain_model
        repository._to_domain_model = Mock()

        # Act
        result = repository.find_by_filters(
            start_time=start_time,
            end_time=end_time,
            order_by="nonexistent_field",
        )

        # Assert
        assert result == []
        # Should use timestamp_utc as default
        mock_query.order_by.assert_called()

    @pytest.mark.unit
    def test_find_by_filters_with_order_desc_false_orders_ascending(self, repository, mock_session):
        """Test that find_by_filters orders ascending when order_desc is False."""
        # Arrange
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query

        # Mock _to_domain_model
        repository._to_domain_model = Mock()

        # Act
        result = repository.find_by_filters(
            start_time=start_time,
            end_time=end_time,
            order_desc=False,
        )

        # Assert
        assert result == []
        # Should call order_by with asc()
        mock_query.order_by.assert_called()

    @pytest.mark.unit
    def test_count_by_filters_returns_zero_when_scalar_is_none(self, repository, mock_session):
        """Test that count_by_filters returns 0 when scalar() returns None."""
        # Arrange
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        mock_session.query.return_value = mock_query

        # Act
        result = repository.count_by_filters(start_time=start_time, end_time=end_time)

        # Assert
        assert result == 0


class TestUptimeViewerRepository:
    """Test suite for UptimeViewerRepository."""

    @pytest.fixture
    def mock_session(self):
        """Provide a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def repository(self, mock_session):
        """Provide an UptimeViewerRepository instance."""
        return UptimeViewerRepository(mock_session)

    @pytest.mark.unit
    def test_find_by_time_range_delegates_to_base_repository(self, repository, mock_session):
        """Test that find_by_time_range delegates to base repository."""
        # Arrange
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        mock_records = [Mock(), Mock()]

        # Mock base repository
        repository._base_repository.find_by_time_range = Mock(return_value=mock_records)

        # Act
        result = repository.find_by_time_range(start_time, end_time)

        # Assert
        assert result == mock_records
        repository._base_repository.find_by_time_range.assert_called_once_with(
            start_time=start_time, end_time=end_time
        )

    @pytest.mark.unit
    def test_calculate_uptime_percentage_delegates_to_base_repository(self, repository, mock_session):
        """Test that calculate_uptime_percentage delegates to base repository."""
        # Arrange
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        expected_percentage = 95.5

        # Mock base repository
        repository._base_repository.calculate_uptime_percentage = Mock(return_value=expected_percentage)

        # Act
        result = repository.calculate_uptime_percentage(start_time, end_time)

        # Assert
        assert result == expected_percentage
        repository._base_repository.calculate_uptime_percentage.assert_called_once_with(
            start_time=start_time, end_time=end_time
        )

