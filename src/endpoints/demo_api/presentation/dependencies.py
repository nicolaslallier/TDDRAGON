"""
FastAPI dependencies for demo_api endpoint.

Provides dependency injection for repository and use cases.
"""


from fastapi import Depends
from sqlalchemy.orm import Session

from src.endpoints.demo_api.application.create_item import CreateItem
from src.endpoints.demo_api.application.list_items import ListItems
from src.endpoints.demo_api.domain.repositories import DemoItemRepository
from src.endpoints.demo_api.infrastructure.repositories import (
    SQLAlchemyDemoItemRepository,
)
from src.shared.infrastructure.database import get_session


def get_repository(
    session: Session = Depends(get_session),
) -> DemoItemRepository:
    """
    Get DemoItemRepository instance.

    Creates a repository instance with the current database session.
    This is used as a FastAPI dependency.

    Args:
        session: Database session from dependency injection.

    Returns:
        DemoItemRepository implementation instance.
    """
    return SQLAlchemyDemoItemRepository(session)


def get_create_item_use_case(
    repository: DemoItemRepository = Depends(get_repository),
) -> CreateItem:
    """
    Get CreateItem use case instance.

    Creates a CreateItem use case with the repository dependency.

    Args:
        repository: Repository instance from dependency injection.

    Returns:
        CreateItem use case instance.
    """
    return CreateItem(repository=repository)


def get_list_items_use_case(
    repository: DemoItemRepository = Depends(get_repository),
) -> ListItems:
    """
    Get ListItems use case instance.

    Creates a ListItems use case with the repository dependency.

    Args:
        repository: Repository instance from dependency injection.

    Returns:
        ListItems use case instance.
    """
    return ListItems(repository=repository)
