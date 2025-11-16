"""create demo_items table

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create demo_items table."""
    op.create_table(
        "demo_items",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
            comment="Unique identifier for the demo item",
        ),
        sa.Column(
            "label",
            sa.String(length=255),
            nullable=False,
            comment="Text label for the demo item",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Timestamp when the record was created",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop demo_items table."""
    op.drop_table("demo_items")
