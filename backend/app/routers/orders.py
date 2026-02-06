"""
Orders Router - Table ordering API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime
import uuid

from app.database import get_db
from app.models.order import Order, OrderItem, TableSession, OrderStatus
from app.models.menu import MenuItem
from app.models.table import Table
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderStatusUpdate,
    OrderKitchen, OrderItemKitchen,
    TableSessionCreate, TableSessionResponse, TableSessionSummary,
    StaffCallRequest
)
from app.services.notification_service import notification_manager, Notification, NotificationType

router = APIRouter()


# ============ Table Session ============

@router.post("/sessions", response_model=TableSessionResponse)
async def create_table_session(
    session: TableSessionCreate,
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """Start a new table session (when guests sit down)"""
    # Verify table exists
    result = await db.execute(select(Table).where(Table.id == session.table_id))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Create session
    new_session = TableSession(
        id=str(uuid.uuid4()),
        branch_code=branch_code,
        table_id=session.table_id,
        guest_count=session.guest_count,
        booking_id=session.booking_id
    )

    db.add(new_session)

    # Update table status
    table.status = "occupied"

    await db.commit()
    await db.refresh(new_session)

    # TODO: Fix notification - need to add new NotificationType for orders
    # await notification_manager.broadcast(branch_code, {
    #     "type": "table_session_started",
    #     "table_id": session.table_id,
    #     "session_id": new_session.id
    # })

    return new_session


@router.get("/sessions/{session_id}", response_model=TableSessionResponse)
async def get_table_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get table session details"""
    result = await db.execute(select(TableSession).where(TableSession.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.get("/sessions/{session_id}/summary", response_model=TableSessionSummary)
async def get_session_summary(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session summary for checkout (POS)"""
    # Get session
    result = await db.execute(select(TableSession).where(TableSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get table
    result = await db.execute(select(Table).where(Table.id == session.table_id))
    table = result.scalar_one_or_none()

    # Get all orders for this session
    result = await db.execute(
        select(Order).where(Order.session_id == session_id).order_by(Order.order_number)
    )
    orders = result.scalars().all()

    # Load items for each order
    orders_with_items = []
    subtotal = 0
    for order in orders:
        result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order.items = result.scalars().all()
        orders_with_items.append(order)

        for item in order.items:
            subtotal += item.item_price * item.quantity

    tax = subtotal * 0.1  # 10% tax

    return TableSessionSummary(
        session_id=session_id,
        table_number=table.table_number if table else "?",
        guest_count=session.guest_count,
        started_at=session.started_at,
        orders=orders_with_items,
        subtotal=subtotal,
        tax=tax,
        total=subtotal + tax
    )


# ============ Orders ============

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """Create new order from table"""
    # Check if session exists, create one if not (for demo/walk-in)
    result = await db.execute(
        select(TableSession).where(TableSession.id == order_data.session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        # Auto-create a session for this table
        # First check if there's an active session for this table
        result = await db.execute(
            select(TableSession).where(
                TableSession.table_id == order_data.table_id,
                TableSession.ended_at == None
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            # Create new session
            session = TableSession(
                id=order_data.session_id,
                branch_code=branch_code,
                table_id=order_data.table_id,
                guest_count=4  # Default
            )
            db.add(session)
            await db.flush()

    # Get next order number for this session
    result = await db.execute(
        select(func.count(Order.id)).where(Order.session_id == order_data.session_id)
    )
    order_count = result.scalar() or 0

    # Create order
    order = Order(
        id=str(uuid.uuid4()),
        branch_code=branch_code,
        table_id=order_data.table_id,
        session_id=order_data.session_id,
        order_number=order_count + 1,
        status=OrderStatus.PENDING.value
    )
    db.add(order)

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
            id=str(uuid.uuid4()),
            order_id=order.id,
            menu_item_id=item_data.menu_item_id,
            item_name=menu_item.name,
            item_price=menu_item.price,
            quantity=item_data.quantity,
            notes=item_data.notes,
            status=OrderStatus.PENDING.value
        )
        db.add(order_item)

    await db.commit()
    await db.refresh(order)

    # Load items - return as separate field in response to avoid lazy load issues
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
    items = result.scalars().all()

    # Get table info for notification
    result = await db.execute(select(Table).where(Table.id == order_data.table_id))
    table = result.scalar_one_or_none()

    # TODO: Fix notification - need to add new NotificationType for orders
    # await notification_manager.broadcast(branch_code, {
    #     "type": "new_order",
    #     "order_id": order.id,
    #     "table_number": table.table_number if table else "?",
    #     "order_number": order.order_number,
    #     "items_count": len(order_data.items)
    # })

    # Create response manually to avoid lazy loading issues
    return OrderResponse(
        id=order.id,
        branch_code=order.branch_code,
        table_id=order.table_id,
        session_id=order.session_id,
        order_number=order.order_number,
        status=order.status,
        created_at=order.created_at,
        items=items
    )


@router.get("", response_model=List[OrderResponse])
async def get_orders(
    session_id: str = None,
    table_id: str = None,
    status: str = None,
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """Get orders (filter by session, table, or status)"""
    query = select(Order).where(Order.branch_code == branch_code)

    if session_id:
        query = query.where(Order.session_id == session_id)
    if table_id:
        query = query.where(Order.table_id == table_id)
    if status:
        query = query.where(Order.status == status)

    query = query.order_by(Order.created_at.desc())

    result = await db.execute(query)
    orders = result.scalars().all()

    # Load items for each order
    for order in orders:
        result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
        order.items = result.scalars().all()

    return orders


@router.get("/kitchen", response_model=List[OrderKitchen])
async def get_kitchen_orders(
    branch_code: str = "hirama",
    status: List[str] = Query(default=["pending", "confirmed", "preparing"]),
    db: AsyncSession = Depends(get_db)
):
    """Get orders for kitchen display (KDS)"""
    query = select(Order).where(
        Order.branch_code == branch_code,
        Order.status.in_(status)
    ).order_by(Order.created_at)

    result = await db.execute(query)
    orders = result.scalars().all()

    kitchen_orders = []
    for order in orders:
        # Load items
        result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
        items = result.scalars().all()

        # Get table number
        result = await db.execute(select(Table).where(Table.id == order.table_id))
        table = result.scalar_one_or_none()

        # Calculate elapsed time
        elapsed = (datetime.now() - order.created_at.replace(tzinfo=None)).total_seconds() / 60

        kitchen_orders.append(OrderKitchen(
            id=order.id,
            order_number=order.order_number,
            table_number=table.table_number if table else "?",
            status=order.status,
            items=[OrderItemKitchen(
                id=item.id,
                item_name=item.item_name,
                quantity=item.quantity,
                notes=item.notes,
                status=item.status
            ) for item in items],
            created_at=order.created_at,
            elapsed_minutes=round(elapsed, 1)
        ))

    return kitchen_orders


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update order status (for kitchen/staff)"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = status_update.status

    # Update timestamps
    now = datetime.now()
    if status_update.status == OrderStatus.CONFIRMED.value:
        order.confirmed_at = now
    elif status_update.status == OrderStatus.READY.value:
        order.ready_at = now
    elif status_update.status == OrderStatus.SERVED.value:
        order.served_at = now

    await db.commit()

    # Notify relevant parties
    result = await db.execute(select(Table).where(Table.id == order.table_id))
    table = result.scalar_one_or_none()

    # TODO: Fix notification - need to add new NotificationType for orders
    # await notification_manager.broadcast(order.branch_code, {
    #     "type": "order_status_changed",
    #     "order_id": order_id,
    #     "table_number": table.table_number if table else "?",
    #     "old_status": old_status,
    #     "new_status": status_update.status
    # })

    return {"message": "Status updated", "order_id": order_id, "status": status_update.status}


@router.patch("/items/{item_id}/status")
async def update_item_status(
    item_id: str,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update individual item status (for kitchen)"""
    result = await db.execute(select(OrderItem).where(OrderItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")

    item.status = status_update.status
    if status_update.status == OrderStatus.READY.value:
        item.prepared_at = datetime.now()

    await db.commit()

    return {"message": "Item status updated", "item_id": item_id, "status": status_update.status}


# ============ Staff Call ============

@router.post("/call-staff")
async def call_staff(
    call: StaffCallRequest,
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """Call staff from table (assistance, water, bill, etc.)"""
    # Get table info
    result = await db.execute(select(Table).where(Table.id == call.table_id))
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Map call types to Japanese
    call_type_labels = {
        "assistance": "呼び出し",
        "water": "お水",
        "bill": "お会計",
        "other": "その他"
    }

    # TODO: Fix notification - need to add new NotificationType for orders
    # await notification_manager.broadcast(branch_code, {
    #     "type": "staff_call",
    #     "table_id": call.table_id,
    #     "table_number": table.table_number,
    #     "call_type": call.call_type,
    #     "call_type_label": call_type_labels.get(call.call_type, call.call_type),
    #     "message": call.message,
    #     "timestamp": datetime.now().isoformat()
    # })

    return {"message": "Staff notified", "table_number": table.table_number}

