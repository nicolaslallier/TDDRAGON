"""
Domain repository interfaces for log collector.

Protocol definitions for data access operations.
"""

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord


class LogRepository(Protocol):
    """
    Protocol defining the contract for LogEntry data access.

    Implementations should provide:
    - create: Create a new LogEntry in the data store
    - find_by_time_range: Query logs by time range
    - find_by_status_code: Query logs by HTTP status code
    """

    def create(self, entry: LogEntry) -> LogEntry:
        """
        Create a new LogEntry in the data store.

        Args:
            entry: LogEntry to create.

        Returns:
            Created LogEntry with assigned id.
        """
        ...  # pragma: no cover

    def find_by_time_range(
        self, start_time: datetime, end_time: datetime
    ) -> Sequence[LogEntry]:
        """
        Find LogEntries within a time range.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).

        Returns:
            Sequence of LogEntries ordered by timestamp.
        """
        ...  # pragma: no cover

    def find_by_status_code(self, status_code: int) -> Sequence[LogEntry]:
        """
        Find LogEntries by HTTP status code.

        Args:
            status_code: HTTP status code to filter by.

        Returns:
            Sequence of LogEntries with the specified status code.
        """
        ...  # pragma: no cover


class UptimeRepository(Protocol):
    """
    Protocol defining the contract for UptimeRecord data access.

    Implementations should provide:
    - create: Create a new UptimeRecord in the data store
    - find_by_time_range: Query uptime records by time range
    - calculate_uptime_percentage: Calculate uptime percentage for a period
    """

    def create(self, record: UptimeRecord) -> UptimeRecord:
        """
        Create a new UptimeRecord in the data store.

        Args:
            record: UptimeRecord to create.

        Returns:
            Created UptimeRecord with assigned id.
        """
        ...  # pragma: no cover

    def find_by_time_range(
        self, start_time: datetime, end_time: datetime
    ) -> Sequence[UptimeRecord]:
        """
        Find UptimeRecords within a time range.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).

        Returns:
            Sequence of UptimeRecords ordered by timestamp.
        """
        ...  # pragma: no cover

    def calculate_uptime_percentage(
        self, start_time: datetime, end_time: datetime
    ) -> float:
        """
        Calculate uptime percentage for a time period.

        Args:
            start_time: Start of time period.
            end_time: End of time period.

        Returns:
            Uptime percentage as a float between 0.0 and 100.0.
        """
        ...  # pragma: no cover
