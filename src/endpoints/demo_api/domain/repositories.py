"""
Repository interfaces for demo_api endpoint.

Defines the contracts for data access operations. Implementations
are provided in the infrastructure layer.
"""

from typing import Protocol

from src.endpoints.demo_api.domain.models import DemoItem


class DemoItemRepository(Protocol):
    """
    Repository interface for DemoItem persistence operations.

    This protocol defines the contract for storing and retrieving
    DemoItem entities. Implementations should be provided in the
    infrastructure layer.
    """

    def create(self, label: str) -> DemoItem:
        """
        Create a new DemoItem.

        Args:
            label: Text label for the new item.

        Returns:
            Created DemoItem instance with generated id.

        Raises:
            ValueError: If label is invalid.
        """
        ...  # pragma: no cover

    def find_all(self) -> list[DemoItem]:
        """
        Find all DemoItems.

        Returns:
            List of all DemoItem instances, ordered by creation date.
        """
        ...  # pragma: no cover
