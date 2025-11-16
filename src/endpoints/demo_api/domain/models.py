"""
Domain models for demo API.

Core business entities and domain logic.
"""

from datetime import datetime


class DemoItem:
    """
    Domain model representing a demo item.

    This is the core business entity for the demo API. It encapsulates
    the business rules and validation logic for demo items.

    Args:
        id: Unique identifier for the item.
        label: Text label for the item. Must not be empty.
        created_at: Timestamp when the item was created.

    Raises:
        ValueError: If label is empty, None, or whitespace-only.

    Example:
        >>> from datetime import datetime
        >>> item = DemoItem(id=1, label="My Item", created_at=datetime.now())
        >>> item.label
        'My Item'
    """

    def __init__(self, id: int, label: str, created_at: datetime) -> None:
        """
        Initialize DemoItem.

        Args:
            id: Unique identifier for the item.
            label: Text label for the item. Must not be empty.
            created_at: Timestamp when the item was created.

        Raises:
            ValueError: If label is empty, None, or whitespace-only.
        """
        if not label or not label.strip():
            raise ValueError("Label cannot be empty")

        self.id = id
        self.label = label
        self.created_at = created_at

    def __eq__(self, other: object) -> bool:
        """
        Compare two DemoItems for equality.

        Two DemoItems are considered equal if they have the same id.

        Args:
            other: Object to compare with.

        Returns:
            True if both are DemoItems with the same id, False otherwise.
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
