"""
Regression tests for application layer use cases.

Ensures that use cases continue to work correctly after changes.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.endpoints.demo_api.application.create_item import CreateItem
from src.endpoints.demo_api.application.list_items import ListItems
from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.domain.repositories import DemoItemRepository


class TestCreateItemRegression:
    """Regression tests for CreateItem use case."""

    @pytest.mark.regression
    def test_create_item_initializes_with_repository(self):
        """Test that CreateItem.__init__ stores repository correctly."""
        # Arrange
        mock_repository = MagicMock(spec=DemoItemRepository)

        # Act
        use_case = CreateItem(repository=mock_repository)

        # Assert
        assert use_case._repository is mock_repository  # Line 26

    @pytest.mark.regression
    def test_create_item_execute_with_valid_label_returns_demo_item(self):
        """Test that execute method creates and returns DemoItem."""
        # Arrange
        mock_repository = MagicMock(spec=DemoItemRepository)
        mock_item = DemoItem(id=1, label="Test", created_at=datetime.now())
        mock_repository.create.return_value = mock_item
        use_case = CreateItem(repository=mock_repository)

        # Act
        result = use_case.execute("Test")

        # Assert
        assert result is mock_item
        mock_repository.create.assert_called_once_with("Test")  # Line 49

    @pytest.mark.regression
    def test_create_item_execute_trims_whitespace(self):
        """Test that execute method trims whitespace from label."""
        # Arrange
        mock_repository = MagicMock(spec=DemoItemRepository)
        mock_item = DemoItem(id=1, label="Test", created_at=datetime.now())
        mock_repository.create.return_value = mock_item
        use_case = CreateItem(repository=mock_repository)

        # Act
        use_case.execute("  Test  ")

        # Assert
        mock_repository.create.assert_called_once_with("Test")  # Line 48

    @pytest.mark.regression
    def test_create_item_execute_with_empty_label_raises_error(self):
        """Test that execute raises ValueError for empty label."""
        # Arrange
        mock_repository = MagicMock(spec=DemoItemRepository)
        use_case = CreateItem(repository=mock_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            use_case.execute("")  # Line 45-46

    @pytest.mark.regression
    def test_create_item_execute_with_none_label_raises_error(self):
        """Test that execute raises ValueError for None label."""
        # Arrange
        mock_repository = MagicMock(spec=DemoItemRepository)
        use_case = CreateItem(repository=mock_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            use_case.execute(None)  # Line 45-46


class TestListItemsRegression:
    """Regression tests for ListItems use case."""

    @pytest.mark.regression
    def test_list_items_initializes_with_repository(self):
        """Test that ListItems.__init__ stores repository correctly."""
        # Arrange
        mock_repository = MagicMock(spec=DemoItemRepository)

        # Act
        use_case = ListItems(repository=mock_repository)

        # Assert
        assert use_case._repository is mock_repository  # Line 26

    @pytest.mark.regression
    def test_list_items_execute_returns_repository_find_all(self):
        """Test that execute method calls repository.find_all."""
        # Arrange
        mock_repository = MagicMock(spec=DemoItemRepository)
        mock_items = [
            DemoItem(id=1, label="Item 1", created_at=datetime.now()),
            DemoItem(id=2, label="Item 2", created_at=datetime.now()),
        ]
        mock_repository.find_all.return_value = mock_items
        use_case = ListItems(repository=mock_repository)

        # Act
        result = use_case.execute()

        # Assert
        assert result is mock_items
        mock_repository.find_all.assert_called_once()  # Line 37
