"""
POS Router - Point of Sale APIs
Team: pos
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from decimal import Decimal
from typing import Optional
import secrets

from app.database import get_db
from app.domains.order.models import Order, OrderItem, OrderStatus, TableSession
from app.domains.shared.models import Table
from app.domains.pos.schemas import (
    CheckoutRequest, CheckoutResponse, TableOverview,
    POSDashboard, TableStatusEnum, PaymentMethod
)

router = APIRouter()

TAX_RATE = Decimal("0.10")  # 10% tax


@router.get("/tables", response_model=POSDashboard)
async def get_pos_tables(
    branch_code: str = "jinan",
    db: AsyncSession = Depends(get_db)
):
    """Get all tables with current status for POS overview"""
    # Get all tables
    result = await db.execute(
        select(Table).where(Table.branch_code == branch_code).order_by(Table.table_number)
    )
    tables = result.scalars().all()

    table_overviews = []
    summary = {"available": 0, "occupied": 0, "pending_payment": 0, "cleaning": 0}

    for table in tables:
        # Check for active session
        session_result = await db.execute(
            select(TableSession).where(
                TableSession.table_id == table.id,
                TableSession.ended_at.is_(None)
            )
        )
        session = session_result.scalar_one_or_none()

        if session:
            # Get orders for this session
            orders_result = await db.execute(
                select(Order)
                .options(selectinload(Order.items))
                .where(Order.session_id == session.id)
            )
            orders = orders_result.scalars().all()

            # Calculate total
            total = Decimal("0")
            for order in orders:
                if order.status != OrderStatus.CANCELLED.value:
                    for item in order.items:
                        total += item.item_price * item.quantity

            # Determine status
            if session.is_paid:
                status = TableStatusEnum.cleaning
                summary["cleaning"] += 1
            elif total > 0:
                status = TableStatusEnum.pending_payment
                summary["pending_payment"] += 1
            else:
                status = TableStatusEnum.occupied
                summary["occupied"] += 1

            table_overviews.append(TableOverview(
                id=table.id,
                table_number=table.table_number,
                capacity=table.capacity,
                zone=table.zone,
                status=status,
                session_id=session.id,
                guest_count=session.guest_count,
                current_total=total,
                started_at=session.started_at,
                order_count=len(orders)
            ))
        else:
            summary["available"] += 1
            table_overviews.append(TableOverview(
                id=table.id,
                table_number=table.table_number,
                capacity=table.capacity,
                zone=table.zone,
                status=TableStatusEnum.available
            ))

    return POSDashboard(tables=table_overviews, summary=summary)


@router.get("/sessions/{session_id}/bill")
async def get_session_bill(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed bill for a session"""
    # Get session
    session_result = await db.execute(
        select(TableSession).where(TableSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get table
    table_result = await db.execute(
        select(Table).where(Table.id == session.table_id)
    )
    table = table_result.scalar_one_or_none()

    # Get all orders
    orders_result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.session_id == session_id,
            Order.status != OrderStatus.CANCELLED.value
        )
        .order_by(Order.created_at)
    )
    orders = orders_result.scalars().all()

    # Build bill items
    items = []
    subtotal = Decimal("0")

    for order in orders:
        for item in order.items:
            item_total = item.item_price * item.quantity
            subtotal += item_total
            items.append({
                "name": item.item_name,
                "quantity": item.quantity,
                "unit_price": float(item.item_price),
                "total": float(item_total),
                "notes": item.notes,
                "order_number": order.order_number
            })

    tax = subtotal * TAX_RATE
    total = subtotal + tax

    return {
        "session_id": session_id,
        "table_number": table.table_number if table else "??",
        "guest_count": session.guest_count,
        "started_at": session.started_at.isoformat(),
        "items": items,
        "subtotal": float(subtotal),
        "tax": float(tax),
        "tax_rate": float(TAX_RATE),
        "total": float(total),
        "is_paid": session.is_paid
    }


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    checkout_data: CheckoutRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process payment and close session"""
    # Get session
    session_result = await db.execute(
        select(TableSession).where(TableSession.id == checkout_data.session_id)
    )
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.is_paid:
        raise HTTPException(status_code=400, detail="Session already paid")

    # Get table
    table_result = await db.execute(
        select(Table).where(Table.id == session.table_id)
    )
    table = table_result.scalar_one_or_none()

    # Calculate total
    orders_result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.session_id == checkout_data.session_id,
            Order.status != OrderStatus.CANCELLED.value
        )
    )
    orders = orders_result.scalars().all()

    subtotal = Decimal("0")
    for order in orders:
        for item in order.items:
            subtotal += item.item_price * item.quantity

    tax = subtotal * TAX_RATE
    discount = checkout_data.discount_amount
    total = subtotal + tax - discount

    # Calculate change for cash
    change = None
    if checkout_data.payment_method == PaymentMethod.cash and checkout_data.received_amount:
        if checkout_data.received_amount < total:
            raise HTTPException(status_code=400, detail="Insufficient payment")
        change = checkout_data.received_amount - total

    # Mark session as paid
    now = datetime.utcnow()
    session.is_paid = True
    session.ended_at = now
    session.total_amount = total

    # Generate receipt number
    receipt_number = f"R{now.strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"

    await db.commit()

    return CheckoutResponse(
        session_id=checkout_data.session_id,
        table_number=table.table_number if table else "??",
        subtotal=subtotal,
        tax=tax,
        discount=discount,
        total=total,
        payment_method=checkout_data.payment_method.value,
        change=change,
        receipt_number=receipt_number,
        completed_at=now
    )


@router.post("/tables/{table_id}/close")
async def close_table(
    table_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Close table and end session after cleanup"""
    # Find active session
    session_result = await db.execute(
        select(TableSession).where(
            TableSession.table_id == table_id,
            TableSession.ended_at.is_(None)
        )
    )
    session = session_result.scalar_one_or_none()

    if not session:
        return {"message": "No active session", "table_id": table_id}

    if not session.is_paid:
        raise HTTPException(status_code=400, detail="Session not paid yet")

    session.ended_at = datetime.utcnow()
    await db.commit()

    return {"message": "Table closed", "table_id": table_id}
