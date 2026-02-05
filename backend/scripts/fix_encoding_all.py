"""
Fix encoding for all files with mojibake (corrupted Japanese text)
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# ============================================
# CHECKIN ROUTER - Japanese messages
# ============================================
CHECKIN_ROUTER = '''"""
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
            message="予約が見つかりませんでした。\\nスタッフにお声がけください。"
        )

    # Check booking date
    today = date.today()
    if booking.date != today:
        if booking.date < today:
            return QRScanResult(
                success=False,
                check_in_type=CheckInType.booking,
                message=f"この予約は {booking.date} でした。\\nスタッフにお声がけください。"
            )
        else:
            return QRScanResult(
                success=False,
                check_in_type=CheckInType.booking,
                message=f"予約日は {booking.date} です。\\n当日にお越しください。",
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
                message=f"既にチェックイン済みです。\\nお席へどうぞ。",
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
            message=f"{booking.guest_name}様\\nいらっしゃいませ！\\n\\nお席へご案内いたします。",
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
            message=f"{booking.guest_name}様\\nいらっしゃいませ！\\n\\n只今満席のため、少々お待ちください。",
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
        message=f"テーブル {table.table_number} に案内しました"
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
        "message": f"番号 {waiting.queue_number} - {waiting.customer_name}様をお呼びしました",
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
'''

# ============================================
# CHECKIN SCHEMAS
# ============================================
CHECKIN_SCHEMAS = '''"""
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
    booking = "booking"      # 予約あり
    walkin = "walkin"        # ウォークイン


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
    stats: Optional[dict] = None
'''

# ============================================
# CHECKIN MODELS
# ============================================
CHECKIN_MODELS = '''"""
Check-in Models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class WaitingStatus(str, enum.Enum):
    WAITING = "waiting"         # 待機中
    CALLED = "called"           # 呼び出し済み
    SEATED = "seated"           # 着席済み
    CANCELLED = "cancelled"     # キャンセル
    NO_SHOW = "no_show"         # 来店なし


class WaitingList(Base):
    """Waiting list for walk-in customers"""
    __tablename__ = "waiting_list"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Customer info
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20))
    guest_count = Column(Integer, nullable=False)

    # Queue management
    queue_number = Column(Integer, nullable=False)  # 順番
    status = Column(String(20), default=WaitingStatus.WAITING.value, index=True)

    # Estimated wait time
    estimated_wait_minutes = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    called_at = Column(DateTime(timezone=True))
    seated_at = Column(DateTime(timezone=True))

    # Link to table when seated
    assigned_table_id = Column(String(36), ForeignKey("tables.id"))

    # Notes
    note = Column(String(500))


class CheckInLog(Base):
    """Log all check-in events for analytics"""
    __tablename__ = "checkin_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Event type
    event_type = Column(String(50), nullable=False, index=True)
    # Types: booking_checkin, walkin_registered, table_assigned,
    #        customer_called, customer_seated, customer_left

    # Related entities
    booking_id = Column(String(36), ForeignKey("bookings.id"))
    waiting_id = Column(String(36), ForeignKey("waiting_list.id"))
    table_id = Column(String(36), ForeignKey("tables.id"))

    # Details
    customer_name = Column(String(255))
    guest_count = Column(Integer)

    # Context
    event_data = Column(Text)  # JSON string for additional data

    created_at = Column(DateTime(timezone=True), server_default=func.now())
'''

# ============================================
# POS SCHEMAS
# ============================================
POS_SCHEMAS = '''"""
POS Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    paypay = "paypay"
    linepay = "linepay"


class TableStatusEnum(str, Enum):
    available = "available"    # 空席
    occupied = "occupied"      # 使用中
    pending_payment = "pending_payment"  # 未会計
    cleaning = "cleaning"      # 清掃中


class CheckoutRequest(BaseModel):
    session_id: str
    payment_method: PaymentMethod
    discount_amount: Decimal = Decimal("0")
    discount_reason: Optional[str] = None
    received_amount: Optional[Decimal] = None  # For cash payment


class CheckoutResponse(BaseModel):
    session_id: str
    table_number: str
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    payment_method: str
    change: Optional[Decimal] = None
    receipt_number: str
    completed_at: datetime


class TableOverview(BaseModel):
    id: str
    table_number: str
    capacity: int
    zone: Optional[str] = None
    status: TableStatusEnum
    session_id: Optional[str] = None
    guest_count: Optional[int] = None
    current_total: Decimal = Decimal("0")
    started_at: Optional[datetime] = None
    order_count: int = 0


class POSDashboard(BaseModel):
    tables: list[TableOverview]
    summary: dict  # occupied, available, pending_payment counts
'''

# ============================================
# MENU MODEL
# ============================================
MENU_MODEL = '''"""
Menu Model - Menu items and categories
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Numeric
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class MenuCategory(str, enum.Enum):
    MEAT = "meat"           # 肉類
    DRINKS = "drinks"       # 飲物
    SALAD = "salad"         # サラダ
    RICE = "rice"           # ご飯・麺
    SIDE = "side"           # サイドメニュー
    DESSERT = "dessert"     # デザート
    SET = "set"             # セットメニュー


class MenuItem(Base):
    """Menu item configuration"""
    __tablename__ = "menu_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Item identity
    name = Column(String(100), nullable=False)          # 上ハラミ
    name_en = Column(String(100))                       # Premium Harami
    description = Column(Text)                          # 説明

    # Category & Display
    category = Column(String(30), nullable=False, index=True)  # meat, drinks, etc.
    subcategory = Column(String(50))                    # beef, pork, chicken
    display_order = Column(Integer, default=0)          # Sort order in menu

    # Pricing
    price = Column(Numeric(10, 0), nullable=False)      # ¥1,800
    tax_rate = Column(Numeric(4, 2), default=10.0)      # 10%

    # Image
    image_url = Column(String(500))                     # Image path

    # Kitchen info
    prep_time_minutes = Column(Integer, default=5)      # Estimated prep time
    kitchen_note = Column(String(200))                  # Instructions for kitchen

    # Flags
    is_available = Column(Boolean, default=True)        # Currently available
    is_popular = Column(Boolean, default=False)         # Show as recommended
    is_spicy = Column(Boolean, default=False)           # 辛い
    is_vegetarian = Column(Boolean, default=False)      # ベジタリアン
    allergens = Column(String(200))                     # egg, milk, wheat, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<MenuItem {self.name} ¥{self.price}>"
'''

# ============================================
# BRANCH CUSTOMERS CSV
# ============================================
BRANCH_CUSTOMERS_CSV = """global_customer_id,branch_code,visit_count,last_visit,is_vip,notes,sentiment
cust-001,hirama,15,2025-12-20 19:30:00,true,常連様。いつもタン塩を注文される,positive
cust-002,hirama,8,2025-11-15 18:00:00,false,お子様連れで来店。個室希望,positive
cust-003,hirama,3,2025-10-01 20:00:00,false,初回割引利用,neutral
cust-004,hirama,22,2026-01-10 19:00:00,true,VIP。特別なお祝いでよく利用,very_positive
cust-005,hirama,1,2025-08-05 18:30:00,false,一度きりの来店,neutral
cust-006,hirama,12,2025-12-01 20:30:00,true,肉の焼き加減にこだわる。レア希望,positive
cust-007,hirama,5,2025-09-20 19:00:00,false,アレルギー（甲殻類）あり,neutral
cust-008,hirama,18,2026-01-25 18:30:00,true,ワイン好き。記念日利用多し,very_positive
cust-009,hirama,2,2025-07-10 19:30:00,false,クーポン利用のみ,neutral
cust-010,hirama,10,2025-11-30 20:00:00,true,大人数宴会でよく予約,positive
cust-011,hirama,1,2025-06-01 18:00:00,false,料理の提供が遅いとクレーム,negative
cust-012,hirama,7,2025-10-15 19:00:00,false,静かな席希望。デート利用,positive
cust-013,hirama,4,2025-09-05 18:30:00,false,辛いもの好き,neutral
cust-014,hirama,20,2026-02-01 19:30:00,true,会社の接待でよく利用。上質な肉希望,very_positive
cust-015,hirama,3,2025-08-20 20:00:00,false,ベジタリアン向けメニュー希望,neutral
cust-016,hirama,1,2025-07-15 18:00:00,false,予約時間に遅刻。30分待ち,neutral
cust-017,hirama,9,2025-11-10 19:00:00,false,写真撮影好き。インスタ投稿,positive
cust-018,hirama,25,2026-01-20 20:30:00,true,創業時からの常連様。最高級コース,very_positive
cust-019,hirama,2,2025-08-01 18:30:00,false,価格について質問多い,neutral
cust-020,hirama,6,2025-10-05 19:00:00,false,禁煙席希望。匂いに敏感,positive
cust-021,hirama,1,2025-06-20 18:00:00,false,サービスに不満。二度と来ないと発言,very_negative
cust-022,hirama,11,2025-12-10 19:30:00,true,誕生日ケーキ持ち込み許可済,positive
cust-023,hirama,4,2025-09-15 20:00:00,false,飲み放題プラン好き,neutral
cust-024,hirama,8,2025-11-01 18:30:00,false,子供用メニュー注文,positive
cust-025,hirama,2,2025-07-25 19:00:00,false,前回の会計ミスで返金対応済,neutral
cust-026,hirama,15,2025-12-25 20:00:00,true,クリスマス毎年予約。ロマンチックな席希望,very_positive
cust-027,hirama,1,2025-06-10 18:00:00,false,メニューが分かりにくいとフィードバック,neutral
cust-028,hirama,7,2025-10-20 19:30:00,false,ホルモン専門。通な注文,positive
cust-029,hirama,3,2025-08-15 18:30:00,false,早めの時間帯希望。高齢者同伴,neutral
cust-030,hirama,19,2026-01-15 20:00:00,true,ワイン会幹事。大口注文,very_positive
cust-031,hirama,2,2025-07-05 19:00:00,false,席が狭いとコメント,negative
cust-032,hirama,10,2025-11-20 18:00:00,true,スポーツ選手。タンパク質重視,positive
cust-033,hirama,5,2025-09-25 19:30:00,false,デザート追加注文多し,positive
cust-034,hirama,1,2025-06-25 20:00:00,false,予約キャンセル歴あり（無断）,negative
cust-035,hirama,12,2025-12-05 18:30:00,true,日本酒詳しい。銘柄指定,positive
cust-036,hirama,4,2025-09-10 19:00:00,false,外国人ゲスト同伴。英語メニュー必要,neutral
cust-037,hirama,6,2025-10-10 20:00:00,false,赤ちゃん連れ。ベビーカー,positive
cust-038,hirama,1,2025-06-15 18:00:00,false,量が少ないとクレーム,negative
cust-039,hirama,8,2025-11-05 19:30:00,false,女子会利用。サラダ多め,positive
cust-040,hirama,16,2025-12-30 20:00:00,true,年末年始は必ず予約,very_positive
cust-041,hirama,3,2025-08-10 18:30:00,false,支払い分割希望,neutral
cust-042,hirama,7,2025-10-25 19:00:00,false,スタッフの対応を褒めてくれた,positive
cust-043,hirama,2,2025-07-20 20:00:00,false,駐車場について質問,neutral
cust-044,hirama,13,2025-12-15 18:00:00,true,法人カード利用。領収書必要,positive
cust-045,hirama,5,2025-09-30 19:30:00,false,アニバーサリープレート希望,positive
cust-046,hirama,1,2025-06-30 18:30:00,false,料理が冷たいとクレーム,negative
cust-047,hirama,9,2025-11-25 20:00:00,false,焼肉のたれ追加注文多し,neutral
cust-048,hirama,4,2025-09-01 19:00:00,false,静かで落ち着いた雰囲気を評価,positive
cust-049,hirama,2,2025-07-30 18:00:00,false,クーポンサイト経由,neutral
cust-050,hirama,21,2026-01-05 19:30:00,true,最重要VIP。社長秘書から予約,very_positive
"""


def fix_all_files():
    """Fix all files with encoding issues"""

    # 1. Fix checkin router
    checkin_router_path = BASE_DIR / "app" / "domains" / "checkin" / "router.py"
    with open(checkin_router_path, 'w', encoding='utf-8') as f:
        f.write(CHECKIN_ROUTER)
    print(f"✅ Fixed {checkin_router_path}")

    # 2. Fix checkin schemas
    checkin_schemas_path = BASE_DIR / "app" / "domains" / "checkin" / "schemas.py"
    with open(checkin_schemas_path, 'w', encoding='utf-8') as f:
        f.write(CHECKIN_SCHEMAS)
    print(f"✅ Fixed {checkin_schemas_path}")

    # 3. Fix checkin models
    checkin_models_path = BASE_DIR / "app" / "domains" / "checkin" / "models.py"
    with open(checkin_models_path, 'w', encoding='utf-8') as f:
        f.write(CHECKIN_MODELS)
    print(f"✅ Fixed {checkin_models_path}")

    # 4. Fix POS schemas
    pos_schemas_path = BASE_DIR / "app" / "domains" / "pos" / "schemas.py"
    with open(pos_schemas_path, 'w', encoding='utf-8') as f:
        f.write(POS_SCHEMAS)
    print(f"✅ Fixed {pos_schemas_path}")

    # 5. Fix menu model
    menu_model_path = BASE_DIR / "app" / "models" / "menu.py"
    with open(menu_model_path, 'w', encoding='utf-8') as f:
        f.write(MENU_MODEL)
    print(f"✅ Fixed {menu_model_path}")

    # 6. Fix branch_customers.csv
    branch_customers_path = BASE_DIR / "data" / "branch_customers.csv"
    with open(branch_customers_path, 'w', encoding='utf-8') as f:
        f.write(BRANCH_CUSTOMERS_CSV.strip())
    print(f"✅ Fixed {branch_customers_path}")

    print("\n✅ All encoding issues fixed!")


if __name__ == "__main__":
    fix_all_files()
