"""
Unit tests for shared logging infrastructure.

These tests ensure that logging utilities work correctly and provide
consistent logging behavior across all endpoints.
"""

import logging
import sys
from io import StringIO

import pytest
from src.shared.infrastructure.logger import get_logger


class TestGetLogger:
    """Test suite for get_logger function."""

    @pytest.mark.unit
    def test_get_logger_returns_logger_instance(self) -> None:
        """Test that get_logger returns a logger instance."""
        # Act
        logger = get_logger(__name__)

        # Assert
        assert isinstance(logger, logging.Logger)

    @pytest.mark.unit
    def test_logger_has_correct_name(self) -> None:
        """Test that logger has the correct name."""
        # Arrange
        name = "test_module"

        # Act
        logger = get_logger(name)

        # Assert
        assert logger.name == name

    @pytest.mark.unit
    def test_logger_logs_info_message(self) -> None:
        """Test that logger can log info messages."""
        # Arrange
        logger = get_logger(__name__)
        test_output = StringIO()
        handler = logging.StreamHandler(test_output)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Act
        logger.info("Test message")

        # Assert
        output = test_output.getvalue()
        assert "Test message" in output

    @pytest.mark.unit
    def test_get_logger_with_custom_level(self) -> None:
        """Test that get_logger accepts custom log level."""
        # Arrange
        level = logging.DEBUG

        # Act
        logger = get_logger(__name__, level=level)

        # Assert
        assert logger.level == level

    @pytest.mark.unit
    def test_get_logger_defaults_to_info_level(self) -> None:
        """Test that get_logger defaults to INFO level."""
        # Act
        logger = get_logger(__name__)

        # Assert
        assert logger.level == logging.INFO

    @pytest.mark.unit
    def test_multiple_calls_return_same_logger(self) -> None:
        """Test that multiple calls with same name return same logger."""
        # Arrange
        name = "test_module"

        # Act
        logger1 = get_logger(name)
        logger2 = get_logger(name)

        # Assert
        assert logger1 is logger2

