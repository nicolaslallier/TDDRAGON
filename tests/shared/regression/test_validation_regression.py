"""
Regression tests for validation utilities.

These tests ensure that previously fixed bugs in validation utilities
do not reoccur. Each test documents a specific bug that was fixed.
"""

import pytest

from src.shared.utils.validation import validate_email, validate_not_empty


class TestValidationRegression:
    """Regression tests for validation utilities."""

    @pytest.mark.regression
    def test_email_validation_handles_none_correctly(self) -> None:
        """
        Regression test: Ensure None values are handled correctly.

        Bug: Previously, None values could cause AttributeError.
        Fix: Added None check before string operations.
        """
        # Arrange
        email = None

        # Act
        result = validate_email(email)  # type: ignore[arg-type]

        # Assert
        assert result is False
        # Should not raise AttributeError or TypeError

    @pytest.mark.regression
    def test_email_validation_handles_empty_string(self) -> None:
        """
        Regression test: Ensure empty strings return False.

        Bug: Previously, empty strings could return True.
        Fix: Added explicit empty string check.
        """
        # Arrange
        email = ""

        # Act
        result = validate_email(email)

        # Assert
        assert result is False

    @pytest.mark.regression
    def test_validate_not_empty_handles_whitespace_strings(self) -> None:
        """
        Regression test: Ensure whitespace-only strings return False.

        Bug: Previously, strings with only whitespace returned True.
        Fix: Added strip() check for strings.
        """
        # Arrange
        value = "   \t\n   "

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is False

    @pytest.mark.regression
    def test_validate_not_empty_handles_zero_correctly(self) -> None:
        """
        Regression test: Ensure zero (int) is considered not empty.

        Bug: Previously, zero could be incorrectly treated as empty.
        Fix: Zero is a valid value and should return True.
        """
        # Arrange
        value = 0

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is True

    @pytest.mark.regression
    def test_email_validation_handles_special_characters(self) -> None:
        """
        Regression test: Ensure special characters in email are handled.

        Bug: Previously, emails with + or _ could fail validation.
        Fix: Updated regex pattern to include all valid email characters.
        """
        # Arrange
        valid_emails = [
            "user+tag@example.com",
            "user_name@example.com",
            "user.name@example.com",
            "user-name@example.com",
        ]

        # Act & Assert
        for email in valid_emails:
            result = validate_email(email)
            assert result is True, f"Email {email} should be valid"

    @pytest.mark.regression
    def test_validate_not_empty_handles_false_boolean(self) -> None:
        """
        Regression test: Ensure False boolean is considered not empty.

        Bug: Previously, False could be incorrectly treated as empty.
        Fix: False is a valid value and should return True.
        """
        # Arrange
        value = False

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is True

    @pytest.mark.regression
    def test_validate_not_empty_handles_none(self) -> None:
        """
        Regression test: Ensure None returns False.

        Bug: Previously, None could cause errors.
        Fix: Added explicit None check.
        """
        # Arrange
        value = None

        # Act
        result = validate_not_empty(value)  # type: ignore[arg-type]

        # Assert
        assert result is False

    @pytest.mark.regression
    def test_validate_not_empty_handles_empty_list(self) -> None:
        """
        Regression test: Ensure empty list returns False.

        Bug: Previously, empty lists could return True.
        Fix: Added explicit empty list check.
        """
        # Arrange
        value = []

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is False

    @pytest.mark.regression
    def test_validate_not_empty_handles_empty_dict(self) -> None:
        """
        Regression test: Ensure empty dict returns False.

        Bug: Previously, empty dicts could return True.
        Fix: Added explicit empty dict check.
        """
        # Arrange
        value = {}

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is False
