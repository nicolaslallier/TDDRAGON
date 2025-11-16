"""
SQLAlchemy models for log_collector endpoint.

Contains database models for time series tables (nginx_access_logs_ts and nginx_uptime_ts).
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.models.base import Base


class NginxAccessLogModel(Base):
    """
    SQLAlchemy model for nginx_access_logs_ts table.

    Time series table for storing Nginx access logs.
    """

    __tablename__ = "nginx_access_logs_ts"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier for the log entry",
    )
    timestamp_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Timestamp when the request occurred (UTC)",
    )
    client_ip: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="IP address of the client",
    )
    http_method: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="HTTP method (GET, POST, etc.)",
    )
    request_uri: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="URI/path requested",
    )
    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="HTTP status code",
    )
    response_time: Mapped[float] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        default=0.0,
        comment="Response time in seconds",
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User agent string",
    )
    raw_line: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Original log line (for debugging)",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"NginxAccessLogModel(id={self.id}, "
            f"timestamp_utc={self.timestamp_utc}, "
            f"status_code={self.status_code})"
        )


class NginxUptimeModel(Base):
    """
    SQLAlchemy model for nginx_uptime_ts table.

    Time series table for storing uptime measurements.
    """

    __tablename__ = "nginx_uptime_ts"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier for the uptime record",
    )
    timestamp_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Timestamp when the measurement was taken (UTC)",
    )
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="Status value (UP or DOWN)",
    )
    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Source of the measurement",
    )
    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Optional details about the measurement",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"NginxUptimeModel(id={self.id}, "
            f"timestamp_utc={self.timestamp_utc}, "
            f"status={self.status})"
        )
