"""
Order Router - Table Order APIs
Team: table-order
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.domains.tableorder.models import Order, OrderItem, OrderStatus, TableSession
from app.domains.tableorder.schemas import (
    OrderCreate, OrderResponse, OrderListResponse,
    TableSessionCreate, TableSessionResponse
)
from app.domains.shared.models import MenuItem
from app.domains.tableorder.events import EventType, EventSource
from app.domains.tableorder.event_service import EventService

router = APIRouter()


# ============ Call Staff Schema ============

class CallStaffRequest(BaseModel):
    table_id: str
    session_id: str
    call_type: str  # "assistance", "water", "bill"


class CallStaffResponse(BaseModel):
    success: bool
    message: str
    call_type: str
    correlation_id: str


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new order from table"""
    event_service = EventService(db)

    # Get next order number for this session
    result = await db.execute(
        select(func.max(Order.order_number))
        .where(Order.session_id == order_data.session_id)
    )
    max_num = result.scalar() or 0

    # Create order
    order = Order(
        branch_code=order_data.branch_code,
        table_id=order_data.table_id,
        session_id=order_data.session_id,
        order_number=max_num + 1,
        status=OrderStatus.PENDING.value
    )

    # Add items
    items_data = []
    for item_data in order_data.items:
        # Get menu item details from database
        result = await db.execute(
            select(MenuItem).where(MenuItem.id == item_data.menu_item_id)
        )
        menu_item = result.scalar_one_or_none()

        # Use DB data if exists, otherwise use demo data from request
        if menu_item:
            item_name = menu_item.name
            item_price = menu_item.price
        elif item_data.item_name and item_data.item_price:
            # Demo mode: use data from request
            item_name = item_data.item_name
            item_price = item_data.item_price
        else:
            # No menu item and no demo data - use placeholder
            item_name = f"Item {item_data.menu_item_id}"
            item_price = 0

        order_item = OrderItem(
            menu_item_id=item_data.menu_item_id,
            item_name=item_name,
            item_price=item_price,
            quantity=item_data.quantity,
            notes=item_data.notes
        )
        order.items.append(order_item)

        items_data.append({
            "menu_item_id": item_data.menu_item_id,
            "name": item_name,
            "price": float(item_price),
            "quantity": item_data.quantity,
            "notes": item_data.notes
        })

    db.add(order)
    await db.commit()
    await db.refresh(order)

    # Reload with items
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order.id)
    )
    order = result.scalar_one()

    # Log ORDER_CREATED event
    correlation_id = await event_service.log_order_created(
        order_id=order.id,
        branch_code=order_data.branch_code,
        table_id=order_data.table_id,
        session_id=order_data.session_id,
        items=items_data,
        source=EventSource.TABLE_ORDER
    )

    # TODO: Send to kitchen via WebSocket and log GATEWAY_SENT
    # await event_service.log_gateway_sent(...)

    return OrderResponse.model_validate(order)


@router.get("/table/{table_id}", response_model=OrderListResponse)
async def get_table_orders(
    table_id: str,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a table (optionally filtered by session)"""
    query = select(Order).options(selectinload(Order.items)).where(Order.table_id == table_id)

    if session_id:
        query = query.where(Order.session_id == session_id)

    query = query.order_by(Order.created_at.desc())

    result = await db.execute(query)
    orders = result.scalars().all()

    return OrderListResponse(
        orders=[OrderResponse.model_validate(o) for o in orders],
        total=len(orders)
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get order by ID"""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse.model_validate(order)


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    """Update order status"""
    event_service = EventService(db)

    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = status

    # Update timestamps based on status
    now = datetime.utcnow()
    if status == OrderStatus.CONFIRMED.value:
        order.confirmed_at = now
    elif status == OrderStatus.READY.value:
        order.ready_at = now
    elif status == OrderStatus.SERVED.value:
        order.served_at = now

    await db.commit()

    # Log status change event
    status_event_map = {
        OrderStatus.CONFIRMED.value: EventType.ORDER_CONFIRMED,
        OrderStatus.PREPARING.value: EventType.ORDER_PREPARING,
        OrderStatus.READY.value: EventType.ORDER_READY,
        OrderStatus.SERVED.value: EventType.ORDER_SERVED,
        OrderStatus.CANCELLED.value: EventType.ORDER_CANCELLED,
    }

    if status in status_event_map:
        await event_service.log_event(
            event_type=status_event_map[status],
            branch_code=order.branch_code,
            event_source=EventSource.API,
            table_id=order.table_id,
            session_id=order.session_id,
            order_id=order.id,
            data={"old_status": old_status, "new_status": status}
        )

    return {"message": "Status updated", "status": status}


# ============ Call Staff Endpoint ============

@router.post("/call-staff", response_model=CallStaffResponse)
async def call_staff(
    request: CallStaffRequest,
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """
    Call staff from table.
    Logs event for tracking and sends notification via WebSocket.
    """
    event_service = EventService(db)

    # Map call type to event type
    call_event_map = {
        "assistance": EventType.CALL_STAFF,
        "water": EventType.CALL_WATER,
        "bill": EventType.CALL_BILL,
    }

    event_type = call_event_map.get(request.call_type, EventType.CALL_STAFF)

    # Log the call event
    event = await event_service.log_event(
        event_type=event_type,
        event_source=EventSource.TABLE_ORDER,
        branch_code=branch_code,
        table_id=request.table_id,
        session_id=request.session_id,
        data={"call_type": request.call_type}
    )

    # TODO: Send notification to staff via WebSocket
    # notification_manager.broadcast(...)

    call_labels = {
        "assistance": "スタッフを呼び出しました",
        "water": "お水をお持ちします",
        "bill": "お会計をお待ちください"
    }

    return CallStaffResponse(
        success=True,
        message=call_labels.get(request.call_type, "スタッフを呼び出しました"),
        call_type=request.call_type,
        correlation_id=event.correlation_id
    )


# Session endpoints
@router.post("/sessions", response_model=TableSessionResponse)
async def create_session(
    session_data: TableSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Start a new table session"""
    event_service = EventService(db)

    session = TableSession(
        branch_code=session_data.branch_code,
        table_id=session_data.table_id,
        booking_id=session_data.booking_id,
        guest_count=session_data.guest_count
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Log session started event
    await event_service.log_event(
        event_type=EventType.SESSION_STARTED,
        event_source=EventSource.TABLE_ORDER,
        branch_code=session_data.branch_code,
        table_id=session_data.table_id,
        session_id=session.id,
        data={
            "guest_count": session_data.guest_count,
            "booking_id": session_data.booking_id
        }
    )

    return TableSessionResponse.model_validate(session)


@router.get("/sessions/{session_id}", response_model=TableSessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session by ID"""
    result = await db.execute(
        select(TableSession).where(TableSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return TableSessionResponse.model_validate(session)
