"""create nginx logs time series tables

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
    """Create nginx_access_logs_ts and nginx_uptime_ts tables."""
    # Create nginx_access_logs_ts table
    op.create_table(
        "nginx_access_logs_ts",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
            comment="Unique identifier for the log entry",
        ),
        sa.Column(
            "timestamp_utc",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Timestamp when the request occurred (UTC)",
        ),
        sa.Column(
            "client_ip",
            sa.Text(),
            nullable=False,
            comment="IP address of the client",
        ),
        sa.Column(
            "http_method",
            sa.String(length=10),
            nullable=False,
            comment="HTTP method (GET, POST, etc.)",
        ),
        sa.Column(
            "request_uri",
            sa.Text(),
            nullable=False,
            comment="URI/path requested",
        ),
        sa.Column(
            "status_code",
            sa.Integer(),
            nullable=False,
            comment="HTTP status code",
        ),
        sa.Column(
            "response_time",
            sa.Numeric(precision=10, scale=3),
            nullable=False,
            server_default="0.0",
            comment="Response time in seconds",
        ),
        sa.Column(
            "user_agent",
            sa.Text(),
            nullable=True,
            comment="User agent string",
        ),
        sa.Column(
            "raw_line",
            sa.Text(),
            nullable=True,
            comment="Original log line (for debugging)",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_nginx_access_logs_ts_timestamp_utc",
        "nginx_access_logs_ts",
        ["timestamp_utc"],
        unique=False,
    )
    op.create_index(
        "ix_nginx_access_logs_ts_status_code",
        "nginx_access_logs_ts",
        ["status_code"],
        unique=False,
    )

    # Create nginx_uptime_ts table
    op.create_table(
        "nginx_uptime_ts",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
            comment="Unique identifier for the uptime record",
        ),
        sa.Column(
            "timestamp_utc",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Timestamp when the measurement was taken (UTC)",
        ),
        sa.Column(
            "status",
            sa.String(length=10),
            nullable=False,
            comment="Status value (UP or DOWN)",
        ),
        sa.Column(
            "source",
            sa.String(length=100),
            nullable=False,
            comment="Source of the measurement",
        ),
        sa.Column(
            "details",
            sa.Text(),
            nullable=True,
            comment="Optional details about the measurement",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_nginx_uptime_ts_timestamp_utc",
        "nginx_uptime_ts",
        ["timestamp_utc"],
        unique=False,
    )
    op.create_index(
        "ix_nginx_uptime_ts_status",
        "nginx_uptime_ts",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """Drop nginx_access_logs_ts and nginx_uptime_ts tables."""
    op.drop_index("ix_nginx_uptime_ts_status", table_name="nginx_uptime_ts")
    op.drop_index("ix_nginx_uptime_ts_timestamp_utc", table_name="nginx_uptime_ts")
    op.drop_table("nginx_uptime_ts")
    op.drop_index(
        "ix_nginx_access_logs_ts_status_code", table_name="nginx_access_logs_ts"
    )
    op.drop_index(
        "ix_nginx_access_logs_ts_timestamp_utc", table_name="nginx_access_logs_ts"
    )
    op.drop_table("nginx_access_logs_ts")
