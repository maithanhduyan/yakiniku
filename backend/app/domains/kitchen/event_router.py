"""
Kitchen Event Router - API endpoints for kitchen event sourcing
Provides endpoints for logging kitchen actions and querying history.
Broadcasts serve/cancel events to all KDS devices for cross-device sync.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.domains.kitchen.events import (
    KitchenEventCreate, KitchenEventResponse, KitchenHistoryResponse
)
from app.domains.kitchen.event_service import KitchenEventService

router = APIRouter()


async def _broadcast_kitchen_sync(event_type: str, event_data: KitchenEventCreate):
    """Broadcast kitchen event to all connected KDS clients for cross-device sync"""
    try:
        from app.routers.websocket import manager
        branch_code = event_data.branch_code or 'hirama'
        await manager.broadcast_to_branch(branch_code, {
            "type": event_type,
            "data": {
                "order_id": event_data.order_id,
                "order_item_id": event_data.order_item_id,
                "item_name": event_data.item_name,
                "item_quantity": event_data.item_quantity,
                "table_number": event_data.table_number,
                "station": event_data.station,
            }
        }, channel="kitchen")
    except Exception as e:
        print(f"⚠️ Failed to broadcast kitchen sync event: {e}")


@router.post("/", response_model=KitchenEventResponse)
async def log_kitchen_event(
    event_data: KitchenEventCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Log a kitchen event from the KDS frontend.
    Used for tracking item served, cancelled, and other actions.
    Broadcasts to all kitchen devices for cross-device sync.
    """
    service = KitchenEventService(db)
    event = await service.log_from_create(event_data)

    # Broadcast to all kitchen clients so other tablets update immediately
    if event_data.event_type in ('kitchen.item.served', 'kitchen.item.cancelled'):
        await _broadcast_kitchen_sync(event_data.event_type, event_data)

    return KitchenEventResponse.model_validate(event)


@router.get("/history", response_model=KitchenHistoryResponse)
async def get_kitchen_history(
    branch_code: str = Query("hirama", description="Branch code"),
    station: Optional[str] = Query(None, description="Filter by station: meat, side, drink, all"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    since_hours: int = Query(24, ge=1, le=168, description="Hours of history to fetch"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get kitchen action history.
    Shows served and cancelled items for quality tracking.
    """
    service = KitchenEventService(db)
    return await service.get_history(
        branch_code=branch_code,
        station=station,
        event_type=event_type,
        limit=limit,
        offset=offset,
        since_hours=since_hours,
    )
