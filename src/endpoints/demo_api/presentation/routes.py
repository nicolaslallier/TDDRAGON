"""
FastAPI routes for demo_api endpoint.

Defines HTTP endpoints for the demo API.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.endpoints.demo_api.application.create_item import CreateItem
from src.endpoints.demo_api.application.list_items import ListItems
from src.endpoints.demo_api.domain.models import DemoItem
from src.endpoints.demo_api.presentation.dependencies import (
    get_create_item_use_case,
    get_list_items_use_case,
)
from src.endpoints.demo_api.presentation.schemas import (
    CreateDemoItemRequest,
    DemoItemResponse,
)

router = APIRouter(prefix="/demo-items", tags=["demo-items"])


def _to_response(item: DemoItem) -> DemoItemResponse:
    """
    Convert domain model to response schema.

    Args:
        item: Domain model instance.

    Returns:
        Response schema instance.
    """
    return DemoItemResponse(
        id=item.id,
        label=item.label,
        created_at=item.created_at,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DemoItemResponse,
    summary="Create a demo item",
    description="Create a new demo item with the provided label.",
)
def create_demo_item(
    request: CreateDemoItemRequest,
    use_case: CreateItem = Depends(get_create_item_use_case),
) -> DemoItemResponse:
    """
    Create a new demo item.

    Creates a new demo item with the provided label and returns
    the created item with its generated id.

    Args:
        request: Request containing the label for the new item.
        use_case: CreateItem use case instance.

    Returns:
        Created demo item with id and timestamp.

    Raises:
        HTTPException: If label validation fails (400 Bad Request).
    """
    try:
        item = use_case.execute(label=request.label)
        return _to_response(item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[DemoItemResponse],
    summary="List all demo items",
    description="Retrieve all demo items from the database.",
)
def list_demo_items(
    use_case: ListItems = Depends(get_list_items_use_case),
) -> list[DemoItemResponse]:
    """
    List all demo items.

    Retrieves all demo items from the database, ordered by
    creation date.

    Args:
        use_case: ListItems use case instance.

    Returns:
        List of all demo items.
    """
    items = use_case.execute()
    return [_to_response(item) for item in items]
