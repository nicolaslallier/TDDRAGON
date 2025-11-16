"""
CollectLogs use case.

Handles collecting log lines, parsing them, and storing them in the repository.
"""

from src.endpoints.log_collector.application.parse_logs import ParseLogs
from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_collector.domain.repositories import LogRepository


class CollectLogs:
    """
    Use case for collecting and storing log entries.

    This use case handles parsing log lines and storing them in the repository.
    It can process single lines or batches of lines.
    """

    def __init__(self, repository: LogRepository) -> None:
        """
        Initialize CollectLogs use case.

        Args:
            repository: Repository for storing log entries.
        """
        self._repository = repository
        self._parser = ParseLogs()

    def execute(self, log_line: str) -> LogEntry:
        """
        Collect and store a single log line.

        Args:
            log_line: Raw log line from Nginx access log.

        Returns:
            Created LogEntry with assigned id.

        Raises:
            ValueError: If log line cannot be parsed.
        """
        entry = self._parser.execute(log_line)
        return self._repository.create(entry)

    def execute_batch(self, log_lines: list[str]) -> list[LogEntry]:
        """
        Collect and store multiple log lines.

        Args:
            log_lines: List of raw log lines from Nginx access log.

        Returns:
            List of created LogEntry instances.

        Raises:
            ValueError: If any log line cannot be parsed.
        """
        entries = []
        for log_line in log_lines:
            entry = self.execute(log_line)
            entries.append(entry)
        return entries
