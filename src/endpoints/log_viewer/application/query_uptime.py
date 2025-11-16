"""
Query uptime use case.

Handles querying uptime records and calculating uptime percentage.
"""

from dataclasses import dataclass
from datetime import datetime

from src.endpoints.log_collector.domain.models import UptimeRecord
from src.endpoints.log_viewer.domain.repositories import UptimeQueryRepository


@dataclass
class QueryUptimeResult:
    """
    Result of a query uptime operation.

    Args:
        records: List of UptimeRecord instances for the time range.
        uptime_percentage: Calculated uptime percentage for the period.
    """

    records: list[UptimeRecord]
    uptime_percentage: float


class QueryUptime:
    """
    Use case for querying uptime records and calculating uptime percentage.

    This use case handles querying uptime records from the repository
    for a given time range and calculating the overall uptime percentage.
    """

    def __init__(self, repository: UptimeQueryRepository) -> None:
        """
        Initialize QueryUptime use case.

        Args:
            repository: Repository for querying uptime records.
        """
        self._repository = repository

    def execute(
        self, start_time: datetime, end_time: datetime
    ) -> QueryUptimeResult:
        """
        Execute query uptime operation.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).

        Returns:
            QueryUptimeResult containing records and uptime percentage.
        """
        # Query uptime records
        records = list(
            self._repository.find_by_time_range(
                start_time=start_time, end_time=end_time
            )
        )

        # Calculate uptime percentage
        uptime_percentage = self._repository.calculate_uptime_percentage(
            start_time=start_time, end_time=end_time
        )

        return QueryUptimeResult(
            records=records,
            uptime_percentage=uptime_percentage,
        )

