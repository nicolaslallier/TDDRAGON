"""
Unit tests for domain models.

Tests for the DemoItem domain model and its behavior.
"""

from datetime import datetime

import pytest

from src.endpoints.demo_api.domain.models import DemoItem


class TestDemoItem:
    """Test suite for DemoItem domain model."""

    def test_create_demo_item_with_valid_data_returns_instance(self):
        """Test that creating a DemoItem with valid data returns an instance."""
        # Arrange
        label = "Test Item"

        # Act
        item = DemoItem(id=1, label=label, created_at=datetime.now())

        # Assert
        assert item.id == 1
        assert item.label == label
        assert isinstance(item.created_at, datetime)

    def test_create_demo_item_with_empty_label_raises_error(self):
        """Test that creating a DemoItem with empty label raises ValueError."""
        # Arrange
        empty_label = ""

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            DemoItem(id=1, label=empty_label, created_at=datetime.now())

    def test_create_demo_item_with_none_label_raises_error(self):
        """Test that creating a DemoItem with None label raises ValueError."""
        # Arrange
        none_label = None

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            DemoItem(id=1, label=none_label, created_at=datetime.now())

    def test_create_demo_item_with_whitespace_label_raises_error(self):
        """Test that creating a DemoItem with whitespace-only label raises ValueError."""
        # Arrange
        whitespace_label = "   "

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            DemoItem(id=1, label=whitespace_label, created_at=datetime.now())

    def test_demo_item_equality(self):
        """Test that two DemoItems with same id are equal."""
        # Arrange
        item1 = DemoItem(id=1, label="Item 1", created_at=datetime.now())
        item2 = DemoItem(id=1, label="Item 2", created_at=datetime.now())

        # Act & Assert
        assert item1 == item2

    def test_demo_item_inequality(self):
        """Test that two DemoItems with different ids are not equal."""
        # Arrange
        item1 = DemoItem(id=1, label="Item", created_at=datetime.now())
        item2 = DemoItem(id=2, label="Item", created_at=datetime.now())

        # Act & Assert
        assert item1 != item2

    def test_demo_item_equality_with_non_demo_item_returns_false(self):
        """Test that comparing DemoItem with non-DemoItem object returns False."""
        # Arrange
        item = DemoItem(id=1, label="Item", created_at=datetime.now())
        other_object = "not a DemoItem"

        # Act & Assert
        assert item != other_object
        assert item != other_object

    def test_demo_item_repr_returns_string_representation(self):
        """Test that __repr__ returns a string representation of DemoItem."""
        # Arrange
        item = DemoItem(id=1, label="Test Item", created_at=datetime.now())

        # Act
        repr_str = repr(item)

        # Assert
        assert isinstance(repr_str, str)
        assert "DemoItem" in repr_str
        assert "id=1" in repr_str
        assert "label='Test Item'" in repr_str
