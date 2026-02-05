"""
Booking Router - Web Booking APIs
Team: web
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime
from typing import Optional
import secrets

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.domains.booking.schemas import (
    BookingCreate, BookingResponse, BookingUpdate,
    BookingListResponse
)

router = APIRouter()


@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new booking"""
    booking = Booking(
        branch_code=booking_data.branch_code,
        date=booking_data.date,
        time=booking_data.time,
        guests=booking_data.guests,
        guest_name=booking_data.guest_name,
        guest_phone=booking_data.guest_phone,
        guest_email=booking_data.guest_email,
        note=booking_data.note,
        source=booking_data.source,
        status=BookingStatus.PENDING.value
    )

    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    return BookingResponse.model_validate(booking)


@router.get("/", response_model=BookingListResponse)
async def list_bookings(
    branch_code: str = "hirama",
    booking_date: Optional[date] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List bookings with optional filters"""
    query = select(Booking).where(Booking.branch_code == branch_code)

    if booking_date:
        query = query.where(Booking.date == booking_date)
    if status:
        query = query.where(Booking.status == status)

    query = query.order_by(Booking.date, Booking.time)

    result = await db.execute(query)
    bookings = result.scalars().all()

    return BookingListResponse(
        bookings=[BookingResponse.model_validate(b) for b in bookings],
        total=len(bookings),
        date=booking_date
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get booking by ID"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return BookingResponse.model_validate(booking)


@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    update_data: BookingUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update booking details"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(booking, field, value)

    await db.commit()
    await db.refresh(booking)

    return BookingResponse.model_validate(booking)


@router.post("/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Confirm a pending booking"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != BookingStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Booking is not pending")

    booking.status = BookingStatus.CONFIRMED.value
    await db.commit()
    await db.refresh(booking)

    return BookingResponse.model_validate(booking)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a booking"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = BookingStatus.CANCELLED.value
    await db.commit()
    await db.refresh(booking)

    return BookingResponse.model_validate(booking)


@router.get("/qr/{qr_token}", response_model=BookingResponse)
async def get_booking_by_qr(
    qr_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get booking by QR token (for check-in)"""
    result = await db.execute(
        select(Booking).where(Booking.qr_token == qr_token)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Invalid QR code")

    return BookingResponse.model_validate(booking)

