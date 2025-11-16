"""
Integration tests for FastAPI routes.

Tests the API routes with a test database.
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


class TestDemoItemsRoutes:
    """Integration test suite for demo items routes."""

    @pytest.mark.integration
    def test_create_demo_item_returns_201(self, client):
        """Test that creating a demo item returns 201 Created."""
        # Arrange
        payload = {"label": "Test Item"}

        # Act
        response = client.post("/demo-items", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["label"] == "Test Item"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.integration
    def test_create_demo_item_with_empty_label_returns_422(self, client):
        """Test that creating an item with empty label returns 422 Unprocessable Entity."""
        # Arrange
        payload = {"label": ""}

        # Act
        response = client.post("/demo-items", json=payload)

        # Assert
        # FastAPI/Pydantic returns 422 for validation errors
        assert response.status_code == 422

    @pytest.mark.integration
    def test_list_demo_items_returns_200(self, client):
        """Test that listing demo items returns 200 OK."""
        # Arrange
        # Create some items first
        client.post("/demo-items", json={"label": "Item 1"})
        client.post("/demo-items", json={"label": "Item 2"})

        # Act
        response = client.get("/demo-items")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["label"] == "Item 1"
        assert data[1]["label"] == "Item 2"

    @pytest.mark.integration
    def test_list_demo_items_when_empty_returns_empty_list(self, client):
        """Test that listing items when none exist returns empty list."""
        # Act
        response = client.get("/demo-items")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == []
