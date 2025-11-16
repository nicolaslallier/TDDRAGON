"""
Shared validation exception classes.

Common exception classes used across all endpoints for validation errors.
"""


class ValidationError(Exception):
    """
    Exception raised when validation fails.

    This exception is used across all endpoints to indicate that input
    validation has failed. It provides a clear error message to help
    identify what validation rule was violated.

    Args:
        message: Error message describing the validation failure.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize ValidationError.

        Args:
            message: Error message describing the validation failure.
        """
        super().__init__(message)
        self.message = message

