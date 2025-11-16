"""
ListItems use case.

Handles the business logic for retrieving all demo items.
"""

from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.domain.repositories import DemoItemRepository


class ListItems:
    """
    Use case for listing all demo items.

    This use case handles the business logic for retrieving all demo items
    from the repository.
    """

    def __init__(self, repository: DemoItemRepository) -> None:
        """
        Initialize ListItems use case.

        Args:
            repository: Repository for retrieving demo items.
        """
        self._repository = repository

    def execute(self) -> list[DemoItem]:
        """
        Execute the list items use case.

        Retrieves all demo items from the repository.

        Returns:
            List of all DemoItem instances, ordered by creation date.
        """
        return self._repository.find_all()
