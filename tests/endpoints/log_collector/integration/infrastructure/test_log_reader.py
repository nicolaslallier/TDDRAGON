"""
Integration tests for LogReader.

Tests the LogReader with actual files and streams.
"""

import tempfile
from io import StringIO
from pathlib import Path

import pytest

from src.endpoints.log_collector.infrastructure.log_reader import LogReader


class TestLogReaderIntegration:
    """Integration test suite for LogReader."""

    @pytest.mark.integration
    def test_read_from_file_reads_all_lines(self):
        """Test that read_from_file reads all lines from a file."""
        # Arrange
        reader = LogReader()
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
            '192.168.1.3 - - [16/Nov/2024:10:00:02 +0000] "GET /demo-items HTTP/1.1" 200 789 "-" "Mozilla/5.0"',
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            for line in log_lines:
                f.write(line + "\n")
            file_path = f.name

        try:
            # Act
            result = reader.read_from_file(file_path)

            # Assert
            assert len(result) == 3
            assert result[0] == log_lines[0]
            assert result[1] == log_lines[1]
            assert result[2] == log_lines[2]
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.integration
    def test_read_from_file_with_nonexistent_file_returns_empty_list(self):
        """Test that read_from_file returns empty list for nonexistent file."""
        # Arrange
        reader = LogReader()
        nonexistent_path = "/tmp/nonexistent_file_12345.log"

        # Act
        result = reader.read_from_file(nonexistent_path)

        # Assert
        assert result == []

    @pytest.mark.integration
    def test_read_new_lines_tracks_position(self):
        """Test that read_new_lines tracks file position correctly."""
        # Arrange
        reader = LogReader()
        initial_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]
        new_lines = [
            '192.168.1.3 - - [16/Nov/2024:10:00:02 +0000] "GET /demo-items HTTP/1.1" 200 789 "-" "Mozilla/5.0"',
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            for line in initial_lines:
                f.write(line + "\n")
            file_path = f.name

        try:
            # Act - Read initial lines
            result1 = reader.read_new_lines(file_path)
            assert len(result1) == 2

            # Append new lines
            with open(file_path, "a", encoding="utf-8") as f:
                for line in new_lines:
                    f.write(line + "\n")

            # Read new lines only
            result2 = reader.read_new_lines(file_path)

            # Assert
            assert len(result2) == 1
            assert result2[0] == new_lines[0]
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.integration
    def test_read_new_lines_with_nonexistent_file_returns_empty_list(self):
        """Test that read_new_lines returns empty list for nonexistent file."""
        # Arrange
        reader = LogReader()
        nonexistent_path = "/tmp/nonexistent_file_12345.log"

        # Act
        result = reader.read_new_lines(nonexistent_path)

        # Assert
        assert result == []

    @pytest.mark.integration
    def test_read_from_stream_reads_all_lines(self):
        """Test that read_from_stream reads all lines from a stream."""
        # Arrange
        reader = LogReader()
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
            '192.168.1.3 - - [16/Nov/2024:10:00:02 +0000] "GET /demo-items HTTP/1.1" 200 789 "-" "Mozilla/5.0"',
        ]
        stream = StringIO("\n".join(log_lines) + "\n")

        # Act
        result = reader.read_from_stream(stream)

        # Assert
        assert len(result) == 3
        assert result[0] == log_lines[0]
        assert result[1] == log_lines[1]
        assert result[2] == log_lines[2]

    @pytest.mark.integration
    def test_read_from_stream_with_empty_stream_returns_empty_list(self):
        """Test that read_from_stream returns empty list for empty stream."""
        # Arrange
        reader = LogReader()
        stream = StringIO("")

        # Act
        result = reader.read_from_stream(stream)

        # Assert
        assert result == []

    @pytest.mark.integration
    def test_reset_position_resets_file_position(self):
        """Test that reset_position resets file position tracking."""
        # Arrange
        reader = LogReader()
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            for line in log_lines:
                f.write(line + "\n")
            file_path = f.name

        try:
            # Act - Read initial lines
            result1 = reader.read_new_lines(file_path)
            assert len(result1) == 2

            # Reset position
            reader.reset_position(file_path)

            # Read again - should read from beginning
            result2 = reader.read_new_lines(file_path)

            # Assert
            assert len(result2) == 2
            assert result2[0] == log_lines[0]
            assert result2[1] == log_lines[1]
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.integration
    def test_read_from_file_skips_empty_lines(self):
        """Test that read_from_file skips empty lines."""
        # Arrange
        reader = LogReader()
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            "",
            "   ",
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            for line in log_lines:
                f.write(line + "\n")
            file_path = f.name

        try:
            # Act
            result = reader.read_from_file(file_path)

            # Assert - Should only return non-empty lines
            assert len(result) == 2
            assert result[0] == log_lines[0]
            assert result[1] == log_lines[3]
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.integration
    def test_read_from_file_handles_io_error(self):
        """Test that read_from_file handles IOError gracefully."""
        # Arrange
        from unittest.mock import patch

        reader = LogReader()

        # Create a file that exists but raises IOError when opened
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("test line\n")
            temp_path = f.name

        try:
            # Mock open to raise IOError when called
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                # Act
                result = reader.read_from_file(temp_path)

                # Assert
                assert result == []
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.integration
    def test_read_new_lines_handles_io_error(self):
        """Test that read_new_lines handles IOError gracefully."""
        # Arrange
        from unittest.mock import patch

        reader = LogReader()

        # Create a file that exists but raises IOError when opened
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("test line\n")
            temp_path = f.name

        try:
            # Mock open to raise IOError when called
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                # Act
                result = reader.read_new_lines(temp_path)

                # Assert
                assert result == []
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.integration
    def test_read_from_stream_handles_io_error(self):
        """Test that read_from_stream handles IOError gracefully."""
        # Arrange
        from unittest.mock import Mock

        reader = LogReader()
        stream = Mock()
        stream.readline.side_effect = OSError("Stream error")

        # Act
        result = reader.read_from_stream(stream)

        # Assert
        assert result == []
