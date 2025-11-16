"""
Integration tests for repository implementations.

Tests the SQLAlchemy repository implementation against a real database.
"""

import time
from datetime import datetime

import pytest

from src.endpoints.demo_api.infrastructure.models import DemoItemModel
from src.endpoints.demo_api.infrastructure.repositories import (
    SQLAlchemyDemoItemRepository,
)


class TestSQLAlchemyDemoItemRepository:
    """Integration test suite for SQLAlchemyDemoItemRepository."""

    @pytest.mark.integration
    def test_create_item_persists_to_database(self, test_session):
        """Test that creating an item persists it to the database."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)
        label = "Test Item"

        # Act
        created_item = repository.create(label)

        # Assert
        assert created_item.id is not None
        assert created_item.label == label
        assert isinstance(created_item.created_at, datetime)

        # Verify it's actually in the database
        test_session.commit()
        db_item = (
            test_session.query(DemoItemModel).filter_by(id=created_item.id).first()
        )
        assert db_item is not None
        assert db_item.label == label

    @pytest.mark.integration
    def test_create_item_with_empty_label_raises_error(self, test_session):
        """Test that creating an item with empty label raises ValueError."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)
        empty_label = ""

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            repository.create(empty_label)

    @pytest.mark.integration
    def test_find_all_returns_all_items(self, test_session):
        """Test that find_all returns all items from database."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)
        item1 = repository.create("Item 1")
        item2 = repository.create("Item 2")
        test_session.commit()

        # Act
        items = repository.find_all()

        # Assert
        assert len(items) == 2
        assert item1 in items
        assert item2 in items

    @pytest.mark.integration
    def test_find_all_returns_empty_list_when_no_items(self, test_session):
        """Test that find_all returns empty list when database is empty."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)

        # Act
        items = repository.find_all()

        # Assert
        assert items == []

    @pytest.mark.integration
    def test_find_all_returns_items_ordered_by_created_at(self, test_session):
        """Test that find_all returns items ordered by creation date."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)
        item1 = repository.create("First Item")
        test_session.commit()

        time.sleep(0.01)  # Small delay to ensure different timestamps
        item2 = repository.create("Second Item")
        test_session.commit()

        # Act
        items = repository.find_all()

        # Assert
        assert len(items) == 2
        assert items[0].id == item1.id
        assert items[1].id == item2.id
        assert items[0].created_at <= items[1].created_at
