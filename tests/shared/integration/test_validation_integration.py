"""
Integration tests for validation utilities.

Tests validation functions with various edge cases and integration scenarios.
"""

import pytest

from src.shared.utils.validation import validate_email, validate_not_empty


class TestValidationIntegration:
    """Integration test suite for validation utilities."""

    @pytest.mark.integration
    def test_validate_email_with_none_returns_false(self):
        """Test that validate_email returns False when email is None."""
        # Act
        result = validate_email(None)

        # Assert
        assert result is False  # Line 32

    @pytest.mark.integration
    def test_validate_email_with_non_string_returns_false(self):
        """Test that validate_email returns False when email is not a string."""
        # Act
        result = validate_email(12345)

        # Assert
        assert result is False  # Line 32

    @pytest.mark.integration
    def test_validate_not_empty_with_none_returns_false(self):
        """Test that validate_not_empty returns False when value is None."""
        # Act
        result = validate_not_empty(None)

        # Assert
        assert result is False  # Line 59

    @pytest.mark.integration
    def test_validate_not_empty_with_empty_string_returns_false(self):
        """Test that validate_not_empty returns False when string is empty."""
        # Act
        result = validate_not_empty("")

        # Assert
        assert result is False  # Line 61

    @pytest.mark.integration
    def test_validate_not_empty_with_whitespace_string_returns_false(self):
        """Test that validate_not_empty returns False when string is whitespace-only."""
        # Act
        result = validate_not_empty("   ")

        # Assert
        assert result is False  # Line 61

    @pytest.mark.integration
    def test_validate_not_empty_with_empty_list_returns_false(self):
        """Test that validate_not_empty returns False when list is empty."""
        # Act
        result = validate_not_empty([])

        # Assert
        assert result is False  # Line 63

    @pytest.mark.integration
    def test_validate_not_empty_with_empty_dict_returns_false(self):
        """Test that validate_not_empty returns False when dict is empty."""
        # Act
        result = validate_not_empty({})

        # Assert
        assert result is False  # Line 63

    @pytest.mark.integration
    def test_validate_not_empty_with_valid_values_returns_true(self):
        """Test that validate_not_empty returns True for valid values."""
        # Act & Assert
        assert validate_not_empty("hello") is True
        assert validate_not_empty([1, 2, 3]) is True
        assert validate_not_empty({"key": "value"}) is True
        assert validate_not_empty(0) is True  # 0 is not empty
        assert validate_not_empty(False) is True  # False is not empty

    @pytest.mark.integration
    def test_validate_email_with_valid_email_returns_true(self):
        """Test that validate_email returns True for valid email addresses."""
        # Act & Assert - These should trigger lines 33-34
        assert validate_email("user@example.com") is True
        assert validate_email("test.user+tag@example.co.uk") is True
        assert validate_email("user123@test-domain.com") is True
