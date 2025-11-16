"""
Base SQLAlchemy model.

Provides a base class for all database models with common functionality.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    This class provides common functionality and metadata for all database
    models. It uses SQLAlchemy 2.0 style declarative base.
    """

    pass


class TimestampMixin:
    """
    Mixin class providing created_at timestamp.

    This mixin can be added to any model to automatically track when
    records are created. The created_at field is automatically set
    when a record is inserted.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created",
    )
