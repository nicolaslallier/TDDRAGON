"""
Regression tests for infrastructure layer.

Ensures that repository implementations continue to work correctly.
"""

from datetime import datetime

import pytest

from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.infrastructure.models import DemoItemModel
from src.endpoints.demo_api.infrastructure.repositories import (
    SQLAlchemyDemoItemRepository,
)


class TestSQLAlchemyDemoItemRepositoryRegression:
    """Regression tests for SQLAlchemyDemoItemRepository."""

    @pytest.mark.regression
    def test_repository_init_stores_session(self, test_session):
        """Test that repository stores session correctly."""
        # Arrange & Act
        repository = SQLAlchemyDemoItemRepository(test_session)

        # Assert
        assert repository._session is test_session  # Line 31

    @pytest.mark.regression
    def test_repository_create_with_valid_label(self, test_session):
        """Test that create method persists item to database."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)
        label = "Test Item"

        # Act
        result = repository.create(label)

        # Assert
        assert result.id is not None
        assert result.label == label
        assert isinstance(result.created_at, datetime)
        # Verify database persistence (lines 49-52)
        test_session.commit()
        db_item = test_session.query(DemoItemModel).filter_by(id=result.id).first()
        assert db_item is not None
        assert db_item.label == label

    @pytest.mark.regression
    def test_repository_create_with_empty_label_raises_error(self, test_session):
        """Test that create raises ValueError for empty label."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            repository.create("")  # Line 46-47

    @pytest.mark.regression
    def test_repository_find_all_returns_all_items(self, test_session):
        """Test that find_all returns all items ordered by created_at."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)
        item1 = repository.create("Item 1")
        test_session.commit()
        item2 = repository.create("Item 2")
        test_session.commit()

        # Act
        items = repository.find_all()

        # Assert
        assert len(items) == 2
        assert items[0].id == item1.id  # Ordered by created_at (lines 63-67)
        assert items[1].id == item2.id

    @pytest.mark.regression
    def test_repository_to_domain_model_conversion(self, test_session):
        """Test that _to_domain_model converts correctly."""
        # Arrange
        repository = SQLAlchemyDemoItemRepository(test_session)
        db_model = DemoItemModel(label="Test")
        test_session.add(db_model)
        test_session.flush()

        # Act
        domain_model = repository._to_domain_model(db_model)

        # Assert
        assert isinstance(domain_model, DemoItem)
        assert domain_model.id == db_model.id  # Line 81-85
        assert domain_model.label == db_model.label
        assert domain_model.created_at == db_model.created_at
