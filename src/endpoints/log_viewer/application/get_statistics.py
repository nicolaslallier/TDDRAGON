"""
Get statistics use case.

Handles generating statistics and chart data for the UI.
"""

from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

from src.endpoints.log_viewer.domain.repositories import (
    LogQueryRepository,
    UptimeQueryRepository,
)


class GetStatistics:
    """
    Use case for generating statistics and chart data.

    This use case handles generating data for charts and visualizations,
    including HTTP status code histograms and uptime timelines.
    """

    def __init__(
        self,
        log_repository: Optional[LogQueryRepository] = None,
        uptime_repository: Optional[UptimeQueryRepository] = None,
    ) -> None:
        """
        Initialize GetStatistics use case.

        Args:
            log_repository: Repository for querying logs (optional).
            uptime_repository: Repository for querying uptime records (optional).
        """
        self._log_repository = log_repository
        self._uptime_repository = uptime_repository

    def get_http_code_histogram(
        self,
        start_time: datetime,
        end_time: datetime,
        status_code: Optional[int] = None,
        uri: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> dict[int, int]:
        """
        Get HTTP status code histogram.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).
            status_code: Optional HTTP status code filter.
            uri: Optional URI filter (substring match).
            client_ip: Optional client IP filter.

        Returns:
            Dictionary mapping status codes to counts.

        Raises:
            ValueError: If log_repository is not provided.
        """
        if self._log_repository is None:
            raise ValueError("log_repository is required for HTTP code histogram")

        # Query all logs matching filters
        logs = list(
            self._log_repository.find_by_filters(
                start_time=start_time,
                end_time=end_time,
                status_code=status_code,
                uri=uri,
                client_ip=client_ip,
                limit=None,  # No limit for statistics
                offset=0,
                order_by="timestamp_utc",
                order_desc=True,
            )
        )

        # Count status codes
        histogram: dict[int, int] = defaultdict(int)
        for log in logs:
            histogram[log.status_code] += 1

        return dict(histogram)

    def get_uptime_timeline(
        self, start_time: datetime, end_time: datetime
    ) -> list[dict[str, Any]]:
        """
        Get uptime timeline data for charting.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).

        Returns:
            List of dictionaries with timestamp and status for each record.

        Raises:
            ValueError: If uptime_repository is not provided.
        """
        if self._uptime_repository is None:
            raise ValueError("uptime_repository is required for uptime timeline")

        # Query uptime records
        records = list(
            self._uptime_repository.find_by_time_range(
                start_time=start_time, end_time=end_time
            )
        )

        # Convert to timeline format (ensure datetime is ISO format string for JSON serialization)
        timeline = []
        for record in records:
            timeline.append(
                {
                    "timestamp": record.timestamp_utc.isoformat() if record.timestamp_utc else None,
                    "status": record.status,
                    "source": record.source,
                    "details": record.details,
                }
            )

        return timeline

