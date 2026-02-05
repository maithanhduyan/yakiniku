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

from app.database import get_db
from app.domains.order.models import Order, OrderItem, OrderStatus, TableSession
from app.domains.order.schemas import (
    OrderCreate, OrderResponse, OrderListResponse,
    TableSessionCreate, TableSessionResponse
)
from app.domains.shared.models import MenuItem

router = APIRouter()


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new order from table"""
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
    for item_data in order_data.items:
        # Get menu item details
        result = await db.execute(
            select(MenuItem).where(MenuItem.id == item_data.menu_item_id)
        )
        menu_item = result.scalar_one_or_none()

        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item_data.menu_item_id} not found")

        order_item = OrderItem(
            menu_item_id=item_data.menu_item_id,
            item_name=menu_item.name,
            item_price=menu_item.price,
            quantity=item_data.quantity,
            notes=item_data.notes
        )
        order.items.append(order_item)

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
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

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

    return {"message": "Status updated", "status": status}


# Session endpoints
@router.post("/sessions", response_model=TableSessionResponse)
async def create_session(
    session_data: TableSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Start a new table session"""
    session = TableSession(
        branch_code=session_data.branch_code,
        table_id=session_data.table_id,
        booking_id=session_data.booking_id,
        guest_count=session_data.guest_count
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

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
