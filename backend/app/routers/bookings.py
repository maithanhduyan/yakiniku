"""
Bookings Router - CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date
from typing import List, Optional

from app.database import get_db
from app.models.booking import Booking
from app.models.table import Table, TableAssignment
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.services.notification_service import notify_new_booking, notify_booking_cancelled, notify_booking_confirmed
from app.services.table_optimization import TableOptimizationService

router = APIRouter()


@router.get("/", response_model=List[BookingResponse])
async def list_bookings(
    branch_code: str = Query(default="hirama"),
    booking_date: Optional[date] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List bookings with optional filters"""
    query = select(Booking).where(Booking.branch_code == branch_code)

    if booking_date:
        query = query.where(Booking.date == booking_date)

    if status:
        query = query.where(Booking.status == status)

    query = query.order_by(Booking.date.desc(), Booking.time)

    result = await db.execute(query)
    bookings = result.scalars().all()

    return [
        BookingResponse(
            id=b.id,
            branch_code=b.branch_code,
            date=b.date,
            time=b.time,
            guests=b.guests,
            guest_name=b.guest_name or "",
            guest_phone=b.guest_phone or "",
            guest_email=b.guest_email,
            status=b.status,
            note=b.note,
            staff_note=b.staff_note,
            source=b.source,
            created_at=b.created_at.isoformat() if b.created_at else "",
        )
        for b in bookings
    ]


@router.get("/today", response_model=List[BookingResponse])
async def get_today_bookings(
    branch_code: str = Query(default="hirama"),
    db: AsyncSession = Depends(get_db),
):
    """Get today's bookings"""
    today = date.today()
    return await list_bookings(branch_code=branch_code, booking_date=today, db=db)


@router.get("/available-slots")
async def get_available_slots(
    branch_code: str = Query(default="hirama"),
    booking_date: date = Query(...),
    guests: int = Query(default=2),
    db: AsyncSession = Depends(get_db),
):
    """
    Get available time slots for a date based on actual table capacity.
    Uses AI optimization to check real availability.
    """
    # All possible slots (17:00 - 22:00, 30min intervals)
    all_slots = [
        f"{h:02d}:{m:02d}"
        for h in range(17, 23)
        for m in [0, 30]
        if not (h == 22 and m == 30)  # Last order 22:00
    ]

    # Check if we have tables configured
    tables_query = select(Table).where(
        and_(Table.branch_code == branch_code, Table.is_active == True)
    )
    tables_result = await db.execute(tables_query)
    tables = tables_result.scalars().all()

    if not tables:
        # Fallback: No tables configured, use simple booking count
        query = select(Booking.time).where(
            and_(
                Booking.branch_code == branch_code,
                Booking.date == booking_date,
                Booking.status.in_(["pending", "confirmed"]),
            )
        )
        result = await db.execute(query)
        booked_times = [r[0] for r in result.fetchall()]
        available = [slot for slot in all_slots if slot not in booked_times]

        return {
            "date": booking_date.isoformat(),
            "available_slots": available,
            "mode": "simple"
        }

    # Use AI optimization service
    optimizer = TableOptimizationService(db, branch_code)

    available_slots = []
    slot_details = []

    for slot in all_slots:
        result = await optimizer.check_availability(guests, booking_date, slot)

        if result["available"]:
            available_slots.append(slot)
            slot_details.append({
                "time": slot,
                "tables": [
                    {
                        "table_number": t.table_number,
                        "capacity": t.capacity,
                        "score": t.score
                    }
                    for t in result["tables"][:2]  # Top 2 suggestions
                ]
            })

    return {
        "date": booking_date.isoformat(),
        "available_slots": available_slots,
        "slot_details": slot_details,
        "mode": "optimized",
        "total_tables": len(tables),
        "total_capacity": sum(t.max_capacity for t in tables)
    }


@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking(
    booking: BookingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new booking with AI table optimization"""
    # Check if we have tables configured
    tables_query = select(Table).where(
        and_(Table.branch_code == booking.branch_code, Table.is_active == True)
    )
    tables_result = await db.execute(tables_query)
    tables = list(tables_result.scalars().all())

    if tables:
        # Use AI optimization to find best table
        optimizer = TableOptimizationService(db, booking.branch_code)
        availability = await optimizer.check_availability(
            booking.guests, booking.date, booking.time
        )

        if not availability["available"]:
            # Suggest alternatives
            alternatives = availability.get("alternatives", [])
            alt_times = [a["time"] for a in alternatives[:3]]

            raise HTTPException(
                status_code=409,
                detail={
                    "message": "申し訳ございません、ご希望の時間は満席です。",
                    "alternatives": alt_times,
                    "suggestion": f"代わりに {', '.join(alt_times)} はいかがでしょうか？" if alt_times else None
                }
            )
    else:
        # Fallback: Simple check (no tables configured)
        existing = await db.execute(
            select(Booking).where(
                and_(
                    Booking.branch_code == booking.branch_code,
                    Booking.date == booking.date,
                    Booking.time == booking.time,
                    Booking.status.in_(["pending", "confirmed"]),
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Time slot already booked")

    # Create booking
    db_booking = Booking(
        branch_code=booking.branch_code,
        date=booking.date,
        time=booking.time,
        guests=booking.guests,
        guest_name=booking.guest_name,
        guest_phone=booking.guest_phone,
        guest_email=booking.guest_email,
        note=booking.note,
        source="web",
    )

    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)

    # Auto-assign table if tables are configured
    assigned_table = None
    if tables:
        try:
            assignment = await optimizer.auto_assign_table(
                db_booking.id,
                booking.guests,
                booking.date,
                booking.time
            )
            if assignment:
                # Get table info
                table_query = select(Table).where(Table.id == assignment.table_id)
                table_result = await db.execute(table_query)
                assigned_table = table_result.scalar_one_or_none()
        except Exception as e:
            # Log but don't fail the booking
            print(f"Table assignment failed: {e}")

    # Send real-time notification to staff dashboard
    await notify_new_booking(
        branch_code=db_booking.branch_code,
        guest_name=db_booking.guest_name or "ゲスト",
        booking_date=db_booking.date.isoformat(),
        booking_time=db_booking.time,
        guests=db_booking.guests,
        booking_id=db_booking.id,
        table_number=assigned_table.table_number if assigned_table else None,
    )

    return BookingResponse(
        id=db_booking.id,
        branch_code=db_booking.branch_code,
        date=db_booking.date,
        time=db_booking.time,
        guests=db_booking.guests,
        guest_name=db_booking.guest_name or "",
        guest_phone=db_booking.guest_phone or "",
        guest_email=db_booking.guest_email,
        status=db_booking.status,
        note=db_booking.note,
        staff_note=db_booking.staff_note,
        source=db_booking.source,
        created_at=db_booking.created_at.isoformat() if db_booking.created_at else "",
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific booking"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return BookingResponse(
        id=booking.id,
        branch_code=booking.branch_code,
        date=booking.date,
        time=booking.time,
        guests=booking.guests,
        guest_name=booking.guest_name or "",
        guest_phone=booking.guest_phone or "",
        guest_email=booking.guest_email,
        status=booking.status,
        note=booking.note,
        staff_note=booking.staff_note,
        source=booking.source,
        created_at=booking.created_at.isoformat() if booking.created_at else "",
    )


@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    update: BookingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update booking status or notes"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if update.status:
        booking.status = update.status.value
    if update.note is not None:
        booking.note = update.note
    if update.staff_note is not None:
        booking.staff_note = update.staff_note

    await db.commit()
    await db.refresh(booking)

    return BookingResponse(
        id=booking.id,
        branch_code=booking.branch_code,
        date=booking.date,
        time=booking.time,
        guests=booking.guests,
        guest_name=booking.guest_name or "",
        guest_phone=booking.guest_phone or "",
        guest_email=booking.guest_email,
        status=booking.status,
        note=booking.note,
        staff_note=booking.staff_note,
        source=booking.source,
        created_at=booking.created_at.isoformat() if booking.created_at else "",
    )


@router.delete("/{booking_id}", status_code=204)
async def delete_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a booking"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    await db.delete(booking)
    await db.commit()
