"""
Check-in Router - Customer Reception APIs
Team: checkin
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, date, timedelta
from typing import Optional
import json

from app.database import get_db
from app.domains.checkin.models import WaitingList, WaitingStatus, CheckInLog
from app.domains.checkin.schemas import (
    QRScanResult, CheckInType, WalkInRegister, WaitingResponse,
    WaitingListResponse, TableAssignment, TableAssignmentResult,
    CheckInDashboard, WaitingStatusEnum
)
from app.domains.booking.models import Booking, BookingStatus
from app.domains.tableorder.models import TableSession
from app.domains.shared.models import Table

router = APIRouter()


@router.post("/scan", response_model=QRScanResult)
async def scan_qr_code(
    qr_token: str,
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """
    Scan QR code for check-in
    Returns table assignment or waiting info
    """
    # Find booking by QR token
    result = await db.execute(
        select(Booking).where(
            Booking.qr_token == qr_token,
            Booking.branch_code == branch_code
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        return QRScanResult(
            success=False,
            check_in_type=CheckInType.booking,
            message="äºˆç´„ãŒè¦‹ã¤ã‹ã‚Šã¾ã›ã‚“ã§ã—ãŸã€‚\nã‚¹ã‚¿ãƒƒãƒ•ã«ãŠå£°ãŒã‘ãã ã•ã„ã€‚"
        )

    # Check booking date
    today = date.today()
    if booking.date != today:
        if booking.date < today:
            return QRScanResult(
                success=False,
                check_in_type=CheckInType.booking,
                message=f"ã“ã®äºˆç´„ã¯ {booking.date} ã§ã—ãŸã€‚\nã‚¹ã‚¿ãƒƒãƒ•ã«ãŠå£°ãŒã‘ãã ã•ã„ã€‚"
            )
        else:
            return QRScanResult(
                success=False,
                check_in_type=CheckInType.booking,
                message=f"äºˆç´„æ—¥ã¯ {booking.date} ã§ã™ã€‚\nå½“æ—¥ã«ãŠè¶Šã—ãã ã•ã„ã€‚",
                booking_id=booking.id,
                guest_name=booking.guest_name,
                booking_time=booking.time
            )

    # Check if already checked in
    if booking.status == BookingStatus.CHECKED_IN.value:
        if booking.assigned_table_id:
            table = await get_table(db, booking.assigned_table_id)
            return QRScanResult(
                success=True,
                check_in_type=CheckInType.booking,
                message=f"æ—¢ã«ãƒã‚§ãƒƒã‚¯ã‚¤ãƒ³æ¸ˆã¿ã§ã™ã€‚\nãŠå¸­ã¸ã©ã†ãžã€‚",
                booking_id=booking.id,
                guest_name=booking.guest_name,
                guest_count=booking.guests,
                table_assigned=True,
                table_number=table.table_number if table else None,
                table_zone=table.zone if table else None
            )

    # Try to find available table
    available_table = await find_available_table(db, branch_code, booking.guests)

    if available_table:
        # Assign table immediately
        booking.status = BookingStatus.CHECKED_IN.value
        booking.assigned_table_id = available_table.id
        booking.checked_in_at = datetime.utcnow()

        # Create session
        session = TableSession(
            branch_code=branch_code,
            table_id=available_table.id,
            booking_id=booking.id,
            guest_count=booking.guests
        )
        db.add(session)

        # Log check-in
        await log_checkin_event(
            db, branch_code, "booking_checkin",
            booking_id=booking.id,
            table_id=available_table.id,
            customer_name=booking.guest_name,
            guest_count=booking.guests
        )

        await db.commit()

        return QRScanResult(
            success=True,
            check_in_type=CheckInType.booking,
            message=f"{booking.guest_name}æ§˜\nã„ã‚‰ã£ã—ã‚ƒã„ã¾ã›ï¼\n\nãŠå¸­ã¸ã”æ¡ˆå†…ã„ãŸã—ã¾ã™ã€‚",
            booking_id=booking.id,
            guest_name=booking.guest_name,
            guest_count=booking.guests,
            booking_time=booking.time,
            table_assigned=True,
            table_number=available_table.table_number,
            table_zone=available_table.zone
        )
    else:
        # Need to wait
        queue_info = await get_queue_info(db, branch_code)

        return QRScanResult(
            success=True,
            check_in_type=CheckInType.booking,
            message=f"{booking.guest_name}æ§˜\nã„ã‚‰ã£ã—ã‚ƒã„ã¾ã›ï¼\n\nåªä»Šæº€å¸­ã®ãŸã‚ã€å°‘ã€…ãŠå¾…ã¡ãã ã•ã„ã€‚",
            booking_id=booking.id,
            guest_name=booking.guest_name,
            guest_count=booking.guests,
            booking_time=booking.time,
            table_assigned=False,
            need_to_wait=True,
            estimated_wait_minutes=queue_info["estimated_wait"],
            waiting_ahead=queue_info["waiting_count"]
        )


@router.post("/walkin", response_model=WaitingResponse)
async def register_walkin(
    data: WalkInRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a walk-in customer to waiting list"""
    # Get next queue number
    result = await db.execute(
        select(func.max(WaitingList.queue_number)).where(
            WaitingList.branch_code == data.branch_code,
            func.date(WaitingList.created_at) == date.today()
        )
    )
    max_queue = result.scalar() or 0

    # Calculate estimated wait
    queue_info = await get_queue_info(db, data.branch_code)

    # Create waiting entry
    waiting = WaitingList(
        branch_code=data.branch_code,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        guest_count=data.guest_count,
        queue_number=max_queue + 1,
        estimated_wait_minutes=queue_info["estimated_wait"],
        note=data.note
    )

    db.add(waiting)

    # Log event
    await log_checkin_event(
        db, data.branch_code, "walkin_registered",
        waiting_id=waiting.id,
        customer_name=data.customer_name,
        guest_count=data.guest_count
    )

    await db.commit()
    await db.refresh(waiting)

    return WaitingResponse(
        id=waiting.id,
        queue_number=waiting.queue_number,
        customer_name=waiting.customer_name,
        guest_count=waiting.guest_count,
        status=WaitingStatusEnum(waiting.status),
        estimated_wait_minutes=waiting.estimated_wait_minutes,
        waiting_ahead=queue_info["waiting_count"],
        created_at=waiting.created_at
    )


@router.get("/waiting", response_model=WaitingListResponse)
async def get_waiting_list(
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """Get current waiting list"""
    result = await db.execute(
        select(WaitingList).where(
            WaitingList.branch_code == branch_code,
            WaitingList.status.in_([WaitingStatus.WAITING.value, WaitingStatus.CALLED.value]),
            func.date(WaitingList.created_at) == date.today()
        ).order_by(WaitingList.queue_number)
    )
    waiting_list = result.scalars().all()

    responses = []
    for i, w in enumerate(waiting_list):
        responses.append(WaitingResponse(
            id=w.id,
            queue_number=w.queue_number,
            customer_name=w.customer_name,
            guest_count=w.guest_count,
            status=WaitingStatusEnum(w.status),
            estimated_wait_minutes=w.estimated_wait_minutes,
            waiting_ahead=i,
            created_at=w.created_at
        ))

    # Calculate average wait
    avg_wait = None
    if waiting_list:
        total_wait = sum(w.estimated_wait_minutes or 15 for w in waiting_list)
        avg_wait = total_wait // len(waiting_list)

    return WaitingListResponse(
        waiting=responses,
        total_waiting=len(responses),
        average_wait_minutes=avg_wait
    )


@router.post("/assign-table", response_model=TableAssignmentResult)
async def assign_table(
    assignment: TableAssignment,
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """Assign a table to booking or waiting customer"""
    # Get table
    table = await get_table(db, assignment.table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Check if table is available
    is_available = await check_table_available(db, assignment.table_id)
    if not is_available:
        raise HTTPException(status_code=400, detail="Table is not available")

    customer_name = ""
    guest_count = 1
    booking_id = None
    waiting_id = None

    if assignment.booking_id:
        # Assign to booking
        result = await db.execute(
            select(Booking).where(Booking.id == assignment.booking_id)
        )
        booking = result.scalar_one_or_none()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        booking.status = BookingStatus.CHECKED_IN.value
        booking.assigned_table_id = assignment.table_id
        booking.checked_in_at = datetime.utcnow()

        customer_name = booking.guest_name
        guest_count = booking.guests
        booking_id = booking.id

    elif assignment.waiting_id:
        # Assign to waiting customer
        result = await db.execute(
            select(WaitingList).where(WaitingList.id == assignment.waiting_id)
        )
        waiting = result.scalar_one_or_none()
        if not waiting:
            raise HTTPException(status_code=404, detail="Waiting entry not found")

        waiting.status = WaitingStatus.SEATED.value
        waiting.assigned_table_id = assignment.table_id
        waiting.seated_at = datetime.utcnow()

        customer_name = waiting.customer_name
        guest_count = waiting.guest_count
        waiting_id = waiting.id

    # Create table session
    session = TableSession(
        branch_code=branch_code,
        table_id=assignment.table_id,
        booking_id=booking_id,
        guest_count=guest_count
    )
    db.add(session)

    # Log event
    await log_checkin_event(
        db, branch_code, "table_assigned",
        booking_id=booking_id,
        waiting_id=waiting_id,
        table_id=assignment.table_id,
        customer_name=customer_name,
        guest_count=guest_count
    )

    await db.commit()
    await db.refresh(session)

    return TableAssignmentResult(
        success=True,
        table_number=table.table_number,
        table_zone=table.zone,
        session_id=session.id,
        message=f"ãƒ†ãƒ¼ãƒ–ãƒ« {table.table_number} ã«æ¡ˆå†…ã—ã¾ã—ãŸ"
    )


@router.post("/waiting/{waiting_id}/call")
async def call_waiting_customer(
    waiting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Call next waiting customer"""
    result = await db.execute(
        select(WaitingList).where(WaitingList.id == waiting_id)
    )
    waiting = result.scalar_one_or_none()

    if not waiting:
        raise HTTPException(status_code=404, detail="Waiting entry not found")

    waiting.status = WaitingStatus.CALLED.value
    waiting.called_at = datetime.utcnow()

    await db.commit()

    return {
        "message": f"ç•ªå· {waiting.queue_number} - {waiting.customer_name}æ§˜ã‚’ãŠå‘¼ã³ã—ã¾ã—ãŸ",
        "queue_number": waiting.queue_number,
        "customer_name": waiting.customer_name
    }


@router.get("/dashboard", response_model=CheckInDashboard)
async def get_checkin_dashboard(
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """Get check-in dashboard data"""
    today = date.today()
    now = datetime.now()

    # Get today's upcoming bookings (confirmed, not yet checked in)
    bookings_result = await db.execute(
        select(Booking).where(
            Booking.branch_code == branch_code,
            Booking.date == today,
            Booking.status.in_([
                BookingStatus.PENDING.value,
                BookingStatus.CONFIRMED.value
            ])
        ).order_by(Booking.time)
    )
    bookings = bookings_result.scalars().all()

    upcoming_bookings = [
        {
            "id": b.id,
            "time": b.time,
            "guest_name": b.guest_name,
            "guest_count": b.guests,
            "phone": b.guest_phone,
            "status": b.status,
            "note": b.note
        }
        for b in bookings
    ]

    # Get waiting list
    waiting_result = await db.execute(
        select(WaitingList).where(
            WaitingList.branch_code == branch_code,
            WaitingList.status.in_([WaitingStatus.WAITING.value, WaitingStatus.CALLED.value]),
            func.date(WaitingList.created_at) == today
        ).order_by(WaitingList.queue_number)
    )
    waiting_entries = waiting_result.scalars().all()

    waiting_list = [
        WaitingResponse(
            id=w.id,
            queue_number=w.queue_number,
            customer_name=w.customer_name,
            guest_count=w.guest_count,
            status=WaitingStatusEnum(w.status),
            estimated_wait_minutes=w.estimated_wait_minutes,
            waiting_ahead=i,
            created_at=w.created_at
        )
        for i, w in enumerate(waiting_entries)
    ]

    # Get available tables
    tables_result = await db.execute(
        select(Table).where(
            Table.branch_code == branch_code,
            Table.is_active == True
        ).order_by(Table.table_number)
    )
    all_tables = tables_result.scalars().all()

    available_tables = []
    for table in all_tables:
        if await check_table_available(db, table.id):
            available_tables.append({
                "id": table.id,
                "table_number": table.table_number,
                "capacity": table.capacity,
                "zone": table.zone
            })

    # Stats
    checked_in_result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.branch_code == branch_code,
            Booking.date == today,
            Booking.status == BookingStatus.CHECKED_IN.value
        )
    )
    checked_in_count = checked_in_result.scalar() or 0

    return CheckInDashboard(
        upcoming_bookings=upcoming_bookings,
        waiting_list=waiting_list,
        available_tables=available_tables,
        stats={
            "checked_in_today": checked_in_count,
            "waiting_count": len(waiting_list),
            "available_tables_count": len(available_tables),
            "upcoming_bookings_count": len(upcoming_bookings)
        }
    )


# Helper functions
async def get_table(db: AsyncSession, table_id: str) -> Optional[Table]:
    result = await db.execute(select(Table).where(Table.id == table_id))
    return result.scalar_one_or_none()


async def check_table_available(db: AsyncSession, table_id: str) -> bool:
    """Check if table has no active session"""
    result = await db.execute(
        select(TableSession).where(
            TableSession.table_id == table_id,
            TableSession.ended_at.is_(None)
        )
    )
    session = result.scalar_one_or_none()
    return session is None


async def find_available_table(
    db: AsyncSession,
    branch_code: str,
    guest_count: int
) -> Optional[Table]:
    """Find best available table for guest count"""
    result = await db.execute(
        select(Table).where(
            Table.branch_code == branch_code,
            Table.is_active == True,
            Table.capacity >= guest_count
        ).order_by(Table.capacity)  # Prefer smaller tables that fit
    )
    tables = result.scalars().all()

    for table in tables:
        if await check_table_available(db, table.id):
            return table

    return None


async def get_queue_info(db: AsyncSession, branch_code: str) -> dict:
    """Get current queue information"""
    result = await db.execute(
        select(func.count(WaitingList.id)).where(
            WaitingList.branch_code == branch_code,
            WaitingList.status == WaitingStatus.WAITING.value,
            func.date(WaitingList.created_at) == date.today()
        )
    )
    waiting_count = result.scalar() or 0

    # Estimate ~15 min per group
    estimated_wait = waiting_count * 15

    return {
        "waiting_count": waiting_count,
        "estimated_wait": estimated_wait
    }


async def log_checkin_event(
    db: AsyncSession,
    branch_code: str,
    event_type: str,
    booking_id: str = None,
    waiting_id: str = None,
    table_id: str = None,
    customer_name: str = None,
    guest_count: int = None,
    event_data: dict = None
):
    """Log check-in event"""
    log = CheckInLog(
        branch_code=branch_code,
        event_type=event_type,
        booking_id=booking_id,
        waiting_id=waiting_id,
        table_id=table_id,
        customer_name=customer_name,
        guest_count=guest_count,
        event_data=json.dumps(event_data) if event_data else None
    )
    db.add(log)
