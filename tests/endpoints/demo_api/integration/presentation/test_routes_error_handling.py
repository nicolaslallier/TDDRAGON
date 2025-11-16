"""
Integration tests for error handling in routes.

Tests error handling and edge cases in API routes.
"""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.endpoints.demo_api.application.create_item import CreateItem
from src.endpoints.demo_api.presentation.dependencies import get_create_item_use_case


@pytest.fixture
def client(test_app):
    """Provide a test client for the FastAPI app."""
    return TestClient(test_app)


class TestRoutesErrorHandling:
    """Test suite for error handling in routes."""

    @pytest.mark.integration
    def test_create_demo_item_with_value_error_from_use_case_returns_400(
        self, test_app, client
    ):
        """Test that ValueError from use case is converted to HTTP 400."""
        # Arrange
        # Create a mock use case that raises ValueError
        mock_use_case = MagicMock(spec=CreateItem)
        mock_use_case.execute = MagicMock(
            side_effect=ValueError("Label cannot be empty")
        )

        def mock_get_create_item_use_case():
            return mock_use_case

        # Override the dependency
        test_app.dependency_overrides[
            get_create_item_use_case
        ] = mock_get_create_item_use_case

        try:
            # Act
            response = client.post("/demo-items", json={"label": "test"})

            # Assert
            assert response.status_code == 400
            assert "Label cannot be empty" in response.json()["detail"]
        finally:
            # Cleanup: remove the override
            test_app.dependency_overrides.pop(get_create_item_use_case, None)
