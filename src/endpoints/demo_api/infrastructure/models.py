"""
SQLAlchemy models for demo_api endpoint.

Contains database models that map to database tables.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.models.base import Base, TimestampMixin


class DemoItemModel(Base, TimestampMixin):
    """
    SQLAlchemy model for demo_items table.

    This model represents the database table structure for demo items.
    It includes an id, label, and created_at timestamp.
    """

    __tablename__ = "demo_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier for the demo item",
    )
    label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Text label for the demo item",
    )

    def __repr__(self) -> str:
        """
        Return string representation of DemoItemModel.

        Returns:
            String representation showing id and label.
        """
        return f"DemoItemModel(id={self.id}, label='{self.label}')"
