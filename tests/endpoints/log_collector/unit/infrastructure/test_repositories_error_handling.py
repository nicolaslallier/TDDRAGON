"""
Unit tests for repository error handling.

Tests error handling paths in repositories.py.
"""

from datetime import datetime, timedelta

import pytest

from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyUptimeRepository,
)


class TestSQLAlchemyUptimeRepositoryErrorHandling:
    """Test suite for SQLAlchemyUptimeRepository error handling."""

    @pytest.mark.unit
    def test_calculate_uptime_percentage_with_no_records_returns_100(
        self, test_session
    ):
        """Test that calculate_uptime_percentage returns 100.0 when no records exist."""
        # Arrange
        repository = SQLAlchemyUptimeRepository(test_session)
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        # Act
        result = repository.calculate_uptime_percentage(start_time, end_time)

        # Assert
        assert result == 100.0
