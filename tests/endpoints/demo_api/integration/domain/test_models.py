"""
Integration tests for domain models.

Tests DemoItem domain model with real data integration.
"""

from datetime import datetime

import pytest

from src.endpoints.demo_api.domain.models import DemoItem


class TestDemoItemIntegration:
    """Integration test suite for DemoItem domain model."""

    @pytest.mark.integration
    def test_demo_item_with_none_label_raises_value_error(self):
        """Test that DemoItem raises ValueError when label is None."""
        # Arrange
        none_label = None

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            DemoItem(id=1, label=none_label, created_at=datetime.now())  # Line 37

    @pytest.mark.integration
    def test_demo_item_equality_with_non_demo_item_returns_false(self):
        """Test that DemoItem.__eq__ returns False when comparing with non-DemoItem."""
        # Arrange
        item = DemoItem(id=1, label="Test", created_at=datetime.now())
        other_object = "not a DemoItem"

        # Act & Assert
        assert item != other_object  # Line 56 should return False
