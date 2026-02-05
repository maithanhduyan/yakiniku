"""
Booking Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class BookingStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no_show"
    checked_in = "checked_in"


class BookingCreate(BaseModel):
    branch_code: str = "hirama"
    date: date
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$")  # "18:00"
    guests: int = Field(..., ge=1, le=20)
    guest_name: str = Field(..., min_length=1, max_length=255)
    guest_phone: str = Field(..., min_length=10, max_length=20)
    guest_email: Optional[str] = None
    note: Optional[str] = None
    source: str = "web"


class BookingUpdate(BaseModel):
    date: Optional[date] = None
    time: Optional[str] = None
    guests: Optional[int] = None
    status: Optional[BookingStatusEnum] = None
    note: Optional[str] = None
    staff_note: Optional[str] = None
    assigned_table_id: Optional[str] = None


class BookingResponse(BaseModel):
    id: str
    branch_code: str
    date: date
    time: str
    guests: int
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    status: str
    note: Optional[str] = None
    staff_note: Optional[str] = None
    qr_token: Optional[str] = None
    assigned_table_id: Optional[str] = None
    checked_in_at: Optional[datetime] = None
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class BookingWithQR(BookingResponse):
    """Booking response with QR code URL"""
    qr_code_url: str  # Full URL to QR code image or data

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    bookings: list[BookingResponse]
    total: int
    date: Optional[date] = None

