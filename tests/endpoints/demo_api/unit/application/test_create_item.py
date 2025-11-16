"""
Unit tests for CreateItem use case.

Tests for the CreateItem use case that handles creating new demo items.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.endpoints.demo_api.application.create_item import CreateItem
from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.domain.repositories import DemoItemRepository


class TestCreateItem:
    """Test suite for CreateItem use case."""

    def test_create_item_with_valid_label_returns_demo_item(self):
        """Test that creating an item with valid label returns DemoItem."""
        # Arrange
        label = "Test Item"
        mock_repository = Mock(spec=DemoItemRepository)
        created_item = DemoItem(id=1, label=label, created_at=datetime.now())
        mock_repository.create.return_value = created_item

        use_case = CreateItem(repository=mock_repository)

        # Act
        result = use_case.execute(label=label)

        # Assert
        assert result == created_item
        mock_repository.create.assert_called_once_with(label)

    def test_create_item_with_empty_label_raises_value_error(self):
        """Test that creating an item with empty label raises ValueError."""
        # Arrange
        empty_label = ""
        mock_repository = Mock(spec=DemoItemRepository)
        use_case = CreateItem(repository=mock_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            use_case.execute(label=empty_label)

        mock_repository.create.assert_not_called()

    def test_create_item_with_whitespace_label_raises_value_error(self):
        """Test that creating an item with whitespace-only label raises ValueError."""
        # Arrange
        whitespace_label = "   "
        mock_repository = Mock(spec=DemoItemRepository)
        use_case = CreateItem(repository=mock_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            use_case.execute(label=whitespace_label)

        mock_repository.create.assert_not_called()

    def test_create_item_trims_label_whitespace(self):
        """Test that label whitespace is trimmed before creating item."""
        # Arrange
        label_with_whitespace = "  Test Item  "
        trimmed_label = "Test Item"
        mock_repository = Mock(spec=DemoItemRepository)
        created_item = DemoItem(id=1, label=trimmed_label, created_at=datetime.now())
        mock_repository.create.return_value = created_item

        use_case = CreateItem(repository=mock_repository)

        # Act
        result = use_case.execute(label=label_with_whitespace)

        # Assert
        assert result == created_item
        mock_repository.create.assert_called_once_with(trimmed_label)
