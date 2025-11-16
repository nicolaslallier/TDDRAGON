"""
Unit tests for shared validation exception classes.

These tests ensure that exception classes work correctly and provide
consistent error handling across all endpoints.
"""

import pytest

from src.shared.exceptions.validation_error import ValidationError


class TestValidationError:
    """Test suite for ValidationError exception."""

    @pytest.mark.unit
    def test_validation_error_raises_with_message(self) -> None:
        """Test that ValidationError raises with provided message."""
        # Arrange
        message = "Invalid input"

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError(message)

        assert str(exc_info.value) == message
        assert exc_info.value.message == message

    @pytest.mark.unit
    def test_validation_error_is_exception_subclass(self) -> None:
        """Test that ValidationError is a subclass of Exception."""
        # Assert
        assert issubclass(ValidationError, Exception)

    @pytest.mark.unit
    def test_validation_error_message_attribute(self) -> None:
        """Test that ValidationError has message attribute."""
        # Arrange
        message = "Test error message"

        # Act
        error = ValidationError(message)

        # Assert
        assert hasattr(error, "message")
        assert error.message == message
