"""
Integration tests for logger and validation utilities.

These tests verify that logging infrastructure works correctly with
validation utilities, demonstrating cross-component integration.
"""

import logging
from io import StringIO

import pytest

from src.shared.exceptions.validation_error import ValidationError
from src.shared.infrastructure.logger import get_logger
from src.shared.utils.validation import validate_email


class TestLoggerAndValidationIntegration:
    """Integration tests for logger and validation components."""

    @pytest.mark.integration
    def test_logger_logs_validation_success(self) -> None:
        """
        Test that logger can log validation success events.

        This integration test verifies that logging and validation
        components work together correctly.
        """
        # Arrange
        logger = get_logger(__name__)
        test_output = StringIO()
        handler = logging.StreamHandler(test_output)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        email = "test@example.com"

        # Act
        is_valid = validate_email(email)
        if is_valid:
            logger.info(f"Email validation successful: {email}")

        # Assert
        assert is_valid is True
        output = test_output.getvalue()
        assert "Email validation successful" in output
        assert email in output

    @pytest.mark.integration
    def test_logger_logs_validation_failure(self) -> None:
        """
        Test that logger can log validation failure events.

        This integration test verifies that logging works correctly
        when validation fails and exceptions are raised.
        """
        # Arrange
        logger = get_logger(__name__)
        test_output = StringIO()
        handler = logging.StreamHandler(test_output)
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        email = "invalid-email"

        # Act
        is_valid = validate_email(email)
        if not is_valid:
            error_msg = f"Email validation failed: {email}"
            logger.error(error_msg)
            # Simulate raising exception after logging
            with pytest.raises(ValidationError):
                raise ValidationError(error_msg)

        # Assert
        assert is_valid is False
        output = test_output.getvalue()
        assert "Email validation failed" in output
        assert email in output

    @pytest.mark.integration
    def test_logger_integration_with_validation_workflow(self) -> None:
        """
        Test complete workflow with logger and validation.

        This integration test simulates a real-world scenario where
        validation and logging are used together in a workflow.
        """
        # Arrange
        logger = get_logger(__name__)
        test_output = StringIO()
        handler = logging.StreamHandler(test_output)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        emails = ["valid@example.com", "invalid", "another@test.com"]

        # Act - Process emails with logging
        results = []
        for email in emails:
            logger.info(f"Validating email: {email}")
            is_valid = validate_email(email)
            if is_valid:
                logger.info(f"Email {email} is valid")
                results.append({"email": email, "valid": True})
            else:
                logger.warning(f"Email {email} is invalid")
                results.append({"email": email, "valid": False})

        # Assert
        assert len(results) == 3
        assert results[0]["valid"] is True
        assert results[1]["valid"] is False
        assert results[2]["valid"] is True

        output = test_output.getvalue()
        assert "Validating email" in output
        assert "is valid" in output
        assert "is invalid" in output
