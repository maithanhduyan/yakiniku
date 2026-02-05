"""
Kitchen Router - Kitchen Display System APIs
Team: kitchen
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.domains.order.models import Order, OrderItem, OrderStatus
from app.domains.shared.models import Table

router = APIRouter()


@router.get("/orders")
async def get_kitchen_orders(
    branch_code: str = "hirama",
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for kitchen display (pending, confirmed, preparing)"""
    query = select(Order).options(selectinload(Order.items)).where(
        Order.branch_code == branch_code
    )

    if status:
        query = query.where(Order.status == status)
    else:
        # By default show active orders (not served/cancelled)
        query = query.where(
            Order.status.in_([
                OrderStatus.PENDING.value,
                OrderStatus.CONFIRMED.value,
                OrderStatus.PREPARING.value,
                OrderStatus.READY.value
            ])
        )

    query = query.order_by(Order.created_at)

    result = await db.execute(query)
    orders = result.scalars().all()

    # Get table info for each order
    kitchen_orders = []
    for order in orders:
        # Get table number
        table_result = await db.execute(
            select(Table).where(Table.id == order.table_id)
        )
        table = table_result.scalar_one_or_none()

        # Calculate wait time
        wait_seconds = (datetime.utcnow() - order.created_at).total_seconds()

        kitchen_orders.append({
            "id": order.id,
            "order_number": order.order_number,
            "table_id": order.table_id,
            "table_number": table.table_number if table else "??",
            "session_id": order.session_id,
            "status": order.status,
            "wait_time_seconds": int(wait_seconds),
            "wait_time_display": format_wait_time(wait_seconds),
            "urgency": get_urgency_level(wait_seconds),
            "items": [
                {
                    "id": item.id,
                    "name": item.item_name,
                    "quantity": item.quantity,
                    "notes": item.notes,
                    "status": item.status
                }
                for item in order.items
            ],
            "created_at": order.created_at.isoformat()
        })

    return {
        "orders": kitchen_orders,
        "total": len(kitchen_orders),
        "summary": {
            "pending": sum(1 for o in kitchen_orders if o["status"] == "pending"),
            "preparing": sum(1 for o in kitchen_orders if o["status"] == "preparing"),
            "ready": sum(1 for o in kitchen_orders if o["status"] == "ready")
        }
    }


@router.patch("/orders/{order_id}/start")
async def start_preparing(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark order as preparing"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = OrderStatus.PREPARING.value
    order.confirmed_at = datetime.utcnow()

    await db.commit()

    return {"message": "Order started", "status": "preparing"}


@router.patch("/orders/{order_id}/ready")
async def mark_ready(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark order as ready for serving"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = OrderStatus.READY.value
    order.ready_at = datetime.utcnow()

    await db.commit()

    return {"message": "Order ready", "status": "ready"}


@router.patch("/orders/{order_id}/served")
async def mark_served(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark order as served"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = OrderStatus.SERVED.value
    order.served_at = datetime.utcnow()

    await db.commit()

    return {"message": "Order served", "status": "served"}


@router.patch("/items/{item_id}/done")
async def mark_item_done(
    item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark individual item as prepared"""
    result = await db.execute(
        select(OrderItem).where(OrderItem.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.status = OrderStatus.READY.value
    item.prepared_at = datetime.utcnow()

    await db.commit()

    return {"message": "Item done", "status": "ready"}


def format_wait_time(seconds: float) -> str:
    """Format wait time for display"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def get_urgency_level(seconds: float) -> str:
    """Get urgency level based on wait time"""
    if seconds < 60:
        return "new"      # âšª < 1 min
    elif seconds < 180:
        return "normal"   # ðŸŸ¢ 1-3 min
    elif seconds < 300:
        return "warning"  # ðŸŸ¡ 3-5 min
    else:
        return "urgent"   # ðŸ”´ > 5 min

