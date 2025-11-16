"""
Regression tests for presentation layer.

Ensures that API routes, dependencies, and health checks continue to work correctly.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.presentation.dependencies import (
    get_create_item_use_case,
    get_list_items_use_case,
    get_repository,
)
from src.endpoints.demo_api.presentation.routes import _to_response


@pytest.fixture
def client(test_app):
    """Provide a test client for the FastAPI app."""
    return TestClient(test_app)


class TestDependenciesRegression:
    """Regression tests for FastAPI dependencies."""

    @pytest.mark.regression
    def test_get_repository_returns_sqlalchemy_repository(self, test_session):
        """Test that get_repository returns SQLAlchemyDemoItemRepository."""
        # Arrange & Act
        repository = get_repository(session=test_session)

        # Assert
        from src.endpoints.demo_api.infrastructure.repositories import (
            SQLAlchemyDemoItemRepository,
        )

        assert isinstance(repository, SQLAlchemyDemoItemRepository)  # Line 34

    @pytest.mark.regression
    def test_get_create_item_use_case_returns_create_item(self, test_session):
        """Test that get_create_item_use_case returns CreateItem instance."""
        # Arrange
        repository = get_repository(session=test_session)

        # Act
        use_case = get_create_item_use_case(repository=repository)

        # Assert
        from src.endpoints.demo_api.application.create_item import CreateItem

        assert isinstance(use_case, CreateItem)  # Line 51
        assert use_case._repository is repository

    @pytest.mark.regression
    def test_get_list_items_use_case_returns_list_items(self, test_session):
        """Test that get_list_items_use_case returns ListItems instance."""
        # Arrange
        repository = get_repository(session=test_session)

        # Act
        use_case = get_list_items_use_case(repository=repository)

        # Assert
        from src.endpoints.demo_api.application.list_items import ListItems

        assert isinstance(use_case, ListItems)  # Line 68
        assert use_case._repository is repository


class TestRoutesRegression:
    """Regression tests for API routes."""

    @pytest.mark.regression
    def test_to_response_converts_demo_item_to_response(self):
        """Test that _to_response converts DemoItem to DemoItemResponse."""
        # Arrange
        item = DemoItem(id=1, label="Test", created_at=datetime.now())

        # Act
        response = _to_response(item)

        # Assert
        assert response.id == 1  # Line 36-40
        assert response.label == "Test"
        assert response.created_at == item.created_at

    @pytest.mark.regression
    def test_create_demo_item_route_with_value_error_returns_400(
        self, test_app, client
    ):
        """Test that ValueError from use case returns 400."""
        # Arrange
        from src.endpoints.demo_api.application.create_item import CreateItem

        mock_use_case = MagicMock(spec=CreateItem)
        mock_use_case.execute = MagicMock(
            side_effect=ValueError("Label cannot be empty")
        )

        def mock_get_create_item_use_case():
            return mock_use_case

        test_app.dependency_overrides[
            get_create_item_use_case
        ] = mock_get_create_item_use_case

        try:
            # Act
            response = client.post("/demo-items", json={"label": "test"})

            # Assert
            assert response.status_code == 400  # Line 70-74
            assert "Label cannot be empty" in response.json()["detail"]
        finally:
            test_app.dependency_overrides.pop(get_create_item_use_case, None)

    @pytest.mark.regression
    def test_list_demo_items_route_converts_to_response_list(self, client):
        """Test that list route converts items to response list."""
        # Arrange
        client.post("/demo-items", json={"label": "Item 1"})
        client.post("/demo-items", json={"label": "Item 2"})

        # Act
        response = client.get("/demo-items")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("id" in item for item in data)  # Line 102-103
        assert all("label" in item for item in data)
        assert all("created_at" in item for item in data)


class TestHealthRegression:
    """Regression tests for health check endpoint."""

    @pytest.mark.regression
    def test_health_check_returns_status_and_database(self, client):
        """Test that health check returns status and database fields."""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "status" in data  # Line 41-52
        assert "database" in data
        assert data["status"] in ["UP", "DOWN"]
        assert data["database"] in ["connected", "disconnected"]

    @pytest.mark.regression
    def test_health_check_with_database_error_returns_down(self, test_app, client):
        """Test that health check returns DOWN when database fails."""
        # Arrange
        from sqlalchemy.orm import Session

        from src.shared.infrastructure.database import get_session

        mock_session = MagicMock(spec=Session)
        mock_session.execute = MagicMock(side_effect=Exception("Connection failed"))

        def mock_get_session():
            yield mock_session

        test_app.dependency_overrides[get_session] = mock_get_session

        try:
            # Act
            response = client.get("/health")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "DOWN"  # Line 47-48
            assert data["database"] == "disconnected"
        finally:
            test_app.dependency_overrides.pop(get_session, None)
