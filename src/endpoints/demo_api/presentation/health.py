"""
Health check endpoint for demo_api.

Provides health check functionality to verify service and database status.
"""

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.endpoints.demo_api.presentation.schemas import HealthResponse
from src.shared.infrastructure.database import get_session

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    status_code=200,
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the service and database connection.",
)
def health_check(
    session: Session = Depends(get_session),
) -> HealthResponse:
    """
    Health check endpoint.

    Verifies that the service is running and can connect to the database.
    Returns status "UP" if healthy, "DOWN" if there are issues.

    Args:
        session: Database session for checking database connectivity.

    Returns:
        HealthResponse with service and database status.
    """
    database_status: Optional[str] = None

    try:
        # Test database connection
        session.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:
        database_status = "disconnected"

    status_value = "UP" if database_status == "connected" else "DOWN"

    return HealthResponse(status=status_value, database=database_status)
