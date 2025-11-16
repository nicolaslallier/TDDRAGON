"""
Repository implementations for log_collector endpoint.

Contains SQLAlchemy-based implementations of repository interfaces.
"""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord
from src.endpoints.log_collector.infrastructure.models import (
    NginxAccessLogModel,
    NginxUptimeModel,
)


class SQLAlchemyLogRepository:
    """
    SQLAlchemy implementation of LogRepository.

    This repository uses SQLAlchemy to persist and retrieve LogEntry
    entities from the nginx_access_logs_ts time series table.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize SQLAlchemyLogRepository.

        Args:
            session: SQLAlchemy database session.
        """
        self._session = session

    def create(self, entry: LogEntry) -> LogEntry:
        """
        Create a new LogEntry in the database.

        Args:
            entry: LogEntry domain model to create.

        Returns:
            Created LogEntry with assigned id.
        """
        db_model = NginxAccessLogModel(
            timestamp_utc=entry.timestamp_utc,
            client_ip=entry.client_ip,
            http_method=entry.http_method,
            request_uri=entry.request_uri,
            status_code=entry.status_code,
            response_time=entry.response_time,
            user_agent=entry.user_agent,
            raw_line=entry.raw_line,
        )
        self._session.add(db_model)
        self._session.flush()
        self._session.commit()
        # Ensure data is visible to other connections (SQLite requirement)
        self._session.expire_all()

        # For SQLite with WAL mode, ensure checkpoint is performed
        # This makes committed data visible to other connections immediately
        try:
            connection = self._session.connection()
            if connection.dialect.name == "sqlite":
                # Execute WAL checkpoint to ensure data is visible to other connections
                from sqlalchemy import text

                connection.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
        except Exception:
            # Ignore errors - checkpoint is optional
            pass

        return self._to_domain_model(db_model)

    def find_by_time_range(
        self, start_time: datetime, end_time: datetime
    ) -> Sequence[LogEntry]:
        """
        Find LogEntries within a time range.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).

        Returns:
            Sequence of LogEntries ordered by timestamp.
        """
        db_models = (
            self._session.query(NginxAccessLogModel)
            .filter(
                and_(
                    NginxAccessLogModel.timestamp_utc >= start_time,
                    NginxAccessLogModel.timestamp_utc <= end_time,
                )
            )
            .order_by(NginxAccessLogModel.timestamp_utc.asc())
            .all()
        )

        return [self._to_domain_model(model) for model in db_models]

    def find_by_status_code(self, status_code: int) -> Sequence[LogEntry]:
        """
        Find LogEntries by HTTP status code.

        Args:
            status_code: HTTP status code to filter by.

        Returns:
            Sequence of LogEntries with the specified status code.
        """
        db_models = (
            self._session.query(NginxAccessLogModel)
            .filter(NginxAccessLogModel.status_code == status_code)
            .order_by(NginxAccessLogModel.timestamp_utc.desc())
            .all()
        )

        return [self._to_domain_model(model) for model in db_models]

    def _to_domain_model(self, db_model: NginxAccessLogModel) -> LogEntry:
        """
        Convert database model to domain model.

        Args:
            db_model: SQLAlchemy model instance.

        Returns:
            Domain model instance.
        """
        return LogEntry(
            id=cast(int, db_model.id),
            timestamp_utc=db_model.timestamp_utc,
            client_ip=db_model.client_ip,
            http_method=db_model.http_method,
            request_uri=db_model.request_uri,
            status_code=db_model.status_code,
            response_time=float(db_model.response_time)
            if db_model.response_time
            else 0.0,
            user_agent=db_model.user_agent,
            raw_line=db_model.raw_line,
        )


class SQLAlchemyUptimeRepository:
    """
    SQLAlchemy implementation of UptimeRepository.

    This repository uses SQLAlchemy to persist and retrieve UptimeRecord
    entities from the nginx_uptime_ts time series table.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize SQLAlchemyUptimeRepository.

        Args:
            session: SQLAlchemy database session.
        """
        self._session = session

    def create(self, record: UptimeRecord) -> UptimeRecord:
        """
        Create a new UptimeRecord in the database.

        Args:
            record: UptimeRecord domain model to create.

        Returns:
            Created UptimeRecord with assigned id.
        """
        db_model = NginxUptimeModel(
            timestamp_utc=record.timestamp_utc,
            status=record.status,
            source=record.source,
            details=record.details,
        )
        self._session.add(db_model)
        self._session.flush()
        self._session.commit()
        # Ensure data is visible to other connections (SQLite requirement)
        self._session.expire_all()

        # For SQLite with WAL mode, ensure checkpoint is performed
        # This makes committed data visible to other connections immediately
        try:
            connection = self._session.connection()
            if connection.dialect.name == "sqlite":
                # Execute WAL checkpoint to ensure data is visible to other connections
                from sqlalchemy import text

                connection.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
        except Exception:
            # Ignore errors - checkpoint is optional
            pass

        return self._to_domain_model(db_model)

    def find_by_time_range(
        self, start_time: datetime, end_time: datetime
    ) -> Sequence[UptimeRecord]:
        """
        Find UptimeRecords within a time range.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).

        Returns:
            Sequence of UptimeRecords ordered by timestamp.
        """
        db_models = (
            self._session.query(NginxUptimeModel)
            .filter(
                and_(
                    NginxUptimeModel.timestamp_utc >= start_time,
                    NginxUptimeModel.timestamp_utc <= end_time,
                )
            )
            .order_by(NginxUptimeModel.timestamp_utc.asc())
            .all()
        )

        return [self._to_domain_model(model) for model in db_models]

    def calculate_uptime_percentage(
        self, start_time: datetime, end_time: datetime
    ) -> float:
        """
        Calculate uptime percentage for a time period.

        Args:
            start_time: Start of time period.
            end_time: End of time period.

        Returns:
            Uptime percentage as a float between 0.0 and 100.0.
        """
        # Get all records in time range
        records = self.find_by_time_range(start_time, end_time)

        if not records:
            return 100.0  # No records means no downtime detected

        # Count UP vs total
        total = len(records)
        up_count = sum(1 for r in records if r.status == "UP")

        return (up_count / total) * 100.0

    def _to_domain_model(self, db_model: NginxUptimeModel) -> UptimeRecord:
        """
        Convert database model to domain model.

        Args:
            db_model: SQLAlchemy model instance.

        Returns:
            Domain model instance.
        """
        return UptimeRecord(
            id=cast(int, db_model.id),
            timestamp_utc=db_model.timestamp_utc,
            status=db_model.status,
            source=db_model.source,
            details=db_model.details,
        )
