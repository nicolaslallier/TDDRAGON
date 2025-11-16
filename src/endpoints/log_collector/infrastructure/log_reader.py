"""
Log reader for reading Nginx access logs.

Supports reading from files (with position tracking) and streams.
"""

from pathlib import Path
from typing import IO


class LogReader:
    """
    Reader for Nginx access log files and streams.

    This class handles reading log lines from files (with position tracking
    for incremental reads) and from streams (stdout, pipes, etc.).
    """

    def __init__(self) -> None:
        """Initialize LogReader."""
        self._file_positions: dict[str, int] = {}

    def read_from_file(self, file_path: str) -> list[str]:
        """
        Read all lines from a log file.

        Args:
            file_path: Path to the log file.

        Returns:
            List of log lines. Returns empty list if file doesn't exist.
        """
        path = Path(file_path)
        if not path.exists():
            return []

        try:
            with open(path, encoding="utf-8") as f:
                return [line.rstrip("\n") for line in f if line.strip()]
        except OSError:
            return []

    def read_new_lines(self, file_path: str) -> list[str]:
        """
        Read new lines from a log file since last read.

        Tracks file position to only read new lines. Useful for
        continuous monitoring of log files.

        Args:
            file_path: Path to the log file.

        Returns:
            List of new log lines since last read.
        """
        path = Path(file_path)
        if not path.exists():
            return []

        last_position = self._file_positions.get(file_path, 0)

        try:
            with open(path, encoding="utf-8") as f:
                # Seek to last position
                f.seek(last_position)

                # Read new lines
                new_lines = []
                for line in f:
                    if line.strip():
                        new_lines.append(line.rstrip("\n"))

                # Update position
                self._file_positions[file_path] = f.tell()

                return new_lines
        except OSError:
            return []

    def read_from_stream(self, stream: IO[str]) -> list[str]:
        """
        Read available lines from a stream.

        Reads all currently available lines from the stream without blocking.
        Useful for reading from stdout or pipes.

        Args:
            stream: File-like object (stdout, pipe, etc.).

        Returns:
            List of log lines read from stream.
        """
        lines = []
        try:
            while True:
                line = stream.readline()
                if not line:
                    break
                if line.strip():
                    lines.append(line.rstrip("\n"))
        except OSError:
            pass

        return lines

    def reset_position(self, file_path: str) -> None:
        """
        Reset file position tracking for a file.

        Next read_new_lines call will read from the beginning.

        Args:
            file_path: Path to the log file.
        """
        if file_path in self._file_positions:
            del self._file_positions[file_path]
