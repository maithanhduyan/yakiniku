"""
Booking Schemas
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class BookingCreate(BaseModel):
    """Schema for creating a booking"""
    date: date
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$", examples=["18:00"])
    guests: int = Field(..., ge=1, le=20)
    guest_name: str = Field(..., min_length=1, max_length=255)
    guest_phone: str = Field(..., min_length=10, max_length=20)
    guest_email: Optional[str] = None
    note: Optional[str] = None
    branch_code: str = "hirama"


class BookingUpdate(BaseModel):
    """Schema for updating a booking"""
    status: Optional[BookingStatus] = None
    note: Optional[str] = None
    staff_note: Optional[str] = None


class BookingResponse(BaseModel):
    """Schema for booking response"""
    id: str
    branch_code: str
    date: date
    time: str
    guests: int
    guest_name: str
    guest_phone: str
    guest_email: Optional[str]
    status: str
    note: Optional[str]
    staff_note: Optional[str]
    source: str
    created_at: str

    model_config = {"from_attributes": True}

