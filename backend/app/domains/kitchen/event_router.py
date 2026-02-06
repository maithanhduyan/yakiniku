"""
Kitchen Event Router - API endpoints for kitchen event sourcing
Provides endpoints for logging kitchen actions and querying history
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


@router.post("/", response_model=KitchenEventResponse)
async def log_kitchen_event(
    event_data: KitchenEventCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Log a kitchen event from the KDS frontend.
    Used for tracking item served, cancelled, and other actions.
    """
    service = KitchenEventService(db)
    event = await service.log_from_create(event_data)
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
