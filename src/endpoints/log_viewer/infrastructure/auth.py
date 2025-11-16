"""
Mock authentication service for log viewer.

Provides placeholder authentication for v0.3.0.
"""

from typing import Optional

from fastapi import Request
from starlette.middleware.sessions import SessionMiddleware


class MockAuthService:
    """
    Mock authentication service.

    Provides simple session-based authentication for internal use.
    This is a placeholder implementation for v0.3.0.
    """

    # Mock user credentials (in production, this would be in a database)
    MOCK_USERS = {
        "admin": "admin123",
        "operator": "operator123",
        "viewer": "viewer123",
    }

    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        """
        Authenticate a user with username and password.

        Args:
            username: Username to authenticate.
            password: Password to verify.

        Returns:
            True if credentials are valid, False otherwise.
        """
        return (
            username in MockAuthService.MOCK_USERS
            and MockAuthService.MOCK_USERS[username] == password
        )

    @staticmethod
    def is_authenticated(request: Request) -> bool:
        """
        Check if the current request is authenticated.

        Args:
            request: FastAPI request object.

        Returns:
            True if user is authenticated, False otherwise.
        """
        session = request.session
        return session.get("authenticated", False)

    @staticmethod
    def get_username(request: Request) -> Optional[str]:
        """
        Get the username of the authenticated user.

        Args:
            request: FastAPI request object.

        Returns:
            Username if authenticated, None otherwise.
        """
        if MockAuthService.is_authenticated(request):
            return request.session.get("username")
        return None

    @staticmethod
    def login(request: Request, username: str) -> None:
        """
        Log in a user by setting session data.

        Args:
            request: FastAPI request object.
            username: Username to log in.
        """
        request.session["authenticated"] = True
        request.session["username"] = username

    @staticmethod
    def logout(request: Request) -> None:
        """
        Log out the current user by clearing session data.

        Args:
            request: FastAPI request object.
        """
        request.session.clear()

