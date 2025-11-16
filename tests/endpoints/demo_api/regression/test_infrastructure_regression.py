"""
Regression tests for demo_api infrastructure layer.

Ensures that infrastructure components continue to work correctly after changes.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.infrastructure.repositories import (
    SQLAlchemyDemoItemRepository,
)


class TestSQLAlchemyDemoItemRepositoryRegression:
    """Regression tests for SQLAlchemyDemoItemRepository."""

    @pytest.mark.regression
    def test_sqlalchemy_demo_item_repository_initializes_with_session(self):
        """Test that SQLAlchemyDemoItemRepository.__init__ stores session correctly."""
        # Arrange
        mock_session = Mock()

        # Act
        repository = SQLAlchemyDemoItemRepository(session=mock_session)

        # Assert
        assert repository._session is mock_session

    @pytest.mark.regression
    def test_create_demo_item_converts_to_domain_model(self):
        """Test that create converts database model to domain model."""
        # Arrange
        from src.endpoints.demo_api.infrastructure.models import DemoItemModel

        mock_session = Mock()
        mock_db_model = Mock(spec=DemoItemModel)
        mock_db_model.id = 1
        mock_db_model.label = "Test"
        mock_db_model.created_at = datetime.now()
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.commit.return_value = None

        repository = SQLAlchemyDemoItemRepository(session=mock_session)

        # Mock _to_domain_model to return a DemoItem
        mock_item = DemoItem(id=1, label="Test", created_at=datetime.now())
        with patch.object(repository, "_to_domain_model", return_value=mock_item):
            # Act
            result = repository.create("Test")

            # Assert
            assert result is mock_item
            mock_session.add.assert_called_once()
            mock_session.flush.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.regression
    def test_create_demo_item_raises_error_for_empty_label(self):
        """Test that create raises ValueError for empty label."""
        # Arrange
        mock_session = Mock()
        repository = SQLAlchemyDemoItemRepository(session=mock_session)

        # Act & Assert
        with pytest.raises(ValueError, match="Label cannot be empty"):
            repository.create("")

    @pytest.mark.regression
    def test_find_all_calls_session_query(self):
        """Test that find_all calls session query correctly."""
        # Arrange
        from src.endpoints.demo_api.infrastructure.models import DemoItemModel

        mock_session = Mock()
        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_db_model = Mock(spec=DemoItemModel)
        mock_query.all.return_value = [mock_db_model]
        mock_session.query.return_value = mock_query

        repository = SQLAlchemyDemoItemRepository(session=mock_session)

        # Mock _to_domain_model to return a DemoItem
        mock_item = DemoItem(id=1, label="Test", created_at=datetime.now())
        with patch.object(repository, "_to_domain_model", return_value=mock_item):
            # Act
            result = repository.find_all()

            # Assert
            assert len(result) == 1
            mock_session.query.assert_called_once()

    @pytest.mark.regression
    def test_to_domain_model_converts_demo_item(self):
        """Test that _to_domain_model converts DemoItemModel to DemoItem."""
        # Arrange
        from src.endpoints.demo_api.infrastructure.models import DemoItemModel

        mock_session = Mock()
        repository = SQLAlchemyDemoItemRepository(session=mock_session)
        db_model = Mock(spec=DemoItemModel)
        db_model.id = 1
        db_model.label = "Test"
        db_model.created_at = datetime.now()

        # Act
        result = repository._to_domain_model(db_model)

        # Assert
        assert isinstance(result, DemoItem)
        assert result.id == 1
        assert result.label == "Test"
