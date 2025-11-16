"""
Regression tests for shared exceptions.

Ensures that exception classes continue to work correctly.
"""

import pytest

from src.shared.exceptions.validation_error import ValidationError


class TestValidationErrorRegression:
    """Regression tests for ValidationError exception."""

    @pytest.mark.regression
    def test_validation_error_init_sets_message(self):
        """Test that ValidationError.__init__ sets message correctly."""
        # Arrange
        message = "Validation failed"

        # Act
        error = ValidationError(message)

        # Assert
        assert error.message == message  # Line 27-28
        assert str(error) == message

    @pytest.mark.regression
    def test_validation_error_can_be_raised(self):
        """Test that ValidationError can be raised and caught."""
        # Arrange
        message = "Test validation error"

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError(message)

        assert exc_info.value.message == message  # Line 27-28
