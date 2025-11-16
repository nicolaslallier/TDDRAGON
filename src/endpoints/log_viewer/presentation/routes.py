"""
FastAPI routes for log viewer endpoint.

Defines HTTP endpoints for the web UI and HTMX API.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from src.endpoints.log_viewer.application.export_logs import ExportLogs
from src.endpoints.log_viewer.application.get_statistics import GetStatistics
from src.endpoints.log_viewer.application.query_logs import QueryLogs
from src.endpoints.log_viewer.application.query_uptime import QueryUptime
from src.endpoints.log_viewer.infrastructure.auth import MockAuthService
from src.endpoints.log_viewer.presentation.dependencies import (
    get_export_logs_use_case,
    get_query_logs_use_case,
    get_query_uptime_use_case,
    get_statistics_use_case,
)
from src.shared.infrastructure.logger import get_logger

logger = get_logger(__name__)

# Initialize templates
from pathlib import Path
_template_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_template_dir))

router = APIRouter(prefix="/log-viewer", tags=["log-viewer"])


def require_auth(request: Request) -> None:
    """
    Dependency to require authentication.

    Args:
        request: FastAPI request object.

    Raises:
        HTTPException: If user is not authenticated.
    """
    if not MockAuthService.is_authenticated(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"Location": "/log-viewer/login"},
        )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Display login page.

    Args:
        request: FastAPI request object.

    Returns:
        HTML response with login page.
    """
    # If already authenticated, redirect to access logs
    if MockAuthService.is_authenticated(request):
        return RedirectResponse(url="/log-viewer/access-logs", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(request, "login.html")


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Handle login form submission.

    Args:
        request: FastAPI request object.
        username: Username from form.
        password: Password from form.

    Returns:
        Redirect response to access logs page or login page with error.
    """
    if MockAuthService.authenticate(username, password):
        MockAuthService.login(request, username)
        return RedirectResponse(
            url="/log-viewer/access-logs", status_code=status.HTTP_302_FOUND
        )

    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": "Invalid username or password"},
    )


@router.get("/logout")
async def logout(request: Request):
    """
    Handle logout.

    Args:
        request: FastAPI request object.

    Returns:
        Redirect response to login page.
    """
    MockAuthService.logout(request)
    return RedirectResponse(url="/log-viewer/login", status_code=status.HTTP_302_FOUND)


@router.get("/access-logs", response_class=HTMLResponse)
async def access_logs_page(
    request: Request,
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    status_code: Optional[int] = Query(None),
    uri: Optional[str] = Query(None),
    client_ip: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    query_logs: QueryLogs = Depends(get_query_logs_use_case),
    get_statistics: GetStatistics = Depends(get_statistics_use_case),
):
    """
    Display access logs page with filters and results.

    Args:
        request: FastAPI request object.
        start_time: Optional start time filter (ISO format).
        end_time: Optional end time filter (ISO format).
        status_code: Optional status code filter.
        uri: Optional URI filter.
        client_ip: Optional client IP filter.
        page: Page number.
        page_size: Page size.
        query_logs: QueryLogs use case.
        get_statistics: GetStatistics use case.

    Returns:
        HTML response with access logs page.
    """
    require_auth(request)

    # Default to last 24 hours if no time range specified
    now = datetime.now()
    if start_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            if start_dt.tzinfo:
                start_dt = start_dt.astimezone().replace(tzinfo=None)
        except ValueError:
            start_dt = datetime.fromisoformat(start_time)
    else:
        start_dt = now - timedelta(hours=24)

    if end_time:
        try:
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            if end_dt.tzinfo:
                end_dt = end_dt.astimezone().replace(tzinfo=None)
        except ValueError:
            end_dt = datetime.fromisoformat(end_time)
    else:
        end_dt = now

    # Query logs
    result = query_logs.execute(
        start_time=start_dt,
        end_time=end_dt,
        status_code=status_code,
        uri=uri,
        client_ip=client_ip,
        page=page,
        page_size=page_size,
    )

    # Get statistics for charts
    histogram = get_statistics.get_http_code_histogram(
        start_time=start_dt,
        end_time=end_dt,
        status_code=status_code,
        uri=uri,
        client_ip=client_ip,
    )

    username = MockAuthService.get_username(request)

    return templates.TemplateResponse(
        request,
        "access_logs.html",
        {
            "username": username,
            "logs": result.logs,
            "total_count": result.total_count,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
            "has_next_page": result.has_next_page,
            "has_previous_page": result.has_previous_page,
            "start_time": start_dt.strftime("%Y-%m-%dT%H:%M"),
            "end_time": end_dt.strftime("%Y-%m-%dT%H:%M"),
            "status_code": status_code,
            "uri": uri,
            "client_ip": client_ip,
            "http_code_histogram": histogram,
        },
    )


@router.post("/api/filter-logs", response_class=HTMLResponse)
async def filter_logs_post(
    request: Request,
    start_time: Optional[str] = Form(None),
    end_time: Optional[str] = Form(None),
    status_code: Optional[str] = Form(None),  # Accept as string to handle empty strings
    uri: Optional[str] = Form(None),
    client_ip: Optional[str] = Form(None),
    page: int = Form(1),
    page_size: int = Form(50),
    query_logs: QueryLogs = Depends(get_query_logs_use_case),
):
    """
    HTMX POST endpoint for filtering logs.
    
    Args:
        request: FastAPI request object.
        start_time: Optional start time filter (datetime-local format).
        end_time: Optional end time filter (datetime-local format).
        status_code: Optional HTTP status code filter (as string, empty string treated as None).
        uri: Optional URI filter.
        client_ip: Optional client IP filter.
        page: Page number (default: 1).
        page_size: Page size (default: 50).
        query_logs: QueryLogs use case.
    
    Returns:
        HTML partial with filtered log table.
    """
    # Convert empty string to None and parse status_code to int if provided
    status_code_int: Optional[int] = None
    if status_code and status_code.strip():
        try:
            status_code_int = int(status_code)
        except ValueError:
            status_code_int = None
    
    return await _filter_logs_impl(
        request, start_time, end_time, status_code_int, uri, client_ip, page, page_size, query_logs
    )


@router.get("/api/filter-logs", response_class=HTMLResponse)
async def filter_logs_get(
    request: Request,
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    status_code: Optional[int] = Query(None),
    uri: Optional[str] = Query(None),
    client_ip: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    query_logs: QueryLogs = Depends(get_query_logs_use_case),
):
    """HTMX GET endpoint for filtering logs (used for live updates)."""
    return await _filter_logs_impl(
        request, start_time, end_time, status_code, uri, client_ip, page, page_size, query_logs
    )


async def _filter_logs_impl(
    request: Request,
    start_time: Optional[str],
    end_time: Optional[str],
    status_code: Optional[int],
    uri: Optional[str],
    client_ip: Optional[str],
    page: int,
    page_size: int,
    query_logs: QueryLogs,
):
    """
    Implementation for filtering logs (returns partial HTML).

    Args:
        request: FastAPI request object.
        start_time: Start time filter (ISO format).
        end_time: End time filter (ISO format).
        status_code: Optional status code filter.
        uri: Optional URI filter.
        client_ip: Optional client IP filter.
        page: Page number.
        page_size: Page size.
        query_logs: QueryLogs use case.

    Returns:
        HTML partial with log table.
    """
    require_auth(request)

    # Parse times (datetime-local format: "YYYY-MM-DDTHH:mm" or ISO format)
    if start_time:
        try:
            # Try ISO format first
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            if start_dt.tzinfo:
                start_dt = start_dt.astimezone().replace(tzinfo=None)
        except ValueError:
            # Fall back to datetime-local format (no timezone)
            start_dt = datetime.fromisoformat(start_time)
    else:
        start_dt = datetime.now() - timedelta(hours=24)

    if end_time:
        try:
            # Try ISO format first
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            if end_dt.tzinfo:
                end_dt = end_dt.astimezone().replace(tzinfo=None)
        except ValueError:
            # Fall back to datetime-local format (no timezone)
            end_dt = datetime.fromisoformat(end_time)
    else:
        end_dt = datetime.now()

    # Query logs
    result = query_logs.execute(
        start_time=start_dt,
        end_time=end_dt,
        status_code=status_code,
        uri=uri,
        client_ip=client_ip,
        page=page,
        page_size=page_size,
    )

    return templates.TemplateResponse(
        request,
        "partials/log_table.html",
        {
            "logs": result.logs,
            "total_count": result.total_count,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
            "has_next_page": result.has_next_page,
            "has_previous_page": result.has_previous_page,
        },
    )


@router.get("/uptime", response_class=HTMLResponse)
async def uptime_page(
    request: Request,
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    query_uptime: QueryUptime = Depends(get_query_uptime_use_case),
    get_statistics: GetStatistics = Depends(get_statistics_use_case),
):
    """
    Display uptime monitoring page.

    Args:
        request: FastAPI request object.
        start_time: Optional start time filter (datetime-local format).
        end_time: Optional end time filter (datetime-local format).
        query_uptime: QueryUptime use case.
        get_statistics: GetStatistics use case.

    Returns:
        HTML response with uptime page.
    """
    require_auth(request)

    # Default to last 15 minutes if no time range specified
    now = datetime.now()
    if start_time:
        try:
            # Try ISO format first
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            if start_dt.tzinfo:
                start_dt = start_dt.astimezone().replace(tzinfo=None)
        except ValueError:
            # Fall back to datetime-local format (no timezone)
            start_dt = datetime.fromisoformat(start_time)
    else:
        start_dt = now - timedelta(minutes=15)

    if end_time:
        try:
            # Try ISO format first
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            if end_dt.tzinfo:
                end_dt = end_dt.astimezone().replace(tzinfo=None)
        except ValueError:
            # Fall back to datetime-local format (no timezone)
            end_dt = datetime.fromisoformat(end_time)
    else:
        end_dt = now

    # Query uptime (filter by source if provided)
    result = query_uptime.execute(start_time=start_dt, end_time=end_dt)
    
    # Filter records by source if source filter is provided
    filtered_records = result.records
    if source:
        filtered_records = [r for r in result.records if r.source == source]
        # Recalculate uptime percentage for filtered records
        if filtered_records:
            up_count = sum(1 for r in filtered_records if r.status == "UP")
            filtered_uptime_percentage = (up_count / len(filtered_records)) * 100.0
        else:
            filtered_uptime_percentage = 100.0  # No records means no downtime detected
    else:
        filtered_uptime_percentage = result.uptime_percentage

    # Get timeline data for chart (handle errors gracefully)
    try:
        timeline = get_statistics.get_uptime_timeline(start_time=start_dt, end_time=end_dt)
        # Filter timeline by source if provided
        if source:
            timeline = [t for t in timeline if t.get("source") == source]
    except Exception as e:
        logger.error(f"Error getting uptime timeline: {e}", exc_info=True)
        timeline = []

    username = MockAuthService.get_username(request)

    return templates.TemplateResponse(
        request,
        "uptime.html",
        {
            "username": username,
            "records": filtered_records,
            "uptime_percentage": filtered_uptime_percentage,
            "start_time": start_dt.strftime("%Y-%m-%dT%H:%M"),  # Format for HTML input
            "end_time": end_dt.strftime("%Y-%m-%dT%H:%M"),  # Format for HTML input
            "start_time_dt": start_dt,  # Keep datetime for display
            "end_time_dt": end_dt,  # Keep datetime for display
            "uptime_timeline": timeline,
            "source_filter": source or "",  # Pass source filter to template
        },
    )


@router.get("/api/filter-uptime", response_class=HTMLResponse)
async def filter_uptime_get(
    request: Request,
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    query_uptime: QueryUptime = Depends(get_query_uptime_use_case),
):
    """
    HTMX GET endpoint for filtering uptime records (returns partial HTML).

    Args:
        request: FastAPI request object.
        start_time: Optional start time filter (datetime-local format).
        end_time: Optional end time filter (datetime-local format).
        query_uptime: QueryUptime use case.

    Returns:
        HTML partial with uptime records table.
    """
    require_auth(request)

    # Default to last 15 minutes if no time range specified
    now = datetime.now()
    if start_time:
        try:
            # Try ISO format first
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            if start_dt.tzinfo:
                start_dt = start_dt.astimezone().replace(tzinfo=None)
        except ValueError:
            # Fall back to datetime-local format (no timezone)
            start_dt = datetime.fromisoformat(start_time)
    else:
        start_dt = now - timedelta(minutes=15)

    if end_time:
        try:
            # Try ISO format first
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            if end_dt.tzinfo:
                end_dt = end_dt.astimezone().replace(tzinfo=None)
        except ValueError:
            # Fall back to datetime-local format (no timezone)
            end_dt = datetime.fromisoformat(end_time)
    else:
        end_dt = now

    # Query uptime
    result = query_uptime.execute(start_time=start_dt, end_time=end_dt)
    
    # Filter records by source if source filter is provided
    filtered_records = result.records
    if source:
        filtered_records = [r for r in result.records if r.source == source]

    return templates.TemplateResponse(
        request,
        "partials/uptime_table.html",
        {
            "records": filtered_records,
        },
    )


@router.get("/api/export-logs")
async def export_logs(
    request: Request,
    start_time: str = Query(...),
    end_time: str = Query(...),
    status_code: Optional[int] = Query(None),
    uri: Optional[str] = Query(None),
    client_ip: Optional[str] = Query(None),
    export_logs_use_case: ExportLogs = Depends(get_export_logs_use_case),
):
    """
    Export logs to CSV.

    Args:
        request: FastAPI request object.
        start_time: Start time filter (ISO format).
        end_time: End time filter (ISO format).
        status_code: Optional status code filter.
        uri: Optional URI filter.
        client_ip: Optional client IP filter.
        export_logs_use_case: ExportLogs use case.

    Returns:
        CSV file download response.
    """
    require_auth(request)

    # Parse times (datetime-local format: "YYYY-MM-DDTHH:mm" or ISO format)
    try:
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        if start_dt.tzinfo:
            start_dt = start_dt.astimezone().replace(tzinfo=None)
    except ValueError:
        start_dt = datetime.fromisoformat(start_time)

    try:
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        if end_dt.tzinfo:
            end_dt = end_dt.astimezone().replace(tzinfo=None)
    except ValueError:
        end_dt = datetime.fromisoformat(end_time)

    # Export logs
    csv_content = export_logs_use_case.execute(
        start_time=start_dt,
        end_time=end_dt,
        status_code=status_code,
        uri=uri,
        client_ip=client_ip,
    )

    # Generate filename with timestamp
    filename = f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

