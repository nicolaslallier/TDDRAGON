"""
Query logs use case.

Handles querying access logs with filters and pagination.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_viewer.domain.repositories import LogQueryRepository


@dataclass
class QueryLogsResult:
    """
    Result of a query logs operation.

    Args:
        logs: List of LogEntry instances matching the query.
        total_count: Total number of logs matching the filters (before pagination).
        page: Current page number.
        page_size: Number of items per page.
    """

    logs: list[LogEntry]
    total_count: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """
        Calculate total number of pages.

        Returns:
            Total number of pages based on total_count and page_size.
        """
        if self.page_size == 0:
            return 0
        return (self.total_count + self.page_size - 1) // self.page_size

    @property
    def has_next_page(self) -> bool:
        """
        Check if there is a next page.

        Returns:
            True if there is a next page, False otherwise.
        """
        return self.page < self.total_pages

    @property
    def has_previous_page(self) -> bool:
        """
        Check if there is a previous page.

        Returns:
            True if there is a previous page, False otherwise.
        """
        return self.page > 1


class QueryLogs:
    """
    Use case for querying access logs with filters and pagination.

    This use case handles querying logs from the repository with various
    filters (time range, status code, URI, client IP) and pagination support.
    """

    def __init__(self, repository: LogQueryRepository) -> None:
        """
        Initialize QueryLogs use case.

        Args:
            repository: Repository for querying logs.
        """
        self._repository = repository

    def execute(
        self,
        start_time: datetime,
        end_time: datetime,
        status_code: Optional[int] = None,
        uri: Optional[str] = None,
        client_ip: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        order_by: str = "timestamp_utc",
        order_desc: bool = True,
    ) -> QueryLogsResult:
        """
        Execute query logs operation.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).
            status_code: Optional HTTP status code filter.
            uri: Optional URI filter (substring match).
            client_ip: Optional client IP filter.
            page: Page number (1-indexed).
            page_size: Number of items per page.
            order_by: Field to order by (default: "timestamp_utc").
            order_desc: Whether to order descending (default: True).

        Returns:
            QueryLogsResult containing logs and pagination information.
        """
        # Validate page number
        if page < 1:
            page = 1

        # Validate page size
        if page_size < 1:
            page_size = 50

        # Calculate offset
        offset = (page - 1) * page_size

        # Query logs with filters
        logs = list(
            self._repository.find_by_filters(
                start_time=start_time,
                end_time=end_time,
                status_code=status_code,
                uri=uri,
                client_ip=client_ip,
                limit=page_size,
                offset=offset,
                order_by=order_by,
                order_desc=order_desc,
            )
        )

        # Get total count
        total_count = self._repository.count_by_filters(
            start_time=start_time,
            end_time=end_time,
            status_code=status_code,
            uri=uri,
            client_ip=client_ip,
        )

        return QueryLogsResult(
            logs=logs,
            total_count=total_count,
            page=page,
            page_size=page_size,
        )

