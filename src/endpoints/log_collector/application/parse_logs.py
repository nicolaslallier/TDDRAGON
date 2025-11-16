"""
ParseLogs use case.

Handles parsing Nginx access log lines into LogEntry domain models.
"""

import re
from datetime import datetime

from src.endpoints.log_collector.domain.models import LogEntry


class ParseLogs:
    """
    Use case for parsing Nginx access log lines.

    This use case handles parsing Nginx combined log format lines
    into structured LogEntry domain models.
    """

    # Nginx combined log format regex
    # Format: $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
    # Extended format may include response time: ... $status $body_bytes_sent $response_time "$http_referer" ...
    # Try extended format first (with response time), then fall back to standard format
    LOG_PATTERN_EXTENDED = re.compile(
        r'(\S+) - (\S+) \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+) ([\d.]+) "([^"]*)" "([^"]*)"'
    )
    LOG_PATTERN_STANDARD = re.compile(
        r'(\S+) - (\S+) \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]*)" "([^"]*)"'
    )

    def execute(self, log_line: str) -> LogEntry:
        """
        Parse a Nginx access log line into a LogEntry.

        Supports Nginx combined log format:
        $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"

        Args:
            log_line: Raw log line from Nginx access log.

        Returns:
            Parsed LogEntry domain model.

        Raises:
            ValueError: If log line cannot be parsed.
        """
        # Try extended format first (with response time)
        match = self.LOG_PATTERN_EXTENDED.match(log_line.strip())
        if match:
            groups = match.groups()
            (
                client_ip,
                remote_user,
                time_local,
                http_method,
                request_uri,
                http_version,
                status_code,
                body_bytes_sent,
                response_time_str,
                http_referer,
                http_user_agent,
            ) = groups
        else:
            # Fall back to standard format
            match = self.LOG_PATTERN_STANDARD.match(log_line.strip())
            if not match:
                raise ValueError(f"Unable to parse log line: {log_line[:50]}...")
            groups = match.groups()
            (
                client_ip,
                remote_user,
                time_local,
                http_method,
                request_uri,
                http_version,
                status_code,
                body_bytes_sent,
                http_referer,
                http_user_agent,
            ) = groups
            response_time_str = None

        # Parse timestamp (Nginx format: 16/Nov/2024:10:00:00 +0000)
        try:
            timestamp = datetime.strptime(time_local, "%d/%b/%Y:%H:%M:%S %z")
            # Convert to UTC explicitly
            if timestamp.tzinfo:
                from datetime import timezone

                timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
            else:
                # Assume UTC if no timezone
                timestamp = timestamp.replace(tzinfo=None)
        except ValueError:
            # Fallback to current time if parsing fails
            timestamp = datetime.now()

        # Parse response time (if available in extended format)
        if response_time_str:
            try:
                response_time = float(response_time_str)
            except (ValueError, TypeError):
                response_time = 0.0
        else:
            response_time = 0.0

        return LogEntry(
            id=0,  # Will be assigned by repository
            timestamp_utc=timestamp,
            client_ip=client_ip,
            http_method=http_method,
            request_uri=request_uri,
            status_code=int(status_code),
            response_time=response_time,
            user_agent=http_user_agent if http_user_agent != "-" else None,
            raw_line=log_line,
        )
