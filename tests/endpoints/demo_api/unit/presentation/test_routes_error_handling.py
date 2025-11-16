"""
Unit tests for routes error handling.

Tests error handling paths in the routes.
"""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException, status

from src.endpoints.demo_api.presentation.routes import create_demo_item


class TestRoutesErrorHandling:
    """Test suite for routes error handling."""

    @pytest.mark.unit
    def test_create_demo_item_with_value_error_raises_http_exception(self):
        """Test that creating item with ValueError raises HTTPException."""
        # Arrange
        from src.endpoints.demo_api.presentation.schemas import CreateDemoItemRequest

        mock_use_case = Mock()
        mock_use_case.execute.side_effect = ValueError("Label cannot be empty")
        # Use valid label to pass Pydantic validation, but use_case will raise ValueError
        request = CreateDemoItemRequest(label="valid")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_demo_item(request=request, use_case=mock_use_case)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Label cannot be empty" in str(exc_info.value.detail)
