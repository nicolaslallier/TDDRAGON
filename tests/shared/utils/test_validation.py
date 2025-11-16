"""
Unit tests for shared validation utilities.

These tests ensure that validation utilities work correctly and are
well-tested as they're used across all endpoints.
"""

import pytest
from src.shared.utils.validation import validate_email, validate_not_empty


class TestValidateEmail:
    """Test suite for validate_email function."""

    @pytest.mark.unit
    def test_valid_email_returns_true(self) -> None:
        """Test that valid email addresses return True."""
        # Arrange
        valid_emails = [
            "user@example.com",
            "test.user@example.co.uk",
            "user+tag@example.com",
            "user_name@example-domain.com",
        ]

        # Act & Assert
        for email in valid_emails:
            assert validate_email(email) is True

    @pytest.mark.unit
    def test_invalid_email_returns_false(self) -> None:
        """Test that invalid email addresses return False."""
        # Arrange
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@example",
            "user @example.com",
            "",
        ]

        # Act & Assert
        for email in invalid_emails:
            assert validate_email(email) is False

    @pytest.mark.unit
    def test_none_email_returns_false(self) -> None:
        """Test that None email returns False."""
        # Arrange
        email = None

        # Act & Assert
        assert validate_email(email) is False  # type: ignore[arg-type]

    @pytest.mark.unit
    @pytest.mark.parametrize("email,expected", [
        ("user@example.com", True),
        ("invalid", False),
        ("", False),
        ("test@domain.co.uk", True),
    ])
    def test_various_emails_return_expected_result(
        self, email: str, expected: bool
    ) -> None:
        """Test various email formats return expected results."""
        assert validate_email(email) == expected


class TestValidateNotEmpty:
    """Test suite for validate_not_empty function."""

    @pytest.mark.unit
    def test_non_empty_string_returns_true(self) -> None:
        """Test that non-empty strings return True."""
        # Arrange
        value = "hello"

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is True

    @pytest.mark.unit
    def test_empty_string_returns_false(self) -> None:
        """Test that empty strings return False."""
        # Arrange
        value = ""

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is False

    @pytest.mark.unit
    def test_whitespace_only_string_returns_false(self) -> None:
        """Test that whitespace-only strings return False."""
        # Arrange
        value = "   "

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is False

    @pytest.mark.unit
    def test_empty_list_returns_false(self) -> None:
        """Test that empty lists return False."""
        # Arrange
        value: list[str] = []

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is False

    @pytest.mark.unit
    def test_non_empty_list_returns_true(self) -> None:
        """Test that non-empty lists return True."""
        # Arrange
        value = [1, 2, 3]

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is True

    @pytest.mark.unit
    def test_empty_dict_returns_false(self) -> None:
        """Test that empty dictionaries return False."""
        # Arrange
        value: dict[str, str] = {}

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is False

    @pytest.mark.unit
    def test_non_empty_dict_returns_true(self) -> None:
        """Test that non-empty dictionaries return True."""
        # Arrange
        value = {"key": "value"}

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is True

    @pytest.mark.unit
    def test_none_returns_false(self) -> None:
        """Test that None returns False."""
        # Arrange
        value = None

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is False

    @pytest.mark.unit
    def test_zero_returns_true(self) -> None:
        """Test that zero (int) returns True."""
        # Arrange
        value = 0

        # Act
        result = validate_not_empty(value)

        # Assert
        assert result is True

