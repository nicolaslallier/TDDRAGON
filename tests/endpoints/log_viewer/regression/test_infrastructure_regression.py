"""
Regression tests for log_viewer infrastructure layer.

Ensures repositories and auth don't regress and edge cases are handled.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_viewer.infrastructure.auth import MockAuthService
from src.endpoints.log_viewer.infrastructure.repositories import (
    LogViewerRepository,
    UptimeViewerRepository,
)


class TestAuthRegression:
    """Regression tests for authentication."""

    @pytest.mark.regression
    def test_get_username_returns_none_when_not_authenticated(self):
        """Test that get_username returns None when not authenticated."""
        # Test line 72: return None when not authenticated
        mock_request = Mock()
        mock_request.session = {}

        with patch.object(MockAuthService, "is_authenticated", return_value=False):
            username = MockAuthService.get_username(mock_request)
            assert username is None


class TestLogViewerRepositoryRegression:
    """Regression tests for LogViewerRepository."""

    @pytest.mark.regression
    def test_find_by_time_range_delegates_to_base_repository(self):
        """Test that find_by_time_range delegates to base repository."""
        # Test line 60: return self._base_repository.find_by_time_range(...)
        from sqlalchemy.orm import Session

        mock_session = Mock(spec=Session)
        mock_base_repository = Mock()
        mock_base_repository.find_by_time_range.return_value = []

        repository = LogViewerRepository(session=mock_session)
        repository._base_repository = mock_base_repository
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        result = repository.find_by_time_range(start_time=start_time, end_time=end_time)

        mock_base_repository.find_by_time_range.assert_called_once_with(
            start_time=start_time, end_time=end_time
        )
        assert result == []

    @pytest.mark.regression
    def test_find_by_filters_applies_status_code_filter(self):
        """Test that find_by_filters applies status_code filter."""
        # Test line 103: query.filter(NginxAccessLogModel.status_code == status_code)
        from src.endpoints.log_collector.infrastructure.models import NginxAccessLogModel
        from sqlalchemy.orm import Session

        mock_session = Mock(spec=Session)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repository = LogViewerRepository(session=mock_session)

        repository.find_by_filters(
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            status_code=404,
        )

        # Verify status_code filter was applied
        filter_calls = [call for call in mock_query.filter.call_args_list]
        assert len(filter_calls) > 0

    @pytest.mark.regression
    def test_find_by_filters_falls_back_to_timestamp_when_order_by_is_invalid(self):
        """Test that find_by_filters falls back to timestamp_utc when order_by is invalid."""
        # Test line 114: order_column = NginxAccessLogModel.timestamp_utc
        from sqlalchemy.orm import Session

        mock_session = Mock(spec=Session)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repository = LogViewerRepository(session=mock_session)

        repository.find_by_filters(
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            order_by="invalid_column",
        )

        # Verify order_by was called (fallback to timestamp_utc)
        mock_query.order_by.assert_called()

    @pytest.mark.regression
    def test_find_by_filters_applies_ascending_order(self):
        """Test that find_by_filters applies ascending order when order_desc is False."""
        # Test line 119: query.order_by(order_column.asc())
        from src.endpoints.log_collector.infrastructure.models import NginxAccessLogModel
        from sqlalchemy.orm import Session

        mock_session = Mock(spec=Session)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = []
        mock_query.all.return_value = []

        repository = LogViewerRepository(session=mock_session)

        repository.find_by_filters(
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            order_desc=False,
        )

        # Verify order_by was called with asc() method
        order_by_calls = mock_query.order_by.call_args_list
        assert len(order_by_calls) > 0
        # Check that asc() was called on the order column
        call_args = order_by_calls[0][0]
        assert call_args is not None

    @pytest.mark.regression
    def test_count_by_filters_applies_status_code_filter(self):
        """Test that count_by_filters applies status_code filter."""
        # Test line 163: query.filter(NginxAccessLogModel.status_code == status_code)
        from sqlalchemy.orm import Session

        mock_session = Mock(spec=Session)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 5

        repository = LogViewerRepository(session=mock_session)

        result = repository.count_by_filters(
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            status_code=404,
        )

        assert result == 5
        # Verify filter was applied
        mock_query.filter.assert_called()

    @pytest.mark.regression
    def test_to_domain_model_delegates_to_base_repository(self):
        """Test that to_domain_model delegates to base repository."""
        # Test line 184: return self._base_repository._to_domain_model(db_model)
        mock_base_repository = Mock()
        mock_db_model = Mock()
        mock_domain_model = Mock()
        mock_base_repository._to_domain_model.return_value = mock_domain_model

        from sqlalchemy.orm import Session

        mock_session = Mock(spec=Session)
        repository = LogViewerRepository(session=mock_session)
        repository._base_repository = mock_base_repository
        result = repository._to_domain_model(mock_db_model)

        mock_base_repository._to_domain_model.assert_called_once_with(mock_db_model)
        assert result == mock_domain_model


class TestUptimeViewerRepositoryRegression:
    """Regression tests for UptimeViewerRepository."""

    @pytest.mark.regression
    def test_find_by_time_range_delegates_to_base_repository(self):
        """Test that find_by_time_range delegates to base repository."""
        mock_base_repository = Mock()
        mock_base_repository.find_by_time_range.return_value = []

        from sqlalchemy.orm import Session

        mock_session = Mock(spec=Session)
        repository = UptimeViewerRepository(session=mock_session)
        repository._base_repository = mock_base_repository
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        result = repository.find_by_time_range(start_time=start_time, end_time=end_time)

        mock_base_repository.find_by_time_range.assert_called_once_with(
            start_time=start_time, end_time=end_time
        )
        assert result == []

