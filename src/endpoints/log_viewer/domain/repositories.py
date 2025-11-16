"""
Domain repository interfaces for log viewer.

Extends repository interfaces from log_collector with query capabilities
needed for the UI (filtering, pagination).
"""

from collections.abc import Sequence
from datetime import datetime
from typing import Optional, Protocol

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord


class LogQueryRepository(Protocol):
    """
    Protocol defining query operations for LogEntry data access.

    Extends LogRepository with additional query capabilities needed for UI.
    """

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

    def find_by_filters(
        self,
        start_time: datetime,
        end_time: datetime,
        status_code: Optional[int] = None,
        uri: Optional[str] = None,
        client_ip: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "timestamp_utc",
        order_desc: bool = True,
    ) -> Sequence[LogEntry]:
        """
        Find LogEntries with multiple filters and pagination.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).
            status_code: Optional HTTP status code filter.
            uri: Optional URI filter (substring match).
            client_ip: Optional client IP filter.
            limit: Maximum number of results to return.
            offset: Number of results to skip (for pagination).
            order_by: Field to order by (default: "timestamp_utc").
            order_desc: Whether to order descending (default: True).

        Returns:
            Sequence of LogEntries matching the filters.
        """
        ...  # pragma: no cover

    def count_by_filters(
        self,
        start_time: datetime,
        end_time: datetime,
        status_code: Optional[int] = None,
        uri: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> int:
        """
        Count LogEntries matching the filters.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).
            status_code: Optional HTTP status code filter.
            uri: Optional URI filter (substring match).
            client_ip: Optional client IP filter.

        Returns:
            Total count of matching LogEntries.
        """
        ...  # pragma: no cover


class UptimeQueryRepository(Protocol):
    """
    Protocol defining query operations for UptimeRecord data access.

    Extends UptimeRepository with additional query capabilities needed for UI.
    """

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

