"""
Export logs use case.

Handles exporting access logs to CSV format.
"""

import csv
import io
from datetime import datetime
from typing import Optional

from src.endpoints.log_viewer.domain.repositories import LogQueryRepository


class ExportLogs:
    """
    Use case for exporting access logs to CSV format.

    This use case handles exporting logs from the repository to CSV format
    with all filters applied.
    """

    def __init__(self, repository: LogQueryRepository) -> None:
        """
        Initialize ExportLogs use case.

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
    ) -> str:
        """
        Execute export logs operation.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).
            status_code: Optional HTTP status code filter.
            uri: Optional URI filter (substring match).
            client_ip: Optional client IP filter.

        Returns:
            CSV content as a string.
        """
        # Query all logs matching filters (no pagination for export)
        logs = list(
            self._repository.find_by_filters(
                start_time=start_time,
                end_time=end_time,
                status_code=status_code,
                uri=uri,
                client_ip=client_ip,
                limit=None,  # No limit for export
                offset=0,
                order_by="timestamp_utc",
                order_desc=True,
            )
        )

        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "id",
                "timestamp_utc",
                "client_ip",
                "http_method",
                "request_uri",
                "status_code",
                "response_time",
                "user_agent",
            ]
        )

        # Write data rows
        for log in logs:
            writer.writerow(
                [
                    str(log.id),
                    log.timestamp_utc.isoformat(),
                    log.client_ip,
                    log.http_method,
                    log.request_uri,
                    str(log.status_code),
                    str(log.response_time),
                    log.user_agent or "",
                ]
            )

        return output.getvalue()

