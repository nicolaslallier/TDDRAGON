"""
Unit tests for ListItems use case.

Tests for the ListItems use case that handles retrieving all demo items.
"""

from datetime import datetime
from unittest.mock import Mock

from src.endpoints.demo_api.application.list_items import ListItems
from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.domain.repositories import DemoItemRepository


class TestListItems:
    """Test suite for ListItems use case."""

    def test_list_items_returns_all_items_from_repository(self):
        """Test that listing items returns all items from repository."""
        # Arrange
        mock_repository = Mock(spec=DemoItemRepository)
        items = [
            DemoItem(id=1, label="Item 1", created_at=datetime.now()),
            DemoItem(id=2, label="Item 2", created_at=datetime.now()),
        ]
        mock_repository.find_all.return_value = items

        use_case = ListItems(repository=mock_repository)

        # Act
        result = use_case.execute()

        # Assert
        assert result == items
        mock_repository.find_all.assert_called_once()

    def test_list_items_with_empty_repository_returns_empty_list(self):
        """Test that listing items when repository is empty returns empty list."""
        # Arrange
        mock_repository = Mock(spec=DemoItemRepository)
        mock_repository.find_all.return_value = []

        use_case = ListItems(repository=mock_repository)

        # Act
        result = use_case.execute()

        # Assert
        assert result == []
        mock_repository.find_all.assert_called_once()
