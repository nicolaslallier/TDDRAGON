"""
Unit tests for LogReader.

Tests for reading logs from files and streams.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from src.endpoints.log_collector.infrastructure.log_reader import LogReader


class TestLogReader:
    """Test suite for LogReader."""

    def test_read_from_file_reads_all_lines(self):
        """Test that reading from file reads all lines."""
        # Arrange
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("\n".join(log_lines))
            log_file = f.name

        reader = LogReader()

        try:
            # Act
            lines = reader.read_from_file(log_file)

            # Assert
            assert len(lines) == 2
            assert log_lines[0] in lines
            assert log_lines[1] in lines
        finally:
            Path(log_file).unlink()

    def test_read_from_file_with_nonexistent_file_returns_empty_list(self):
        """Test that reading from nonexistent file returns empty list."""
        # Arrange
        reader = LogReader()
        nonexistent_file = "/nonexistent/path/to/file.log"

        # Act
        lines = reader.read_from_file(nonexistent_file)

        # Assert
        assert lines == []

    def test_read_new_lines_tracks_position(self):
        """Test that read_new_lines only returns new lines since last read."""
        # Arrange
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write(log_lines[0] + "\n")
            log_file = f.name

        reader = LogReader()

        try:
            # Act - First read
            lines1 = reader.read_new_lines(log_file)

            # Append new line
            with open(log_file, "a") as f:
                f.write(log_lines[1] + "\n")

            # Act - Second read
            lines2 = reader.read_new_lines(log_file)

            # Assert
            assert len(lines1) == 1
            assert len(lines2) == 1
            assert log_lines[0] in lines1
            assert log_lines[1] in lines2
        finally:
            Path(log_file).unlink()

    def test_read_from_stream_reads_lines(self):
        """Test that reading from stream reads lines."""
        # Arrange
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]
        mock_stream = Mock()
        mock_stream.readline.side_effect = [line + "\n" for line in log_lines] + [""]

        reader = LogReader()

        # Act
        lines = reader.read_from_stream(mock_stream)

        # Assert
        assert len(lines) == 2
        assert log_lines[0] in lines
        assert log_lines[1] in lines
