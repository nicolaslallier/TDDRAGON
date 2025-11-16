"""
Shared logging infrastructure.

Common logging utilities used across all endpoints for consistent logging.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger instance with consistent configuration.

    This function creates and configures a logger instance that can be
    used across all endpoints. It ensures consistent logging format and
    behavior throughout the application.

    Args:
        name: Logger name, typically __name__ of the calling module.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               If None, defaults to INFO.

    Returns:
        Configured logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)

    # Set level if provided, otherwise use INFO
    if level is None:
        level = logging.INFO
    logger.setLevel(level)

    # Avoid adding multiple handlers if logger already configured
    if logger.handlers:
        return logger

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger
