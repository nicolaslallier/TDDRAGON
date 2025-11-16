"""
Integration tests for CalculateUptime use case.

Tests the CalculateUptime use case with a real database.
"""


import pytest

from src.endpoints.log_collector.application.calculate_uptime import CalculateUptime
from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyUptimeRepository,
)


class TestCalculateUptimeIntegration:
    """Integration test suite for CalculateUptime use case."""

    @pytest.mark.integration
    def test_record_uptime_creates_uptime_record(self, test_session):
        """Test that record_uptime creates an uptime record in the database."""
        # Arrange
        repository = SQLAlchemyUptimeRepository(test_session)
        use_case = CalculateUptime(repository=repository)

        # Act
        record = use_case.record_uptime(
            status="UP", source="healthcheck", details="Test measurement"
        )

        # Assert
        assert record.id is not None
        assert record.status == "UP"
        assert record.source == "healthcheck"
        assert record.details == "Test measurement"
        assert record.timestamp_utc is not None
        test_session.commit()

    @pytest.mark.integration
    def test_record_uptime_with_down_status(self, test_session):
        """Test that record_uptime can record DOWN status."""
        # Arrange
        repository = SQLAlchemyUptimeRepository(test_session)
        use_case = CalculateUptime(repository=repository)

        # Act
        record = use_case.record_uptime(
            status="DOWN", source="healthcheck", details="Connection timeout"
        )

        # Assert
        assert record.id is not None
        assert record.status == "DOWN"
        assert record.source == "healthcheck"
        assert record.details == "Connection timeout"
        test_session.commit()

    @pytest.mark.integration
    def test_record_uptime_without_details(self, test_session):
        """Test that record_uptime works without details."""
        # Arrange
        repository = SQLAlchemyUptimeRepository(test_session)
        use_case = CalculateUptime(repository=repository)

        # Act
        record = use_case.record_uptime(status="UP", source="healthcheck")

        # Assert
        assert record.id is not None
        assert record.status == "UP"
        assert record.source == "healthcheck"
        assert record.details is None
        test_session.commit()
