"""
Shared validation utilities.

These utilities are used across all endpoints for common validation tasks.
They are domain-agnostic and well-tested.
"""

import re
from typing import Any


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    This is a shared utility used by multiple endpoints for email validation.
    It implements a simple format check that all endpoints can rely on.

    Args:
        email: Email address string to validate.

    Returns:
        True if email format is valid, False otherwise.

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_not_empty(value: Any) -> bool:
    """
    Validate that a value is not empty.

    Checks if a value is not None, not an empty string, not an empty list,
    and not an empty dict.

    Args:
        value: Value to validate.

    Returns:
        True if value is not empty, False otherwise.

    Example:
        >>> validate_not_empty("hello")
        True
        >>> validate_not_empty("")
        False
        >>> validate_not_empty([])
        False
    """
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return not (isinstance(value, (list, dict)) and len(value) == 0)
