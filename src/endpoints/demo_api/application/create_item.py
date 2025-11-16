"""
CreateItem use case.

Handles the business logic for creating a new demo item.
"""

from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.domain.repositories import DemoItemRepository


class CreateItem:
    """
    Use case for creating a new demo item.

    This use case handles the business logic for creating a demo item,
    including validation and delegation to the repository.
    """

    def __init__(self, repository: DemoItemRepository) -> None:
        """
        Initialize CreateItem use case.

        Args:
            repository: Repository for persisting demo items.
        """
        self._repository = repository

    def execute(self, label: str) -> DemoItem:
        """
        Execute the create item use case.

        Creates a new demo item with the provided label. The label
        is validated and trimmed before creation.

        Args:
            label: Text label for the new item. Must not be empty
                   or whitespace-only.

        Returns:
            Created DemoItem instance with generated id.

        Raises:
            ValueError: If label is None, empty, or whitespace-only.
        """
        if not label or not label.strip():
            raise ValueError("Label cannot be empty")

        trimmed_label = label.strip()
        return self._repository.create(trimmed_label)
