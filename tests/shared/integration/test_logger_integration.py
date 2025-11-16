"""
Integration tests for logger infrastructure.

Tests logger behavior in integration scenarios.
"""

import pytest

from src.shared.infrastructure.logger import get_logger


class TestLoggerIntegration:
    """Integration test suite for logger infrastructure."""

    @pytest.mark.integration
    def test_get_logger_returns_existing_logger_with_handlers(self):
        """Test that get_logger returns existing logger if handlers already exist."""
        # Arrange
        logger_name = "test_logger_integration"
        logger1 = get_logger(logger_name)

        # Act - Get logger again (should return early at line 41)
        logger2 = get_logger(logger_name)

        # Assert
        assert logger1 is logger2
        assert len(logger1.handlers) > 0
        # Verify it didn't add duplicate handlers
        handler_count = len(logger1.handlers)
        logger3 = get_logger(logger_name)
        assert len(logger3.handlers) == handler_count  # No new handlers added
