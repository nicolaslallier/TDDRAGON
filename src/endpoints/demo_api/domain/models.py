"""
Domain models for demo_api endpoint.

Contains the core domain entities and value objects.
"""

from datetime import datetime
from typing import Any


class DemoItem:
    """
    Domain model representing a demo item.

    This is a pure domain object that represents a demo item in the system.
    It contains business logic and validation rules.

    Attributes:
        id: Unique identifier for the item.
        label: Text label for the item. Must not be empty.
        created_at: Timestamp when the item was created.
    """

    def __init__(self, id: int, label: str, created_at: datetime) -> None:
        """
        Initialize a DemoItem.

        Args:
            id: Unique identifier for the item.
            label: Text label for the item. Must not be empty.
            created_at: Timestamp when the item was created.

        Raises:
            ValueError: If label is None, empty, or whitespace-only.
        """
        if not label or not label.strip():
            raise ValueError("Label cannot be empty")

        self.id = id
        self.label = label.strip()
        self.created_at = created_at

    def __eq__(self, other: Any) -> bool:
        """
        Compare two DemoItems for equality.

        Two DemoItems are considered equal if they have the same id.

        Args:
            other: Object to compare with.

        Returns:
            True if both items have the same id, False otherwise.
        """
        if not isinstance(other, DemoItem):
            return False
        return self.id == other.id

    def __repr__(self) -> str:
        """
        Return string representation of DemoItem.

        Returns:
            String representation showing id and label.
        """
        return f"DemoItem(id={self.id}, label='{self.label}')"
