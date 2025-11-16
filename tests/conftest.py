"""
Pytest configuration and shared fixtures.

This file contains fixtures and configuration that are available to all tests.
"""

import pytest
from typing import Generator
from src.shared.infrastructure.logger import get_logger


@pytest.fixture
def logger() -> Generator:
    """
    Provide a logger instance for tests.

    This fixture creates a logger instance that can be used in tests
    that need logging functionality.

    Yields:
        Logger instance configured for testing.
    """
    logger_instance = get_logger("test", level=10)  # DEBUG level
    yield logger_instance


@pytest.fixture
def sample_email_valid() -> str:
    """
    Provide a valid email address for testing.

    Returns:
        Valid email address string.
    """
    return "test@example.com"


@pytest.fixture
def sample_email_invalid() -> str:
    """
    Provide an invalid email address for testing.

    Returns:
        Invalid email address string.
    """
    return "invalid-email"


@pytest.fixture
def sample_data_dict() -> dict[str, str]:
    """
    Provide sample dictionary data for testing.

    Returns:
        Dictionary with sample key-value pairs.
    """
    return {
        "name": "Test User",
        "email": "test@example.com",
        "status": "active",
    }

