"""
Event Router - API endpoints for event sourcing
Provides endpoints for querying events, diagnostics, and debugging
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.domains.tableorder.events import EventQuery, EventListResponse, EventResponse
from app.domains.tableorder.event_service import EventService

router = APIRouter()


@router.get("/", response_model=EventListResponse)
async def list_events(
    branch_code: str = Query(..., description="Branch code"),
    table_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    order_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    event_source: Optional[str] = Query(None),
    correlation_id: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    has_error: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Query events with filters.
    Use this to review operations and track issues.
    """
    query = EventQuery(
        branch_code=branch_code,
        table_id=table_id,
        session_id=session_id,
        order_id=order_id,
        event_type=event_type,
        event_source=event_source,
        correlation_id=correlation_id,
        start_time=start_time,
        end_time=end_time,
        has_error=has_error,
        page=page,
        page_size=page_size
    )

    service = EventService(db)
    return await service.get_events(query)


@router.get("/order/{order_id}/timeline", response_model=list[EventResponse])
async def get_order_timeline(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete event timeline for an order.
    Useful for debugging order processing issues.
    """
    service = EventService(db)
    events = await service.get_order_timeline(order_id)

    if not events:
        raise HTTPException(status_code=404, detail="No events found for this order")

    return events


@router.get("/session/{session_id}/timeline", response_model=list[EventResponse])
async def get_session_timeline(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete event timeline for a table session.
    Shows all activity from session start to end.
    """
    service = EventService(db)
    events = await service.get_session_timeline(session_id)

    if not events:
        raise HTTPException(status_code=404, detail="No events found for this session")

    return events


@router.get("/correlation/{correlation_id}", response_model=list[EventResponse])
async def get_correlation_chain(
    correlation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all events in a correlation chain.
    Use this to trace a specific order's journey through the system.

    Example: Order created → Sent to kitchen → Kitchen acknowledged
    """
    service = EventService(db)
    events = await service.get_correlation_chain(correlation_id)

    if not events:
        raise HTTPException(status_code=404, detail="No events found for this correlation")

    return events


# ============ Diagnostics Endpoints ============

@router.get("/diagnostics/undelivered")
async def get_undelivered_orders(
    branch_code: str = Query(...),
    since_minutes: int = Query(5, ge=1, le=60),
    db: AsyncSession = Depends(get_db)
):
    """
    Find orders that were created but not acknowledged by kitchen.

    This is critical for detecting gateway issues where:
    - Customer placed order on iPad
    - Kitchen never received it

    Returns orders that have been waiting for acknowledgment.
    """
    service = EventService(db)
    undelivered = await service.get_undelivered_orders(branch_code, since_minutes)

    return {
        "branch_code": branch_code,
        "since_minutes": since_minutes,
        "count": len(undelivered),
        "orders": undelivered,
        "alert": len(undelivered) > 0,
        "message": f"{len(undelivered)} order(s) not acknowledged in last {since_minutes} minutes" if undelivered else "All orders delivered"
    }


@router.get("/diagnostics/failed-deliveries")
async def get_failed_deliveries(
    branch_code: str = Query(...),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all failed gateway deliveries.

    Shows:
    - WebSocket send failures
    - Kitchen connection issues
    - POS communication errors
    """
    service = EventService(db)
    failures = await service.get_failed_deliveries(branch_code, hours)

    return {
        "branch_code": branch_code,
        "hours": hours,
        "count": len(failures),
        "failures": failures
    }


@router.get("/diagnostics/errors")
async def get_error_summary(
    branch_code: str = Query(...),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary of all errors in the system.

    Useful for:
    - Identifying recurring issues
    - Monitoring system health
    - Debugging patterns
    """
    service = EventService(db)
    summary = await service.get_error_summary(branch_code, hours)

    return {
        "branch_code": branch_code,
        "hours": hours,
        **summary
    }


# ============ Health Check ============

@router.get("/health")
async def event_system_health(
    branch_code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick health check for the event sourcing system.

    Returns:
    - Recent event count
    - Undelivered orders
    - Error rate
    """
    service = EventService(db)

    # Get recent events (last hour)
    from datetime import timedelta
    from app.domains.tableorder.events import EventQuery

    recent = await service.get_events(EventQuery(
        branch_code=branch_code,
        start_time=datetime.utcnow() - timedelta(hours=1),
        page_size=1  # Just need count
    ))

    # Get undelivered
    undelivered = await service.get_undelivered_orders(branch_code, 5)

    # Get error count
    errors = await service.get_error_summary(branch_code, 1)

    status = "healthy"
    if len(undelivered) > 0:
        status = "warning"
    if errors["total_errors"] > 10:
        status = "degraded"

    return {
        "status": status,
        "branch_code": branch_code,
        "metrics": {
            "events_last_hour": recent.total,
            "undelivered_orders": len(undelivered),
            "errors_last_hour": errors["total_errors"]
        },
        "alerts": {
            "has_undelivered": len(undelivered) > 0,
            "high_error_rate": errors["total_errors"] > 10
        }
    }
