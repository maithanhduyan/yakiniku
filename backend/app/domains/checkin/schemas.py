"""
Check-in Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


class WaitingStatusEnum(str, Enum):
    waiting = "waiting"
    called = "called"
    seated = "seated"
    cancelled = "cancelled"
    no_show = "no_show"


class CheckInType(str, Enum):
    booking = "booking"      # CÃ³ Ä‘áº·t trÆ°á»›c
    walkin = "walkin"        # KhÃ¡ch vÃ£ng lai


# QR Scan response
class QRScanResult(BaseModel):
    success: bool
    check_in_type: CheckInType
    message: str  # Japanese message to display

    # Booking info (if booking)
    booking_id: Optional[str] = None
    guest_name: Optional[str] = None
    guest_count: Optional[int] = None
    booking_time: Optional[str] = None

    # Table assignment
    table_assigned: bool = False
    table_number: Optional[str] = None
    table_zone: Optional[str] = None

    # Waiting info (if need to wait)
    need_to_wait: bool = False
    queue_number: Optional[int] = None
    estimated_wait_minutes: Optional[int] = None
    waiting_ahead: Optional[int] = None  # Number of groups ahead


# Walk-in registration
class WalkInRegister(BaseModel):
    branch_code: str = "hirama"
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_phone: Optional[str] = None
    guest_count: int = Field(..., ge=1, le=20)
    note: Optional[str] = None


class WaitingResponse(BaseModel):
    id: str
    queue_number: int
    customer_name: str
    guest_count: int
    status: WaitingStatusEnum
    estimated_wait_minutes: Optional[int] = None
    waiting_ahead: int
    created_at: datetime

    class Config:
        from_attributes = True


class WaitingListResponse(BaseModel):
    waiting: list[WaitingResponse]
    total_waiting: int
    average_wait_minutes: Optional[int] = None


# Table assignment
class TableAssignment(BaseModel):
    table_id: str
    booking_id: Optional[str] = None
    waiting_id: Optional[str] = None


class TableAssignmentResult(BaseModel):
    success: bool
    table_number: str
    table_zone: Optional[str] = None
    session_id: str
    message: str


# Dashboard for check-in screen
class CheckInDashboard(BaseModel):
    # Today's bookings
    upcoming_bookings: list[dict]

    # Current waiting list
    waiting_list: list[WaitingResponse]

    # Available tables
    available_tables: list[dict]

    # Stats
    stats: dict  # checked_in_today, waiting_count, available_tables_count

