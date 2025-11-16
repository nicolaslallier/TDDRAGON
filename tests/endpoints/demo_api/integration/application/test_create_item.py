"""
Integration tests for CreateItem use case.

Tests the CreateItem use case with real repository integration.
"""

import pytest

from src.endpoints.demo_api.application.create_item import CreateItem
from src.endpoints.demo_api.infrastructure.repositories import (
    SQLAlchemyDemoItemRepository,
)


class TestCreateItemIntegration:
    """Integration test suite for CreateItem use case."""

    @pytest.mark.integration
    def test_create_item_with_none_label_raises_value_error(self, test_session):
        """Test that CreateItem raises ValueError when label is None."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)
        use_case = CreateItem(repository=repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            use_case.execute(None)  # This should trigger line 46

    @pytest.mark.integration
    def test_create_item_with_whitespace_label_raises_value_error(self, test_session):
        """Test that CreateItem raises ValueError when label is whitespace-only."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)
        use_case = CreateItem(repository=repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            use_case.execute("   ")
