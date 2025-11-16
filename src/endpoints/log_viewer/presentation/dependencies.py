"""
Dependency injection for log viewer endpoints.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.endpoints.log_viewer.application.export_logs import ExportLogs
from src.endpoints.log_viewer.application.get_statistics import GetStatistics
from src.endpoints.log_viewer.application.query_logs import QueryLogs
from src.endpoints.log_viewer.application.query_uptime import QueryUptime
from src.endpoints.log_viewer.infrastructure.repositories import (
    LogViewerRepository,
    UptimeViewerRepository,
)
from src.shared.infrastructure.database import get_session


def get_log_repository(session: Session = Depends(get_session)) -> LogViewerRepository:
    """
    Get LogViewerRepository instance.

    Args:
        session: Database session from dependency injection.

    Returns:
        LogViewerRepository instance.
    """
    return LogViewerRepository(session=session)


def get_uptime_repository(
    session: Session = Depends(get_session),
) -> UptimeViewerRepository:
    """
    Get UptimeViewerRepository instance.

    Args:
        session: Database session from dependency injection.

    Returns:
        UptimeViewerRepository instance.
    """
    return UptimeViewerRepository(session=session)


def get_query_logs_use_case(
    repository: LogViewerRepository = Depends(get_log_repository),
) -> QueryLogs:
    """
    Get QueryLogs use case instance.

    Args:
        repository: LogViewerRepository from dependency injection.

    Returns:
        QueryLogs use case instance.
    """
    return QueryLogs(repository=repository)


def get_query_uptime_use_case(
    repository: UptimeViewerRepository = Depends(get_uptime_repository),
) -> QueryUptime:
    """
    Get QueryUptime use case instance.

    Args:
        repository: UptimeViewerRepository from dependency injection.

    Returns:
        QueryUptime use case instance.
    """
    return QueryUptime(repository=repository)


def get_export_logs_use_case(
    repository: LogViewerRepository = Depends(get_log_repository),
) -> ExportLogs:
    """
    Get ExportLogs use case instance.

    Args:
        repository: LogViewerRepository from dependency injection.

    Returns:
        ExportLogs use case instance.
    """
    return ExportLogs(repository=repository)


def get_statistics_use_case(
    log_repository: LogViewerRepository = Depends(get_log_repository),
    uptime_repository: UptimeViewerRepository = Depends(get_uptime_repository),
) -> GetStatistics:
    """
    Get GetStatistics use case instance.

    Args:
        log_repository: LogViewerRepository from dependency injection.
        uptime_repository: UptimeViewerRepository from dependency injection.

    Returns:
        GetStatistics use case instance.
    """
    return GetStatistics(
        log_repository=log_repository, uptime_repository=uptime_repository
    )

