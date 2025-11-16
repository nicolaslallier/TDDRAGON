"""
Pydantic schemas for log_collector endpoint.

Contains request and response models for API endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LogQueryRequest(BaseModel):
    """
    Request schema for querying logs.

    Attributes:
        start_time: Start of time range (optional).
        end_time: End of time range (optional).
        status_code: Filter by HTTP status code (optional).
        uri: Filter by request URI (optional).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T23:59:59Z",
                "status_code": 500,
            }
        }
    )

    start_time: Optional[datetime] = Field(
        None, description="Start of time range (inclusive)"
    )
    end_time: Optional[datetime] = Field(
        None, description="End of time range (inclusive)"
    )
    status_code: Optional[int] = Field(None, description="Filter by HTTP status code")
    uri: Optional[str] = Field(None, description="Filter by request URI")


class LogEntryResponse(BaseModel):
    """
    Response schema for a log entry.

    Attributes:
        id: Unique identifier for the log entry.
        timestamp_utc: Timestamp when the request occurred.
        client_ip: IP address of the client.
        http_method: HTTP method.
        request_uri: URI/path requested.
        status_code: HTTP status code.
        response_time: Response time in seconds.
        user_agent: User agent string (optional).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "timestamp_utc": "2024-01-01T10:00:00Z",
                "client_ip": "192.168.1.1",
                "http_method": "GET",
                "request_uri": "/health",
                "status_code": 200,
                "response_time": 0.05,
            }
        }
    )

    id: int = Field(..., description="Unique identifier for the log entry")
    timestamp_utc: datetime = Field(
        ..., description="Timestamp when the request occurred (UTC)"
    )
    client_ip: str = Field(..., description="IP address of the client")
    http_method: str = Field(..., description="HTTP method")
    request_uri: str = Field(..., description="URI/path requested")
    status_code: int = Field(..., description="HTTP status code")
    response_time: float = Field(..., description="Response time in seconds")
    user_agent: Optional[str] = Field(None, description="User agent string")


class UptimeQueryRequest(BaseModel):
    """
    Request schema for querying uptime.

    Attributes:
        start_time: Start of time period.
        end_time: End of time period.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T23:59:59Z",
            }
        }
    )

    start_time: datetime = Field(..., description="Start of time period")
    end_time: datetime = Field(..., description="End of time period")


class UptimeResponse(BaseModel):
    """
    Response schema for uptime calculation.

    Attributes:
        uptime_percentage: Uptime percentage (0.0 to 100.0).
        start_time: Start of time period.
        end_time: End of time period.
        total_measurements: Total number of measurements.
        up_count: Number of UP measurements.
        down_count: Number of DOWN measurements.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "uptime_percentage": 99.5,
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T23:59:59Z",
                "total_measurements": 100,
                "up_count": 99,
                "down_count": 1,
            }
        }
    )

    uptime_percentage: float = Field(
        ..., description="Uptime percentage (0.0 to 100.0)"
    )
    start_time: datetime = Field(..., description="Start of time period")
    end_time: datetime = Field(..., description="End of time period")
    total_measurements: int = Field(..., description="Total number of measurements")
    up_count: int = Field(..., description="Number of UP measurements")
    down_count: int = Field(..., description="Number of DOWN measurements")
