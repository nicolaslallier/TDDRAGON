"""
Pydantic schemas for demo_api endpoint.

Contains request and response models for API endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateDemoItemRequest(BaseModel):
    """
    Request schema for creating a demo item.

    Attributes:
        label: Text label for the demo item. Must be between 1 and 255 characters.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "My Demo Item",
            }
        }
    )

    label: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Text label for the demo item",
        examples=["My Demo Item"],
    )


class DemoItemResponse(BaseModel):
    """
    Response schema for a demo item.

    Attributes:
        id: Unique identifier for the item.
        label: Text label for the item.
        created_at: Timestamp when the item was created.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "label": "My Demo Item",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }
    )

    id: int = Field(..., description="Unique identifier for the demo item")
    label: str = Field(..., description="Text label for the demo item")
    created_at: datetime = Field(..., description="Timestamp when the item was created")


class HealthResponse(BaseModel):
    """
    Response schema for health check endpoint.

    Attributes:
        status: Status of the service (e.g., "UP", "DOWN").
        database: Status of database connection (optional).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "UP",
                "database": "connected",
            }
        }
    )

    status: str = Field(..., description="Status of the service", examples=["UP"])
    database: Optional[str] = Field(
        None, description="Status of database connection", examples=["connected"]
    )
