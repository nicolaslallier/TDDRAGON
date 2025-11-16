"""
End-to-end tests for demo_api endpoint.

Tests the complete API functionality end-to-end.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(test_app):
    """
    Provide a test client for the FastAPI application.

    Args:
        test_app: FastAPI application fixture.

    Yields:
        TestClient instance.
    """
    return TestClient(test_app)


class TestDemoAPIE2E:
    """End-to-end test suite for demo API."""

    @pytest.mark.e2e
    def test_create_and_list_items_workflow(self, client):
        """Test complete workflow of creating and listing items."""
        # Arrange
        item1_label = "First Item"
        item2_label = "Second Item"

        # Act - Create items
        response1 = client.post("/demo-items", json={"label": item1_label})
        response2 = client.post("/demo-items", json={"label": item2_label})

        # Assert - Creation
        assert response1.status_code == 201
        assert response2.status_code == 201

        item1_data = response1.json()
        item2_data = response2.json()

        assert item1_data["label"] == item1_label
        assert item2_data["label"] == item2_label
        assert item1_data["id"] != item2_data["id"]

        # Act - List items
        list_response = client.get("/demo-items")

        # Assert - Listing
        assert list_response.status_code == 200
        items = list_response.json()
        assert len(items) == 2

        # Verify items are ordered by creation date
        assert items[0]["id"] == item1_data["id"]
        assert items[1]["id"] == item2_data["id"]

    @pytest.mark.e2e
    def test_health_check_returns_up(self, client):
        """Test that health check returns UP status."""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert data["database"] == "connected"
