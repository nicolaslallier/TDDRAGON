"""
Regression tests for shared exception classes.

Ensures that exception classes continue to work correctly after changes.
"""

import pytest

from src.shared.exceptions.validation_error import ValidationError


class TestValidationErrorRegression:
    """Regression tests for ValidationError exception."""

    @pytest.mark.regression
    def test_validation_error_initializes_with_message(self):
        """Test that ValidationError.__init__ stores message correctly."""
        # Arrange
        message = "Test validation error"

        # Act
        error = ValidationError(message)

        # Assert
        assert error.message == message
        assert str(error) == message

    @pytest.mark.regression
    def test_validation_error_inherits_from_exception(self):
        """Test that ValidationError inherits from Exception."""
        # Arrange
        message = "Test validation error"

        # Act
        error = ValidationError(message)

        # Assert
        assert isinstance(error, Exception)
