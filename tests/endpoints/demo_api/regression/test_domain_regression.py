"""
Regression tests for demo_api domain layer.

Ensures that domain models continue to work correctly after changes.
"""

from datetime import datetime

import pytest

from src.endpoints.demo_api.domain.models import DemoItem


class TestDemoItemRegression:
    """Regression tests for DemoItem domain model."""

    @pytest.mark.regression
    def test_demo_item_raises_error_for_empty_label(self):
        """Test that DemoItem raises ValueError for empty label."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            DemoItem(id=1, label="", created_at=datetime.now())

    @pytest.mark.regression
    def test_demo_item_raises_error_for_whitespace_label(self):
        """Test that DemoItem raises ValueError for whitespace-only label."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            DemoItem(id=1, label="   ", created_at=datetime.now())

    @pytest.mark.regression
    def test_demo_item_eq_returns_false_for_different_type(self):
        """Test that __eq__ returns False for different type."""
        # Arrange
        item = DemoItem(id=1, label="Test", created_at=datetime.now())

        # Act
        result = item.__eq__("not a DemoItem")

        # Assert
        assert result is False

    @pytest.mark.regression
    def test_demo_item_eq_returns_true_for_same_id(self):
        """Test that __eq__ returns True for same id."""
        # Arrange
        item1 = DemoItem(id=1, label="Test 1", created_at=datetime.now())
        item2 = DemoItem(id=1, label="Test 2", created_at=datetime.now())

        # Act
        result = item1 == item2

        # Assert
        assert result is True

    @pytest.mark.regression
    def test_demo_item_eq_returns_false_for_different_id(self):
        """Test that __eq__ returns False for different id."""
        # Arrange
        item1 = DemoItem(id=1, label="Test", created_at=datetime.now())
        item2 = DemoItem(id=2, label="Test", created_at=datetime.now())

        # Act
        result = item1 == item2

        # Assert
        assert result is False
