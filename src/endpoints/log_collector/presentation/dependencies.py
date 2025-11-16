"""
FastAPI dependencies for log_collector endpoint.

Provides dependency injection for repositories and use cases.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.endpoints.log_collector.application.calculate_uptime import CalculateUptime
from src.endpoints.log_collector.application.collect_logs import CollectLogs
from src.endpoints.log_collector.domain.repositories import (
    LogRepository,
    UptimeRepository,
)
from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyLogRepository,
    SQLAlchemyUptimeRepository,
)
from src.shared.infrastructure.database import get_session


def get_log_repository(
    session: Session = Depends(get_session),
) -> LogRepository:
    """
    Get LogRepository instance.

    Creates a repository instance with the current database session.

    Args:
        session: Database session from dependency injection.

    Returns:
        LogRepository implementation instance.
    """
    return SQLAlchemyLogRepository(session)


def get_uptime_repository(
    session: Session = Depends(get_session),
) -> UptimeRepository:
    """
    Get UptimeRepository instance.

    Creates a repository instance with the current database session.

    Args:
        session: Database session from dependency injection.

    Returns:
        UptimeRepository implementation instance.
    """
    return SQLAlchemyUptimeRepository(session)


def get_collect_logs_use_case(
    repository: LogRepository = Depends(get_log_repository),
) -> CollectLogs:
    """
    Get CollectLogs use case instance.

    Args:
        repository: LogRepository instance from dependency injection.

    Returns:
        CollectLogs use case instance.
    """
    return CollectLogs(repository=repository)


def get_calculate_uptime_use_case(
    repository: UptimeRepository = Depends(get_uptime_repository),
) -> CalculateUptime:
    """
    Get CalculateUptime use case instance.

    Args:
        repository: UptimeRepository instance from dependency injection.

    Returns:
        CalculateUptime use case instance.
    """
    return CalculateUptime(repository=repository)
