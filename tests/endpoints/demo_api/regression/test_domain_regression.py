"""
Regression tests for domain models.

Ensures that domain models continue to work correctly after changes.
"""

from datetime import datetime

import pytest

from src.endpoints.demo_api.domain.models import DemoItem


class TestDemoItemRegression:
    """Regression tests for DemoItem domain model."""

    @pytest.mark.regression
    def test_demo_item_init_with_valid_data(self):
        """Test that DemoItem initializes correctly with valid data."""
        # Arrange
        label = "Test Item"
        created_at = datetime.now()

        # Act
        item = DemoItem(id=1, label=label, created_at=created_at)

        # Assert
        assert item.id == 1
        assert item.label == label  # Line 40
        assert item.created_at == created_at

    @pytest.mark.regression
    def test_demo_item_init_trims_whitespace(self):
        """Test that DemoItem trims whitespace from label."""
        # Arrange
        label = "  Test Item  "
        created_at = datetime.now()

        # Act
        item = DemoItem(id=1, label=label, created_at=created_at)

        # Assert
        assert item.label == "Test Item"  # Line 40

    @pytest.mark.regression
    def test_demo_item_init_with_empty_label_raises_error(self):
        """Test that DemoItem raises ValueError for empty label."""
        # Arrange
        empty_label = ""

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            DemoItem(id=1, label=empty_label, created_at=datetime.now())  # Line 36-37

    @pytest.mark.regression
    def test_demo_item_init_with_none_label_raises_error(self):
        """Test that DemoItem raises ValueError for None label."""
        # Arrange
        none_label = None

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            DemoItem(id=1, label=none_label, created_at=datetime.now())  # Line 36-37

    @pytest.mark.regression
    def test_demo_item_equality_with_same_id(self):
        """Test that DemoItem equality compares by id."""
        # Arrange
        item1 = DemoItem(id=1, label="Item 1", created_at=datetime.now())
        item2 = DemoItem(id=1, label="Item 2", created_at=datetime.now())

        # Act & Assert
        assert item1 == item2  # Line 57

    @pytest.mark.regression
    def test_demo_item_equality_with_different_id(self):
        """Test that DemoItem inequality compares by id."""
        # Arrange
        item1 = DemoItem(id=1, label="Item", created_at=datetime.now())
        item2 = DemoItem(id=2, label="Item", created_at=datetime.now())

        # Act & Assert
        assert item1 != item2

    @pytest.mark.regression
    def test_demo_item_equality_with_non_demo_item(self):
        """Test that DemoItem equality returns False for non-DemoItem."""
        # Arrange
        item = DemoItem(id=1, label="Item", created_at=datetime.now())
        other = "not a DemoItem"

        # Act & Assert
        assert item != other  # Line 55-56
        assert item != other
