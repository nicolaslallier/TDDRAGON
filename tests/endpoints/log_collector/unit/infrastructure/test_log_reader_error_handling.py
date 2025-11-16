"""
Unit tests for LogReader error handling.

Tests error handling paths in log_reader.py.
"""

from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_collector.infrastructure.log_reader import LogReader


class TestLogReaderErrorHandling:
    """Test suite for LogReader error handling."""

    @pytest.mark.unit
    def test_read_from_file_with_io_error_returns_empty_list(self):
        """Test that read_from_file returns empty list on IOError."""
        # Arrange
        import tempfile
        from pathlib import Path

        reader = LogReader()

        # Create a temporary file that exists
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".log"
        ) as tmp_file:
            tmp_file.write("test line\n")
            tmp_path = tmp_file.name

        try:
            # Act - Patch open to raise IOError (line 41-42)
            # The exception will be caught by the except block
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                result = reader.read_from_file(tmp_path)

            # Assert - Exception handler should return empty list
            assert result == []
        finally:
            # Cleanup
            Path(tmp_path).unlink(missing_ok=True)

    @pytest.mark.unit
    def test_read_from_file_with_os_error_returns_empty_list(self):
        """Test that read_from_file returns empty list on OSError."""
        # Arrange
        import tempfile
        from pathlib import Path

        reader = LogReader()

        # Create a temporary file that exists
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".log"
        ) as tmp_file:
            tmp_file.write("test line\n")
            tmp_path = tmp_file.name

        try:
            # Act - Patch open to raise OSError (line 41-42)
            # The exception will be caught by the except block
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                result = reader.read_from_file(tmp_path)

            # Assert - Exception handler should return empty list
            assert result == []
        finally:
            # Cleanup
            Path(tmp_path).unlink(missing_ok=True)

    @pytest.mark.unit
    def test_read_new_lines_with_nonexistent_file_returns_empty_list(self):
        """Test that read_new_lines returns empty list for nonexistent file."""
        # Arrange
        reader = LogReader()
        nonexistent_file = "/nonexistent/path/to/file.log"

        # Act
        result = reader.read_new_lines(nonexistent_file)

        # Assert
        assert result == []

    @pytest.mark.unit
    def test_read_new_lines_with_io_error_returns_empty_list(self):
        """Test that read_new_lines returns empty list on IOError."""
        # Arrange
        import tempfile
        from pathlib import Path

        reader = LogReader()

        # Create a temporary file that exists
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".log"
        ) as tmp_file:
            tmp_file.write("test line\n")
            tmp_path = tmp_file.name

        try:
            # Act - Patch open to raise IOError (line 78-79)
            # The exception will be caught by the except block
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                result = reader.read_new_lines(tmp_path)

            # Assert - Exception handler should return empty list
            assert result == []
        finally:
            # Cleanup
            Path(tmp_path).unlink(missing_ok=True)

    @pytest.mark.unit
    def test_read_new_lines_with_os_error_returns_empty_list(self):
        """Test that read_new_lines returns empty list on OSError."""
        # Arrange
        import tempfile
        from pathlib import Path

        reader = LogReader()

        # Create a temporary file that exists
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".log"
        ) as tmp_file:
            tmp_file.write("test line\n")
            tmp_path = tmp_file.name

        try:
            # Act - Patch open to raise OSError (line 78-79)
            # The exception will be caught by the except block
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                result = reader.read_new_lines(tmp_path)

            # Assert - Exception handler should return empty list
            assert result == []
        finally:
            # Cleanup
            Path(tmp_path).unlink(missing_ok=True)

    @pytest.mark.unit
    def test_read_from_stream_with_io_error_returns_empty_list(self):
        """Test that read_from_stream returns empty list on IOError."""
        # Arrange
        reader = LogReader()
        mock_stream = Mock()
        mock_stream.readline.side_effect = OSError("Stream error")

        # Act
        result = reader.read_from_stream(mock_stream)

        # Assert
        assert result == []

    @pytest.mark.unit
    def test_reset_position_removes_file_from_tracking(self):
        """Test that reset_position removes file from position tracking."""
        # Arrange
        reader = LogReader()
        file_path = "/some/file.log"
        reader._file_positions[file_path] = 100

        # Act
        reader.reset_position(file_path)

        # Assert
        assert file_path not in reader._file_positions
