"""
Domain models for log collector.

Core business entities for log entries and uptime records.
"""

from datetime import datetime
from typing import Optional


class LogEntry:
    """
    Domain model representing a Nginx access log entry.

    This model represents a parsed log entry from Nginx access logs.
    It contains all the information extracted from a log line.

    Args:
        id: Unique identifier for the log entry.
        timestamp_utc: Timestamp when the request occurred (UTC).
        client_ip: IP address of the client.
        http_method: HTTP method (GET, POST, etc.).
        request_uri: URI/path requested.
        status_code: HTTP status code.
        response_time: Response time in seconds.
        user_agent: User agent string (optional).
        raw_line: Original log line (optional, for debugging).
    """

    def __init__(
        self,
        id: int,
        timestamp_utc: datetime,
        client_ip: str,
        http_method: str,
        request_uri: str,
        status_code: int,
        response_time: float,
        user_agent: Optional[str] = None,
        raw_line: Optional[str] = None,
    ) -> None:
        """Initialize LogEntry."""
        self.id = id
        self.timestamp_utc = timestamp_utc
        self.client_ip = client_ip
        self.http_method = http_method
        self.request_uri = request_uri
        self.status_code = status_code
        self.response_time = response_time
        self.user_agent = user_agent
        self.raw_line = raw_line


class UptimeRecord:
    """
    Domain model representing an uptime measurement.

    This model represents a point-in-time measurement of service
    availability status.

    Args:
        id: Unique identifier for the uptime record.
        timestamp_utc: Timestamp when the measurement was taken (UTC).
        status: Status value ("UP" or "DOWN").
        source: Source of the measurement (e.g., "healthcheck_nginx").
        details: Optional details about the measurement (e.g., error message).
    """

    def __init__(
        self,
        id: int,
        timestamp_utc: datetime,
        status: str,
        source: str,
        details: Optional[str] = None,
    ) -> None:
        """Initialize UptimeRecord."""
        self.id = id
        self.timestamp_utc = timestamp_utc
        self.status = status
        self.source = source
        self.details = details
