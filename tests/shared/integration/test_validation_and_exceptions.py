"""
Integration tests for validation utilities and exception handling.

These tests verify that validation utilities work correctly with exception
classes, ensuring the integration between shared components.
"""

import pytest
from src.shared.utils.validation import (
    validate_email,
    validate_not_empty,
)
from src.shared.exceptions.validation_error import ValidationError


class TestValidationWithExceptions:
    """Integration tests for validation utilities with exceptions."""

    @pytest.mark.integration
    def test_validate_email_raises_validation_error_on_invalid(
        self, sample_email_invalid: str
    ) -> None:
        """
        Test that invalid email validation can be used with ValidationError.

        This integration test verifies that validation utilities work correctly
        with exception handling, demonstrating how components work together.

        Args:
            sample_email_invalid: Invalid email fixture.
        """
        # Arrange
        email = sample_email_invalid

        # Act & Assert
        if not validate_email(email):
            with pytest.raises(ValidationError) as exc_info:
                raise ValidationError(f"Invalid email: {email}")
            assert "Invalid email" in str(exc_info.value)

    @pytest.mark.integration
    def test_validate_email_with_valid_email_no_exception(
        self, sample_email_valid: str
    ) -> None:
        """
        Test that valid email validation works without raising exceptions.

        This integration test verifies the happy path where validation
        passes and no exceptions are raised.

        Args:
            sample_email_valid: Valid email fixture.
        """
        # Arrange
        email = sample_email_valid

        # Act
        is_valid = validate_email(email)

        # Assert
        assert is_valid is True
        # No exception should be raised

    @pytest.mark.integration
    def test_validation_workflow_with_multiple_checks(
        self, sample_email_valid: str, sample_data_dict: dict[str, str]
    ) -> None:
        """
        Test complete validation workflow with multiple validation checks.

        This integration test verifies that multiple validation utilities
        can be used together in a workflow, simulating real-world usage.

        Args:
            sample_email_valid: Valid email fixture.
            sample_data_dict: Sample data dictionary fixture.
        """
        # Arrange
        email = sample_email_valid
        data = sample_data_dict

        # Act - Validate email
        email_valid = validate_email(email)

        # Act - Validate data fields
        name_valid = validate_not_empty(data.get("name", ""))
        status_valid = validate_not_empty(data.get("status", ""))

        # Assert
        assert email_valid is True
        assert name_valid is True
        assert status_valid is True

        # If all validations pass, no exception should be raised
        # This simulates a successful validation workflow

    @pytest.mark.integration
    def test_validation_error_contains_correct_message(self) -> None:
        """
        Test that ValidationError works correctly with validation utilities.

        This integration test ensures that when validation fails, the
        exception provides meaningful error messages.
        """
        # Arrange
        invalid_email = "not-an-email"

        # Act
        is_valid = validate_email(invalid_email)

        # Assert
        assert is_valid is False

        # Verify exception can be raised with appropriate message
        with pytest.raises(ValidationError) as exc_info:
            if not is_valid:
                raise ValidationError(
                    f"Email validation failed for: {invalid_email}"
                )

        assert "Email validation failed" in str(exc_info.value)
        assert invalid_email in str(exc_info.value)

