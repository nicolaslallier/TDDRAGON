"""
Regression tests for validation utilities.

Ensures that validation functions continue to work correctly.
"""

import pytest

from src.shared.utils.validation import validate_email, validate_not_empty


class TestValidationRegression:
    """Regression tests for validation utilities."""

    @pytest.mark.regression
    def test_validate_email_with_valid_emails(self):
        """Test that validate_email returns True for valid emails."""
        # Act & Assert
        assert validate_email("user@example.com") is True
        assert validate_email("test.user+tag@example.co.uk") is True
        assert validate_email("user123@test-domain.com") is True

    @pytest.mark.regression
    def test_validate_email_with_invalid_emails(self):
        """Test that validate_email returns False for invalid emails."""
        # Act & Assert
        assert validate_email("invalid-email") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("") is False
        assert validate_email(None) is False

    @pytest.mark.regression
    def test_validate_not_empty_with_none_returns_false(self):
        """Test that validate_not_empty returns False for None."""
        # Act & Assert
        assert validate_not_empty(None) is False  # Line 59

    @pytest.mark.regression
    def test_validate_not_empty_with_empty_string_returns_false(self):
        """Test that validate_not_empty returns False for empty string."""
        # Act & Assert
        assert validate_not_empty("") is False
        assert validate_not_empty("   ") is False

    @pytest.mark.regression
    def test_validate_not_empty_with_empty_collections_returns_false(self):
        """Test that validate_not_empty returns False for empty collections."""
        # Act & Assert
        assert validate_not_empty([]) is False  # Line 63
        assert validate_not_empty({}) is False  # Line 63

    @pytest.mark.regression
    def test_validate_not_empty_with_valid_values_returns_true(self):
        """Test that validate_not_empty returns True for valid values."""
        # Act & Assert
        assert validate_not_empty("hello") is True
        assert validate_not_empty([1, 2, 3]) is True
        assert validate_not_empty({"key": "value"}) is True
        assert validate_not_empty(0) is True
        assert validate_not_empty(False) is True
