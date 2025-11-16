"""
CalculateUptime use case.

Handles calculating uptime percentage and recording uptime measurements.
"""

from datetime import datetime

from src.endpoints.log_collector.domain.models import UptimeRecord
from src.endpoints.log_collector.domain.repositories import UptimeRepository


class CalculateUptime:
    """
    Use case for calculating and recording uptime.

    This use case handles calculating uptime percentage from historical
    records and recording new uptime measurements.
    """

    def __init__(self, repository: UptimeRepository) -> None:
        """
        Initialize CalculateUptime use case.

        Args:
            repository: Repository for storing and querying uptime records.
        """
        self._repository = repository

    def execute(self, start_time: datetime, end_time: datetime) -> float:
        """
        Calculate uptime percentage for a time period.

        Args:
            start_time: Start of time period.
            end_time: End of time period.

        Returns:
            Uptime percentage as a float between 0.0 and 100.0.
        """
        return self._repository.calculate_uptime_percentage(start_time, end_time)

    def record_uptime(
        self, status: str, source: str, details: str | None = None
    ) -> UptimeRecord:
        """
        Record an uptime measurement.

        Args:
            status: Status value ("UP" or "DOWN").
            source: Source of the measurement (e.g., "healthcheck_nginx").
            details: Optional details about the measurement.

        Returns:
            Created UptimeRecord with assigned id.
        """
        record = UptimeRecord(
            id=0,  # Will be assigned by repository
            timestamp_utc=datetime.now(),
            status=status,
            source=source,
            details=details,
        )
        return self._repository.create(record)
