"""
Regression tests for demo_api presentation layer.

Ensures that presentation components continue to work correctly after changes.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.presentation.dependencies import (
    get_create_item_use_case,
    get_list_items_use_case,
    get_repository,
)
from src.endpoints.demo_api.presentation.routes import _to_response


class TestDependenciesRegression:
    """Regression tests for FastAPI dependencies."""

    @pytest.mark.regression
    def test_get_repository_returns_sqlalchemy_repository(self):
        """Test that get_repository returns SQLAlchemyDemoItemRepository instance."""
        # Arrange
        from src.endpoints.demo_api.infrastructure.repositories import (
            SQLAlchemyDemoItemRepository,
        )

        mock_session = Mock()

        # Act
        repository = get_repository(session=mock_session)

        # Assert
        assert repository is not None
        assert isinstance(repository, SQLAlchemyDemoItemRepository)
        assert hasattr(repository, "create")
        assert hasattr(repository, "find_all")

    @pytest.mark.regression
    def test_get_create_item_use_case_returns_create_item_instance(self):
        """Test that get_create_item_use_case returns CreateItem instance."""
        # Arrange
        mock_repository = Mock()

        # Act
        use_case = get_create_item_use_case(repository=mock_repository)

        # Assert
        assert use_case is not None
        assert hasattr(use_case, "execute")

    @pytest.mark.regression
    def test_get_list_items_use_case_returns_list_items_instance(self):
        """Test that get_list_items_use_case returns ListItems instance."""
        # Arrange
        mock_repository = Mock()

        # Act
        use_case = get_list_items_use_case(repository=mock_repository)

        # Assert
        assert use_case is not None
        assert hasattr(use_case, "execute")


class TestRoutesRegression:
    """Regression tests for FastAPI routes."""

    @pytest.mark.regression
    def test_to_response_converts_domain_model_to_schema(self):
        """Test that _to_response converts DemoItem to DemoItemResponse."""
        # Arrange
        item = DemoItem(id=1, label="Test", created_at=datetime.now())

        # Act
        response = _to_response(item)

        # Assert
        assert response.id == 1
        assert response.label == "Test"
        assert response.created_at == item.created_at

    @pytest.mark.regression
    def test_create_demo_item_route_handles_value_error(self):
        """Test that create_demo_item route handles ValueError."""
        # Arrange
        from unittest.mock import Mock

        from fastapi import HTTPException

        from src.endpoints.demo_api.presentation.routes import create_demo_item
        from src.endpoints.demo_api.presentation.schemas import CreateDemoItemRequest

        mock_use_case = Mock()
        mock_use_case.execute.side_effect = ValueError("Label cannot be empty")

        request = CreateDemoItemRequest(label="Valid Label")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_demo_item(request=request, use_case=mock_use_case)

        assert exc_info.value.status_code == 400
        assert "Label cannot be empty" in str(exc_info.value.detail)

    @pytest.mark.regression
    def test_create_demo_item_route_returns_created_item(self):
        """Test that create_demo_item route returns created item."""
        # Arrange
        from unittest.mock import Mock

        from src.endpoints.demo_api.presentation.routes import create_demo_item
        from src.endpoints.demo_api.presentation.schemas import CreateDemoItemRequest

        mock_item = DemoItem(id=1, label="Test Item", created_at=datetime.now())
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_item

        request = CreateDemoItemRequest(label="Test Item")

        # Act
        result = create_demo_item(request=request, use_case=mock_use_case)

        # Assert
        assert result.id == 1
        assert result.label == "Test Item"

    @pytest.mark.regression
    def test_list_demo_items_route_returns_items(self):
        """Test that list_demo_items route returns list of items."""
        # Arrange
        from unittest.mock import Mock

        from src.endpoints.demo_api.domain.models import DemoItem
        from src.endpoints.demo_api.presentation.routes import list_demo_items

        mock_items = [
            DemoItem(id=1, label="Item 1", created_at=datetime.now()),
            DemoItem(id=2, label="Item 2", created_at=datetime.now()),
        ]
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_items

        # Act
        result = list_demo_items(use_case=mock_use_case)

        # Assert
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2


class TestHealthRegression:
    """Regression tests for health endpoint."""

    @pytest.mark.regression
    def test_health_check_route_exists(self):
        """Test that health_check route handler exists."""
        # Arrange
        from src.endpoints.demo_api.presentation.health import health_check

        # Assert
        assert health_check is not None
        assert callable(health_check)

    @pytest.mark.regression
    def test_health_check_with_database_connection(self):
        """Test that health_check tests database connection."""
        # Arrange
        import os

        from src.endpoints.demo_api.presentation.health import health_check
        from src.shared.infrastructure.database import get_session, init_database

        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        init_database("sqlite:///:memory:")

        try:
            session_gen = get_session()
            session = next(session_gen)

            # Act
            result = health_check(session=session)

            # Assert
            assert result.status == "UP"
            assert result.database == "connected"
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_health_check_handles_database_error(self):
        """Test that health_check handles database connection errors."""
        # Arrange
        from unittest.mock import Mock

        from src.endpoints.demo_api.presentation.health import health_check

        mock_session = Mock()
        mock_session.execute.side_effect = Exception("Database error")

        # Act
        result = health_check(session=mock_session)

        # Assert
        assert result.status == "DOWN"
        assert result.database == "disconnected"
