"""
FastAPI routes for log_collector endpoint.

Defines HTTP endpoints for querying logs and uptime.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, status

from src.endpoints.log_collector.application.calculate_uptime import CalculateUptime
from src.endpoints.log_collector.domain.models import LogEntry
from src.endpoints.log_collector.domain.repositories import (
    LogRepository,
    UptimeRepository,
)
from src.endpoints.log_collector.presentation.dependencies import (
    get_calculate_uptime_use_case,
    get_log_repository,
    get_uptime_repository,
)
from src.endpoints.log_collector.presentation.schemas import (
    LogEntryResponse,
    UptimeResponse,
)

router = APIRouter(prefix="/logs", tags=["logs"])


def _to_log_response(entry: LogEntry) -> LogEntryResponse:
    """
    Convert domain model to response schema.

    Args:
        entry: LogEntry domain model instance.

    Returns:
        LogEntryResponse schema instance.
    """
    return LogEntryResponse(
        id=entry.id,
        timestamp_utc=entry.timestamp_utc,
        client_ip=entry.client_ip,
        http_method=entry.http_method,
        request_uri=entry.request_uri,
        status_code=entry.status_code,
        response_time=entry.response_time,
        user_agent=entry.user_agent,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[LogEntryResponse],
    summary="Query log entries",
    description="Query Nginx access logs with optional filters.",
)
def query_logs(
    start_time: datetime
    | None = Query(None, description="Start of time range (inclusive)"),
    end_time: datetime
    | None = Query(None, description="End of time range (inclusive)"),
    status_code: int | None = Query(None, description="Filter by HTTP status code"),
    uri: str | None = Query(None, description="Filter by request URI"),
    repository: LogRepository = Depends(get_log_repository),
) -> list[LogEntryResponse]:
    """
    Query log entries with optional filters.

    Args:
        start_time: Start of time range (optional).
        end_time: End of time range (optional).
        status_code: Filter by HTTP status code (optional).
        uri: Filter by request URI (optional).
        repository: LogRepository instance.

    Returns:
        List of log entries matching the filters.
    """
    # Default to last 24 hours if no time range specified
    if not start_time or not end_time:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)

    # Query by time range
    entries = repository.find_by_time_range(start_time, end_time)

    # Filter by status code if provided
    if status_code is not None:
        entries = [e for e in entries if e.status_code == status_code]

    # Filter by URI if provided
    if uri is not None:
        entries = [e for e in entries if uri in e.request_uri]

    return [_to_log_response(entry) for entry in entries]


@router.get(
    "/uptime",
    status_code=status.HTTP_200_OK,
    response_model=UptimeResponse,
    summary="Calculate uptime percentage",
    description="Calculate uptime percentage for a time period.",
)
def get_uptime(
    start_time: datetime = Query(..., description="Start of time period"),
    end_time: datetime = Query(..., description="End of time period"),
    use_case: CalculateUptime = Depends(get_calculate_uptime_use_case),
    repository: UptimeRepository = Depends(get_uptime_repository),
) -> UptimeResponse:
    """
    Calculate uptime percentage for a time period.

    Args:
        start_time: Start of time period.
        end_time: End of time period.
        use_case: CalculateUptime use case instance.
        repository: UptimeRepository instance.

    Returns:
        UptimeResponse with uptime percentage and statistics.
    """
    # Calculate uptime percentage
    uptime_percentage = use_case.execute(start_time, end_time)

    # Get records for statistics
    records = repository.find_by_time_range(start_time, end_time)
    total_measurements = len(records)
    up_count = sum(1 for r in records if r.status == "UP")
    down_count = total_measurements - up_count

    return UptimeResponse(
        uptime_percentage=uptime_percentage,
        start_time=start_time,
        end_time=end_time,
        total_measurements=total_measurements,
        up_count=up_count,
        down_count=down_count,
    )
