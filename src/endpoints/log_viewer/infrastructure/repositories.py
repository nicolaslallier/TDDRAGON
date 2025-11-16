"""
Repository implementations for log viewer.

Extends repositories from log_collector with query capabilities needed for UI.
"""

from collections.abc import Sequence
from datetime import datetime
from typing import Optional, cast

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord
from src.endpoints.log_collector.infrastructure.models import (
    NginxAccessLogModel,
    NginxUptimeModel,
)
from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyLogRepository,
    SQLAlchemyUptimeRepository,
)
from src.endpoints.log_viewer.domain.repositories import (
    LogQueryRepository,
    UptimeQueryRepository,
)


class LogViewerRepository(LogQueryRepository):
    """
    Repository adapter for querying logs with UI-specific filters.

    Extends SQLAlchemyLogRepository with additional query methods needed
    for the log viewer UI (filtering, pagination, counting).
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize LogViewerRepository.

        Args:
            session: SQLAlchemy database session.
        """
        self._session = session
        self._base_repository = SQLAlchemyLogRepository(session)

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
        return self._base_repository.find_by_time_range(
            start_time=start_time, end_time=end_time
        )

    def find_by_filters(
        self,
        start_time: datetime,
        end_time: datetime,
        status_code: Optional[int] = None,
        uri: Optional[str] = None,
        client_ip: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "timestamp_utc",
        order_desc: bool = True,
    ) -> Sequence[LogEntry]:
        """
        Find LogEntries with multiple filters and pagination.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).
            status_code: Optional HTTP status code filter.
            uri: Optional URI filter (substring match).
            client_ip: Optional client IP filter.
            limit: Maximum number of results to return.
            offset: Number of results to skip (for pagination).
            order_by: Field to order by (default: "timestamp_utc").
            order_desc: Whether to order descending (default: True).

        Returns:
            Sequence of LogEntries matching the filters.
        """
        # Build query
        query = self._session.query(NginxAccessLogModel).filter(
            and_(
                NginxAccessLogModel.timestamp_utc >= start_time,
                NginxAccessLogModel.timestamp_utc <= end_time,
            )
        )

        # Apply filters
        if status_code is not None:
            query = query.filter(NginxAccessLogModel.status_code == status_code)

        if uri is not None:
            query = query.filter(NginxAccessLogModel.request_uri.contains(uri))

        if client_ip is not None:
            query = query.filter(NginxAccessLogModel.client_ip == client_ip)

        # Apply ordering
        order_column = getattr(NginxAccessLogModel, order_by, None)
        if order_column is None:
            order_column = NginxAccessLogModel.timestamp_utc

        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Apply pagination
        if limit is not None:
            query = query.limit(limit)
        if offset > 0:
            query = query.offset(offset)

        # Execute query
        db_models = query.all()

        return [self._to_domain_model(model) for model in db_models]

    def count_by_filters(
        self,
        start_time: datetime,
        end_time: datetime,
        status_code: Optional[int] = None,
        uri: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> int:
        """
        Count LogEntries matching the filters.

        Args:
            start_time: Start of time range (inclusive).
            end_time: End of time range (inclusive).
            status_code: Optional HTTP status code filter.
            uri: Optional URI filter (substring match).
            client_ip: Optional client IP filter.

        Returns:
            Total count of matching LogEntries.
        """
        # Build query
        query = self._session.query(func.count(NginxAccessLogModel.id)).filter(
            and_(
                NginxAccessLogModel.timestamp_utc >= start_time,
                NginxAccessLogModel.timestamp_utc <= end_time,
            )
        )

        # Apply filters
        if status_code is not None:
            query = query.filter(NginxAccessLogModel.status_code == status_code)

        if uri is not None:
            query = query.filter(NginxAccessLogModel.request_uri.contains(uri))

        if client_ip is not None:
            query = query.filter(NginxAccessLogModel.client_ip == client_ip)

        # Execute query and return count
        return cast(int, query.scalar() or 0)

    def _to_domain_model(self, db_model: NginxAccessLogModel) -> LogEntry:
        """
        Convert database model to domain model.

        Args:
            db_model: Database model instance.

        Returns:
            Domain model instance.
        """
        return self._base_repository._to_domain_model(db_model)


class UptimeViewerRepository(UptimeQueryRepository):
    """
    Repository adapter for querying uptime records.

    Extends SQLAlchemyUptimeRepository with query methods needed for UI.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize UptimeViewerRepository.

        Args:
            session: SQLAlchemy database session.
        """
        self._session = session
        self._base_repository = SQLAlchemyUptimeRepository(session)

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
        return self._base_repository.find_by_time_range(
            start_time=start_time, end_time=end_time
        )

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
        return self._base_repository.calculate_uptime_percentage(
            start_time=start_time, end_time=end_time
        )

