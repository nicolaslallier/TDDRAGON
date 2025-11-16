"""
Repository implementations for demo_api endpoint.

Contains SQLAlchemy-based implementations of repository interfaces.
"""

from typing import cast

from sqlalchemy.orm import Session

from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.infrastructure.models import DemoItemModel


class SQLAlchemyDemoItemRepository:
    """
    SQLAlchemy implementation of DemoItemRepository.

    This repository uses SQLAlchemy to persist and retrieve DemoItem
    entities from the database.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize SQLAlchemyDemoItemRepository.

        Args:
            session: SQLAlchemy database session.
        """
        self._session = session

    def create(self, label: str) -> DemoItem:
        """
        Create a new DemoItem in the database.

        Args:
            label: Text label for the new item.

        Returns:
            Created DemoItem domain model with generated id.

        Raises:
            ValueError: If label is invalid.
        """
        if not label or not label.strip():
            raise ValueError("Label cannot be empty")

        db_model = DemoItemModel(label=label.strip())
        self._session.add(db_model)
        self._session.flush()  # Get the generated id
        self._session.commit()  # Commit to make data visible to other sessions

        return self._to_domain_model(db_model)

    def find_all(self) -> list[DemoItem]:
        """
        Find all DemoItems from the database.

        Returns:
            List of all DemoItem domain models, ordered by creation date.
        """
        db_models = (
            self._session.query(DemoItemModel)
            .order_by(DemoItemModel.created_at.asc())
            .all()
        )

        return [self._to_domain_model(model) for model in db_models]

    def _to_domain_model(self, db_model: DemoItemModel) -> DemoItem:
        """
        Convert database model to domain model.

        Args:
            db_model: SQLAlchemy model instance.

        Returns:
            Domain model instance.
        """
        return DemoItem(
            id=cast(int, db_model.id),
            label=db_model.label,
            created_at=db_model.created_at,
        )


# Type alias for convenience
DemoItemRepositoryImpl = SQLAlchemyDemoItemRepository
