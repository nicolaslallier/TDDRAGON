"""
Pydantic schemas for log viewer API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FilterLogsRequest(BaseModel):
    """
    Request schema for filtering logs.

    Args:
        start_time: Start of time range (ISO format string).
        end_time: End of time range (ISO format string).
        status_code: Optional HTTP status code filter.
        uri: Optional URI filter (substring match).
        client_ip: Optional client IP filter.
        page: Page number (default: 1).
        page_size: Number of items per page (default: 50).
    """

    start_time: str = Field(..., description="Start time in ISO format")
    end_time: str = Field(..., description="End time in ISO format")
    status_code: Optional[int] = Field(None, description="HTTP status code filter")
    uri: Optional[str] = Field(None, description="URI filter (substring match)")
    client_ip: Optional[str] = Field(None, description="Client IP filter")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Page size")


class QueryUptimeRequest(BaseModel):
    """
    Request schema for querying uptime.

    Args:
        start_time: Start of time range (ISO format string).
        end_time: End of time range (ISO format string).
    """

    start_time: str = Field(..., description="Start time in ISO format")
    end_time: str = Field(..., description="End time in ISO format")


class LoginRequest(BaseModel):
    """
    Request schema for login.

    Args:
        username: Username.
        password: Password.
    """

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

