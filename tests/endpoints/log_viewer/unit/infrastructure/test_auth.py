"""
Unit tests for MockAuthService.
"""

from unittest.mock import Mock

import pytest
from fastapi import Request

from src.endpoints.log_viewer.infrastructure.auth import MockAuthService


class TestMockAuthService:
    """Test suite for MockAuthService."""

    @pytest.mark.unit
    def test_authenticate_with_valid_credentials_returns_true(self):
        """Test that authenticate returns True for valid credentials."""
        # Act
        result = MockAuthService.authenticate("admin", "admin123")

        # Assert
        assert result is True

    @pytest.mark.unit
    def test_authenticate_with_invalid_username_returns_false(self):
        """Test that authenticate returns False for invalid username."""
        # Act
        result = MockAuthService.authenticate("invalid", "admin123")

        # Assert
        assert result is False

    @pytest.mark.unit
    def test_authenticate_with_invalid_password_returns_false(self):
        """Test that authenticate returns False for invalid password."""
        # Act
        result = MockAuthService.authenticate("admin", "wrong")

        # Assert
        assert result is False

    @pytest.mark.unit
    def test_is_authenticated_returns_false_when_not_logged_in(self):
        """Test that is_authenticated returns False when not logged in."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.session = {}

        # Act
        result = MockAuthService.is_authenticated(mock_request)

        # Assert
        assert result is False

    @pytest.mark.unit
    def test_is_authenticated_returns_true_when_logged_in(self):
        """Test that is_authenticated returns True when logged in."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.session = {"authenticated": True}

        # Act
        result = MockAuthService.is_authenticated(mock_request)

        # Assert
        assert result is True

    @pytest.mark.unit
    def test_get_username_returns_username_when_authenticated(self):
        """Test that get_username returns username when authenticated."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.session = {"authenticated": True, "username": "admin"}

        # Act
        result = MockAuthService.get_username(mock_request)

        # Assert
        assert result == "admin"

    @pytest.mark.unit
    def test_get_username_returns_none_when_not_authenticated(self):
        """Test that get_username returns None when not authenticated."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.session = {}

        # Act
        result = MockAuthService.get_username(mock_request)

        # Assert
        assert result is None

    @pytest.mark.unit
    def test_login_sets_session_data(self):
        """Test that login sets session data."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.session = {}

        # Act
        MockAuthService.login(mock_request, "admin")

        # Assert
        assert mock_request.session["authenticated"] is True
        assert mock_request.session["username"] == "admin"

    @pytest.mark.unit
    def test_logout_clears_session(self):
        """Test that logout clears session."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.session = {"authenticated": True, "username": "admin"}

        # Act
        MockAuthService.logout(mock_request)

        # Assert
        assert len(mock_request.session) == 0

