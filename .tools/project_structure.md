# Cấu trúc Dự án như sau:

```
./backend
├── .python-version
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── domains
│   │   ├── __init__.py
│   │   ├── booking
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   └── schemas.py
│   │   ├── checkin
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   └── schemas.py
│   │   ├── kitchen
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   ├── pos
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── schemas.py
│   │   ├── shared
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   └── tableorder
│   │       ├── __init__.py
│   │       ├── event_router.py
│   │       ├── event_service.py
│   │       ├── events.py
│   │       ├── models.py
│   │       ├── router.py
│   │       └── schemas.py
│   ├── main.py
│   ├── middleware
│   ├── models
│   │   ├── __init__.py
│   │   ├── booking.py
│   │   ├── branch.py
│   │   ├── category.py
│   │   ├── chat.py
│   │   ├── combo.py
│   │   ├── customer.py
│   │   ├── item.py
│   │   ├── menu.py
│   │   ├── order.py
│   │   ├── preference.py
│   │   ├── promotion.py
│   │   ├── staff.py
│   │   └── table.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── bookings.py
│   │   ├── branches.py
│   │   ├── chat.py
│   │   ├── customers.py
│   │   ├── dashboard.py
│   │   ├── menu.py
│   │   ├── notifications.py
│   │   ├── orders.py
│   │   ├── tables.py
│   │   └── websocket.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── booking.py
│   │   ├── branch.py
│   │   ├── chat.py
│   │   ├── customer.py
│   │   ├── menu.py
│   │   └── order.py
│   └── services
│       ├── __init__.py
│       ├── chat_service.py
│       ├── notification_service.py
│       └── table_optimization.py
├── main.py
├── pyproject.toml
├── scripts
│   ├── __init__.py
│   ├── fix_encoding_all.py
│   └── seed_enhanced_menu.py
├── static
│   ├── css
│   ├── images
│   │   └── menu
│   └── js
├── uv.lock
└── yakiniku.db
```

# Danh sách chi tiết các file:

## File ./backend\main.py:
```python
def main():
    print("Hello from yakiniku-backend!")


if __name__ == "__main__":
    main()

```

## File ./backend\app\config.py:
```python
﻿"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "sqlite:///./yakiniku.db"

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5500",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:8082",
        "http://localhost:8083",
        "http://localhost:8084",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:8082",
        "http://127.0.0.1:8083",
        "http://127.0.0.1:8084",
    ]

    # Multi-tenant
    DEFAULT_BRANCH: str = "hirama"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

```

## File ./backend\app\database.py:
```python
﻿"""
Database Connection and Session Management
Async SQLAlchemy with aiosqlite/asyncpg
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Convert sync URLs to async URLs
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite:///"):
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
# postgresql+asyncpg:// is already async-ready

# Create async engine with appropriate settings
engine_kwargs = {
    "echo": False,
}
# SQLite needs special handling for async
if "sqlite" in database_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(database_url, **engine_kwargs)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency to get async DB session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    # Import all models to ensure they're registered with Base
    from app.models import booking, branch, chat, customer, menu, order, preference, staff, table
    # Import domain models
    from app.domains.checkin import models as checkin_models

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


```

## File ./backend\app\main.py:
```python
﻿"""
FastAPI Application Entry Point
"""
import signal
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.services.notification_service import notification_manager


def setup_signal_handlers():
    """Setup signal handlers to gracefully shutdown SSE before uvicorn"""
    import sys
    import time

    def sync_shutdown_handler(signum, frame):
        """Synchronous signal handler that triggers async shutdown"""
        print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
        # Set the shutdown event synchronously - SSE generators will exit on next check
        notification_manager._shutdown_event.set()

        # Give SSE connections 2 seconds to close gracefully
        print("⏳ Waiting for SSE connections to close...")
        time.sleep(2)

        # Now raise KeyboardInterrupt to let uvicorn shutdown
        raise KeyboardInterrupt

    # Register signal handlers
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, sync_shutdown_handler)
    signal.signal(signal.SIGINT, sync_shutdown_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Setup signal handlers early
    setup_signal_handlers()

    # Startup: Initialize database
    await init_db()
    print("🍖 Database initialized")
    yield
    # Shutdown: Close SSE connections first
    print("👋 Shutting down...")
    await notification_manager.shutdown()
    print("✅ Graceful shutdown complete")


app = FastAPI(
    title="Yakiniku JIAN API",
    description="Restaurant booking and customer insights API",
    version="1.0.0",
    lifespan=lifespan,
)

# Static files for menu images (backend serves images)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    print("⚠️ Static directory not found")

# CORS - allow web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Yakiniku JIAN API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ============ Legacy Routers (backward compatibility) ============
from app.routers import bookings, customers, branches, chat, dashboard, notifications, tables, menu, orders
from app.routers import websocket as ws_router

app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(branches.router, prefix="/api/branches", tags=["branches"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(tables.router, prefix="/api/tables", tags=["tables"])
app.include_router(menu.router, prefix="/api/menu", tags=["menu"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(dashboard.router, prefix="/admin", tags=["dashboard"])
app.include_router(ws_router.router, tags=["websocket"])

# ============ Domain Routers (new modular structure) ============
# Team: web
from app.domains.booking.router import router as booking_router
app.include_router(booking_router, prefix="/api/booking", tags=["booking-domain"])

# Team: table-order
from app.domains.tableorder.router import router as tableorder_router
app.include_router(tableorder_router, prefix="/api/tableorder", tags=["tableorder-domain"])

# Event Sourcing for table-order
from app.domains.tableorder.event_router import router as event_router
app.include_router(event_router, prefix="/api/events", tags=["events"])

# Team: kitchen
from app.domains.kitchen.router import router as kitchen_router
app.include_router(kitchen_router, prefix="/api/kitchen", tags=["kitchen-domain"])

# Team: pos
from app.domains.pos.router import router as pos_router
app.include_router(pos_router, prefix="/api/pos", tags=["pos-domain"])

# Team: checkin
from app.domains.checkin.router import router as checkin_router
app.include_router(checkin_router, prefix="/api/checkin", tags=["checkin-domain"])

```

## File ./backend\app\__init__.py:
```python
﻿"""
Yakiniku JIAN - Backend API
Multi-tenant restaurant booking system
"""

```

## File ./backend\app\domains\__init__.py:
```python
﻿"""
Domain modules - organized by team/feature
"""


```

## File ./backend\app\domains\booking\models.py:
```python
﻿"""
Booking Models - Re-export from legacy models with extensions
"""
# Re-export from legacy models
from app.models.booking import Booking, BookingStatus

# Add new fields to existing model using mixin approach
# For now, we'll add qr_token and check-in fields via migration later

__all__ = ["Booking", "BookingStatus"]


```

## File ./backend\app\domains\booking\router.py:
```python
﻿"""
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


```

## File ./backend\app\domains\booking\schemas.py:
```python
﻿"""
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


```

## File ./backend\app\domains\booking\__init__.py:
```python
﻿"""
Booking Domain - Web/Customer Booking System
Team: web
"""
from app.domains.booking.models import Booking, BookingStatus
from app.domains.booking.schemas import (
    BookingCreate, BookingResponse, BookingUpdate
)
from app.domains.booking.router import router

__all__ = [
    "Booking", "BookingStatus",
    "BookingCreate", "BookingResponse", "BookingUpdate",
    "router"
]


```

## File ./backend\app\domains\checkin\models.py:
```python
"""
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

```

## File ./backend\app\domains\checkin\router.py:
```python
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
            message="予約が見つかりませんでした。\nスタッフにお声がけください。"
        )

    # Check booking date
    today = date.today()
    if booking.date != today:
        if booking.date < today:
            return QRScanResult(
                success=False,
                check_in_type=CheckInType.booking,
                message=f"この予約は {booking.date} でした。\nスタッフにお声がけください。"
            )
        else:
            return QRScanResult(
                success=False,
                check_in_type=CheckInType.booking,
                message=f"予約日は {booking.date} です。\n当日にお越しください。",
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
                message=f"既にチェックイン済みです。\nお席へどうぞ。",
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
            message=f"{booking.guest_name}様\nいらっしゃいませ！\n\nお席へご案内いたします。",
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
            message=f"{booking.guest_name}様\nいらっしゃいませ！\n\n只今満席のため、少々お待ちください。",
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

```

## File ./backend\app\domains\checkin\schemas.py:
```python
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

```

## File ./backend\app\domains\checkin\__init__.py:
```python
﻿"""
Check-in Domain - Customer Reception & Seating
Team: checkin
"""
from app.domains.checkin.router import router
from app.domains.checkin.models import WaitingList, CheckInLog

__all__ = ["router", "WaitingList", "CheckInLog"]


```

## File ./backend\app\domains\kitchen\router.py:
```python
﻿"""
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
from app.domains.tableorder.models import Order, OrderItem, OrderStatus
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
        return "new"      # ⚪ < 1 min
    elif seconds < 180:
        return "normal"   # 🟢 1-3 min
    elif seconds < 300:
        return "warning"  # 🟡 3-5 min
    else:
        return "urgent"   # 🔴 > 5 min

```

## File ./backend\app\domains\kitchen\__init__.py:
```python
﻿"""
Kitchen Domain - Kitchen Display System (KDS)
Team: kitchen
"""
from app.domains.kitchen.router import router

__all__ = ["router"]


```

## File ./backend\app\domains\pos\router.py:
```python
﻿"""
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
from app.domains.tableorder.models import Order, OrderItem, OrderStatus, TableSession
from app.domains.shared.models import Table
from app.domains.pos.schemas import (
    CheckoutRequest, CheckoutResponse, TableOverview,
    POSDashboard, TableStatusEnum, PaymentMethod
)

router = APIRouter()

TAX_RATE = Decimal("0.10")  # 10% tax


@router.get("/tables", response_model=POSDashboard)
async def get_pos_tables(
    branch_code: str = "hirama",
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

```

## File ./backend\app\domains\pos\schemas.py:
```python
"""
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

```

## File ./backend\app\domains\pos\__init__.py:
```python
﻿"""
POS Domain - Point of Sale / Checkout
Team: pos
"""
from app.domains.pos.router import router

__all__ = ["router"]


```

## File ./backend\app\domains\shared\models.py:
```python
﻿"""
Shared Models - Re-export from legacy models
"""
# Re-export from legacy models
from app.models.branch import Branch
from app.models.menu import MenuItem
from app.models.table import Table

__all__ = ["Branch", "MenuItem", "Table"]


```

## File ./backend\app\domains\shared\schemas.py:
```python
﻿"""
Shared Schemas - Base schemas for cross-domain use
"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class BranchBase(BaseModel):
    code: str
    name: str
    subdomain: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class MenuItemBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    image_url: Optional[str] = None
    is_available: bool = True
    is_popular: bool = False
    is_spicy: bool = False

    class Config:
        from_attributes = True


class TableBase(BaseModel):
    id: str
    table_number: str
    capacity: int
    zone: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


```

## File ./backend\app\domains\shared\__init__.py:
```python
﻿"""
Shared domain - common models and utilities used across all domains
"""
from app.domains.shared.models import Branch, MenuItem, Table
from app.domains.shared.schemas import BranchBase, MenuItemBase, TableBase

__all__ = [
    "Branch", "MenuItem", "Table",
    "BranchBase", "MenuItemBase", "TableBase"
]


```

## File ./backend\app\domains\tableorder\events.py:
```python
"""
Event Sourcing for Table Order Domain
Tracks all state changes for audit, debugging, and replay

Event Types:
- ORDER_* : Order lifecycle events
- ITEM_* : Order item events
- SESSION_* : Table session events
- CALL_* : Staff call events
- GATEWAY_* : Communication events (for tracking delivery issues)
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Index
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import json

from app.database import Base


# ============ Event Types ============

class EventType(str, Enum):
    # Order lifecycle
    ORDER_CREATED = "order.created"
    ORDER_CONFIRMED = "order.confirmed"
    ORDER_PREPARING = "order.preparing"
    ORDER_READY = "order.ready"
    ORDER_SERVED = "order.served"
    ORDER_CANCELLED = "order.cancelled"

    # Order item events
    ITEM_ADDED = "item.added"
    ITEM_REMOVED = "item.removed"
    ITEM_STATUS_CHANGED = "item.status_changed"

    # Session events
    SESSION_STARTED = "session.started"
    SESSION_ENDED = "session.ended"
    SESSION_PAID = "session.paid"
    SESSION_LOG = "session.log"

    # Staff call events
    CALL_STAFF = "call.staff"
    CALL_WATER = "call.water"
    CALL_BILL = "call.bill"
    CALL_ACKNOWLEDGED = "call.acknowledged"

    # Gateway/Communication events (tracking delivery)
    GATEWAY_SENT = "gateway.sent"           # Event sent to kitchen/POS
    GATEWAY_RECEIVED = "gateway.received"   # Ack from kitchen/POS
    GATEWAY_FAILED = "gateway.failed"       # Delivery failed
    GATEWAY_RETRY = "gateway.retry"         # Retry attempt

    # WebSocket events
    WS_CONNECTED = "ws.connected"
    WS_DISCONNECTED = "ws.disconnected"
    WS_MESSAGE_SENT = "ws.message_sent"
    WS_MESSAGE_FAILED = "ws.message_failed"

    # Error events
    ERROR_VALIDATION = "error.validation"
    ERROR_DATABASE = "error.database"
    ERROR_NETWORK = "error.network"
    ERROR_UNKNOWN = "error.unknown"


class EventSource(str, Enum):
    """Where the event originated from"""
    TABLE_ORDER = "table-order"     # Customer iPad
    KITCHEN = "kitchen"             # Kitchen display
    POS = "pos"                     # POS system
    DASHBOARD = "dashboard"         # Admin dashboard
    SYSTEM = "system"               # Backend automation
    API = "api"                     # Direct API call


# ============ SQLAlchemy Model ============

class OrderEvent(Base):
    """
    Event log for order-related actions.
    Immutable append-only log for event sourcing.
    """
    __tablename__ = "order_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Event metadata
    event_type = Column(String(50), nullable=False, index=True)
    event_source = Column(String(30), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Context
    branch_code = Column(String(50), nullable=False, index=True)
    table_id = Column(String(36), index=True)
    session_id = Column(String(36), index=True)
    order_id = Column(String(36), index=True)
    order_item_id = Column(String(36), index=True)

    # Actor (who triggered the event)
    actor_type = Column(String(20))  # customer, staff, system
    actor_id = Column(String(36))    # customer_id or staff_id

    # Event data (JSON payload)
    data = Column(JSON, default=dict)

    # For tracking gateway issues
    correlation_id = Column(String(36), index=True)  # Links related events
    sequence_number = Column(Integer)  # Order within correlation

    # Error tracking
    error_code = Column(String(50))
    error_message = Column(Text)

    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_order_events_session_time', 'session_id', 'timestamp'),
        Index('ix_order_events_order_time', 'order_id', 'timestamp'),
        Index('ix_order_events_correlation', 'correlation_id', 'sequence_number'),
        Index('ix_order_events_type_time', 'event_type', 'timestamp'),
    )

    def __repr__(self):
        return f"<OrderEvent {self.event_type} @ {self.timestamp}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_source": self.event_source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "branch_code": self.branch_code,
            "table_id": self.table_id,
            "session_id": self.session_id,
            "order_id": self.order_id,
            "data": self.data,
            "correlation_id": self.correlation_id,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }


# ============ Pydantic Schemas ============

class EventCreate(BaseModel):
    """Schema for creating a new event"""
    event_type: EventType
    event_source: EventSource = EventSource.TABLE_ORDER
    branch_code: str
    table_id: Optional[str] = None
    session_id: Optional[str] = None
    order_id: Optional[str] = None
    order_item_id: Optional[str] = None
    actor_type: Optional[str] = None
    actor_id: Optional[str] = None
    data: dict = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    sequence_number: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class EventResponse(BaseModel):
    """Schema for event response"""
    id: str
    event_type: str
    event_source: str
    timestamp: datetime
    branch_code: str
    table_id: Optional[str] = None
    session_id: Optional[str] = None
    order_id: Optional[str] = None
    data: dict
    correlation_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Schema for paginated event list"""
    events: list[EventResponse]
    total: int
    page: int
    page_size: int


class EventQuery(BaseModel):
    """Query parameters for filtering events"""
    branch_code: Optional[str] = None
    table_id: Optional[str] = None
    session_id: Optional[str] = None
    order_id: Optional[str] = None
    event_type: Optional[str] = None
    event_source: Optional[str] = None
    correlation_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    has_error: Optional[bool] = None
    page: int = 1
    page_size: int = 50

```

## File ./backend\app\domains\tableorder\event_router.py:
```python
"""
Event Router - API endpoints for event sourcing
Provides endpoints for querying events, diagnostics, and debugging
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.domains.tableorder.events import EventQuery, EventListResponse, EventResponse
from app.domains.tableorder.event_service import EventService

router = APIRouter()


@router.get("/", response_model=EventListResponse)
async def list_events(
    branch_code: str = Query(..., description="Branch code"),
    table_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    order_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    event_source: Optional[str] = Query(None),
    correlation_id: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    has_error: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Query events with filters.
    Use this to review operations and track issues.
    """
    query = EventQuery(
        branch_code=branch_code,
        table_id=table_id,
        session_id=session_id,
        order_id=order_id,
        event_type=event_type,
        event_source=event_source,
        correlation_id=correlation_id,
        start_time=start_time,
        end_time=end_time,
        has_error=has_error,
        page=page,
        page_size=page_size
    )

    service = EventService(db)
    return await service.get_events(query)


@router.get("/order/{order_id}/timeline", response_model=list[EventResponse])
async def get_order_timeline(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete event timeline for an order.
    Useful for debugging order processing issues.
    """
    service = EventService(db)
    events = await service.get_order_timeline(order_id)

    if not events:
        raise HTTPException(status_code=404, detail="No events found for this order")

    return events


@router.get("/session/{session_id}/timeline", response_model=list[EventResponse])
async def get_session_timeline(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete event timeline for a table session.
    Shows all activity from session start to end.
    """
    service = EventService(db)
    events = await service.get_session_timeline(session_id)

    if not events:
        raise HTTPException(status_code=404, detail="No events found for this session")

    return events


@router.get("/correlation/{correlation_id}", response_model=list[EventResponse])
async def get_correlation_chain(
    correlation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all events in a correlation chain.
    Use this to trace a specific order's journey through the system.

    Example: Order created → Sent to kitchen → Kitchen acknowledged
    """
    service = EventService(db)
    events = await service.get_correlation_chain(correlation_id)

    if not events:
        raise HTTPException(status_code=404, detail="No events found for this correlation")

    return events


# ============ Diagnostics Endpoints ============

@router.get("/diagnostics/undelivered")
async def get_undelivered_orders(
    branch_code: str = Query(...),
    since_minutes: int = Query(5, ge=1, le=60),
    db: AsyncSession = Depends(get_db)
):
    """
    Find orders that were created but not acknowledged by kitchen.

    This is critical for detecting gateway issues where:
    - Customer placed order on iPad
    - Kitchen never received it

    Returns orders that have been waiting for acknowledgment.
    """
    service = EventService(db)
    undelivered = await service.get_undelivered_orders(branch_code, since_minutes)

    return {
        "branch_code": branch_code,
        "since_minutes": since_minutes,
        "count": len(undelivered),
        "orders": undelivered,
        "alert": len(undelivered) > 0,
        "message": f"{len(undelivered)} order(s) not acknowledged in last {since_minutes} minutes" if undelivered else "All orders delivered"
    }


@router.get("/diagnostics/failed-deliveries")
async def get_failed_deliveries(
    branch_code: str = Query(...),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all failed gateway deliveries.

    Shows:
    - WebSocket send failures
    - Kitchen connection issues
    - POS communication errors
    """
    service = EventService(db)
    failures = await service.get_failed_deliveries(branch_code, hours)

    return {
        "branch_code": branch_code,
        "hours": hours,
        "count": len(failures),
        "failures": failures
    }


@router.get("/diagnostics/errors")
async def get_error_summary(
    branch_code: str = Query(...),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary of all errors in the system.

    Useful for:
    - Identifying recurring issues
    - Monitoring system health
    - Debugging patterns
    """
    service = EventService(db)
    summary = await service.get_error_summary(branch_code, hours)

    return {
        "branch_code": branch_code,
        "hours": hours,
        **summary
    }


# ============ Health Check ============

@router.get("/health")
async def event_system_health(
    branch_code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick health check for the event sourcing system.

    Returns:
    - Recent event count
    - Undelivered orders
    - Error rate
    """
    service = EventService(db)

    # Get recent events (last hour)
    from datetime import timedelta
    from app.domains.tableorder.events import EventQuery

    recent = await service.get_events(EventQuery(
        branch_code=branch_code,
        start_time=datetime.utcnow() - timedelta(hours=1),
        page_size=1  # Just need count
    ))

    # Get undelivered
    undelivered = await service.get_undelivered_orders(branch_code, 5)

    # Get error count
    errors = await service.get_error_summary(branch_code, 1)

    status = "healthy"
    if len(undelivered) > 0:
        status = "warning"
    if errors["total_errors"] > 10:
        status = "degraded"

    return {
        "status": status,
        "branch_code": branch_code,
        "metrics": {
            "events_last_hour": recent.total,
            "undelivered_orders": len(undelivered),
            "errors_last_hour": errors["total_errors"]
        },
        "alerts": {
            "has_undelivered": len(undelivered) > 0,
            "high_error_rate": errors["total_errors"] > 10
        }
    }

```

## File ./backend\app\domains\tableorder\event_service.py:
```python
"""
Event Service - Event Sourcing Operations
Handles event logging, querying, and replay
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.domains.tableorder.events import (
    OrderEvent, EventType, EventSource,
    EventCreate, EventResponse, EventListResponse, EventQuery
)


class EventService:
    """Service for event sourcing operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============ Event Creation ============

    async def log_event(
        self,
        event_type: EventType,
        branch_code: str,
        event_source: EventSource = EventSource.TABLE_ORDER,
        table_id: Optional[str] = None,
        session_id: Optional[str] = None,
        order_id: Optional[str] = None,
        order_item_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        data: dict = None,
        correlation_id: Optional[str] = None,
        sequence_number: Optional[int] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> OrderEvent:
        """Log a new event to the event store"""
        event = OrderEvent(
            event_type=event_type.value,
            event_source=event_source.value,
            branch_code=branch_code,
            table_id=table_id,
            session_id=session_id,
            order_id=order_id,
            order_item_id=order_item_id,
            actor_type=actor_type,
            actor_id=actor_id,
            data=data or {},
            correlation_id=correlation_id or str(uuid.uuid4()),
            sequence_number=sequence_number or 1,
            error_code=error_code,
            error_message=error_message,
        )

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        return event

    async def log_order_created(
        self,
        order_id: str,
        branch_code: str,
        table_id: str,
        session_id: str,
        items: List[dict],
        source: EventSource = EventSource.TABLE_ORDER
    ) -> str:
        """Log order created event with correlation ID"""
        correlation_id = str(uuid.uuid4())

        await self.log_event(
            event_type=EventType.ORDER_CREATED,
            event_source=source,
            branch_code=branch_code,
            table_id=table_id,
            session_id=session_id,
            order_id=order_id,
            data={
                "items": items,
                "item_count": len(items),
                "total_quantity": sum(i.get("quantity", 1) for i in items)
            },
            correlation_id=correlation_id,
            sequence_number=1
        )

        return correlation_id

    async def log_gateway_sent(
        self,
        order_id: str,
        branch_code: str,
        destination: str,  # "kitchen", "pos", etc.
        correlation_id: str,
        message_data: dict
    ) -> OrderEvent:
        """Log when order is sent to kitchen/POS via WebSocket"""
        # Get next sequence number for this correlation
        seq = await self._get_next_sequence(correlation_id)

        return await self.log_event(
            event_type=EventType.GATEWAY_SENT,
            event_source=EventSource.SYSTEM,
            branch_code=branch_code,
            order_id=order_id,
            data={
                "destination": destination,
                "message": message_data
            },
            correlation_id=correlation_id,
            sequence_number=seq
        )

    async def log_gateway_received(
        self,
        order_id: str,
        branch_code: str,
        source: str,  # "kitchen", "pos"
        correlation_id: str
    ) -> OrderEvent:
        """Log acknowledgment from kitchen/POS"""
        seq = await self._get_next_sequence(correlation_id)

        return await self.log_event(
            event_type=EventType.GATEWAY_RECEIVED,
            event_source=EventSource.SYSTEM,
            branch_code=branch_code,
            order_id=order_id,
            data={"source": source, "acknowledged_at": datetime.utcnow().isoformat()},
            correlation_id=correlation_id,
            sequence_number=seq
        )

    async def log_gateway_failed(
        self,
        order_id: str,
        branch_code: str,
        destination: str,
        correlation_id: str,
        error_code: str,
        error_message: str
    ) -> OrderEvent:
        """Log failed delivery attempt"""
        seq = await self._get_next_sequence(correlation_id)

        return await self.log_event(
            event_type=EventType.GATEWAY_FAILED,
            event_source=EventSource.SYSTEM,
            branch_code=branch_code,
            order_id=order_id,
            data={"destination": destination},
            correlation_id=correlation_id,
            sequence_number=seq,
            error_code=error_code,
            error_message=error_message
        )

    async def log_error(
        self,
        event_type: EventType,
        branch_code: str,
        error_code: str,
        error_message: str,
        context: dict = None,
        order_id: Optional[str] = None,
        session_id: Optional[str] = None,
        table_id: Optional[str] = None
    ) -> OrderEvent:
        """Log an error event"""
        return await self.log_event(
            event_type=event_type,
            event_source=EventSource.SYSTEM,
            branch_code=branch_code,
            order_id=order_id,
            session_id=session_id,
            table_id=table_id,
            data=context or {},
            error_code=error_code,
            error_message=error_message
        )

    # ============ Event Querying ============

    async def get_events(self, query: EventQuery) -> EventListResponse:
        """Query events with filters and pagination"""
        stmt = select(OrderEvent)

        # Apply filters
        conditions = []
        if query.branch_code:
            conditions.append(OrderEvent.branch_code == query.branch_code)
        if query.table_id:
            conditions.append(OrderEvent.table_id == query.table_id)
        if query.session_id:
            conditions.append(OrderEvent.session_id == query.session_id)
        if query.order_id:
            conditions.append(OrderEvent.order_id == query.order_id)
        if query.event_type:
            conditions.append(OrderEvent.event_type == query.event_type)
        if query.event_source:
            conditions.append(OrderEvent.event_source == query.event_source)
        if query.correlation_id:
            conditions.append(OrderEvent.correlation_id == query.correlation_id)
        if query.start_time:
            conditions.append(OrderEvent.timestamp >= query.start_time)
        if query.end_time:
            conditions.append(OrderEvent.timestamp <= query.end_time)
        if query.has_error is True:
            conditions.append(OrderEvent.error_code.isnot(None))
        elif query.has_error is False:
            conditions.append(OrderEvent.error_code.is_(None))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        # Apply pagination and ordering
        stmt = stmt.order_by(OrderEvent.timestamp.desc())
        stmt = stmt.offset((query.page - 1) * query.page_size).limit(query.page_size)

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return EventListResponse(
            events=[EventResponse.model_validate(e) for e in events],
            total=total,
            page=query.page,
            page_size=query.page_size
        )

    async def get_order_timeline(self, order_id: str) -> List[EventResponse]:
        """Get complete timeline of events for an order"""
        stmt = (
            select(OrderEvent)
            .where(OrderEvent.order_id == order_id)
            .order_by(OrderEvent.timestamp.asc())
        )

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return [EventResponse.model_validate(e) for e in events]

    async def get_session_timeline(self, session_id: str) -> List[EventResponse]:
        """Get complete timeline of events for a session"""
        stmt = (
            select(OrderEvent)
            .where(OrderEvent.session_id == session_id)
            .order_by(OrderEvent.timestamp.asc())
        )

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return [EventResponse.model_validate(e) for e in events]

    async def get_correlation_chain(self, correlation_id: str) -> List[EventResponse]:
        """Get all events in a correlation chain (for tracking delivery)"""
        stmt = (
            select(OrderEvent)
            .where(OrderEvent.correlation_id == correlation_id)
            .order_by(OrderEvent.sequence_number.asc())
        )

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return [EventResponse.model_validate(e) for e in events]

    # ============ Analytics & Diagnostics ============

    async def get_undelivered_orders(
        self,
        branch_code: str,
        since_minutes: int = 5
    ) -> List[dict]:
        """
        Find orders that were created but not acknowledged by kitchen.
        Use this to detect gateway issues.
        """
        since = datetime.utcnow() - timedelta(minutes=since_minutes)

        # Get all ORDER_CREATED events
        created_stmt = (
            select(OrderEvent)
            .where(
                and_(
                    OrderEvent.branch_code == branch_code,
                    OrderEvent.event_type == EventType.ORDER_CREATED.value,
                    OrderEvent.timestamp >= since
                )
            )
        )
        result = await self.db.execute(created_stmt)
        created_events = result.scalars().all()

        undelivered = []
        for event in created_events:
            # Check if there's a corresponding GATEWAY_RECEIVED
            ack_stmt = (
                select(func.count())
                .select_from(OrderEvent)
                .where(
                    and_(
                        OrderEvent.correlation_id == event.correlation_id,
                        OrderEvent.event_type == EventType.GATEWAY_RECEIVED.value
                    )
                )
            )
            ack_count = (await self.db.execute(ack_stmt)).scalar() or 0

            if ack_count == 0:
                undelivered.append({
                    "order_id": event.order_id,
                    "correlation_id": event.correlation_id,
                    "created_at": event.timestamp.isoformat(),
                    "table_id": event.table_id,
                    "session_id": event.session_id,
                    "data": event.data,
                    "minutes_ago": (datetime.utcnow() - event.timestamp.replace(tzinfo=None)).seconds // 60
                })

        return undelivered

    async def get_failed_deliveries(
        self,
        branch_code: str,
        hours: int = 24
    ) -> List[EventResponse]:
        """Get all failed gateway deliveries in the last N hours"""
        since = datetime.utcnow() - timedelta(hours=hours)

        stmt = (
            select(OrderEvent)
            .where(
                and_(
                    OrderEvent.branch_code == branch_code,
                    OrderEvent.event_type == EventType.GATEWAY_FAILED.value,
                    OrderEvent.timestamp >= since
                )
            )
            .order_by(OrderEvent.timestamp.desc())
        )

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return [EventResponse.model_validate(e) for e in events]

    async def get_error_summary(
        self,
        branch_code: str,
        hours: int = 24
    ) -> dict:
        """Get summary of errors in the last N hours"""
        since = datetime.utcnow() - timedelta(hours=hours)

        # Count by error type
        stmt = (
            select(
                OrderEvent.event_type,
                OrderEvent.error_code,
                func.count().label("count")
            )
            .where(
                and_(
                    OrderEvent.branch_code == branch_code,
                    OrderEvent.error_code.isnot(None),
                    OrderEvent.timestamp >= since
                )
            )
            .group_by(OrderEvent.event_type, OrderEvent.error_code)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        summary = {
            "total_errors": sum(r.count for r in rows),
            "by_type": {},
            "by_code": {}
        }

        for row in rows:
            # By event type
            if row.event_type not in summary["by_type"]:
                summary["by_type"][row.event_type] = 0
            summary["by_type"][row.event_type] += row.count

            # By error code
            if row.error_code not in summary["by_code"]:
                summary["by_code"][row.error_code] = 0
            summary["by_code"][row.error_code] += row.count

        return summary

    # ============ Helpers ============

    async def _get_next_sequence(self, correlation_id: str) -> int:
        """Get next sequence number for a correlation chain"""
        stmt = (
            select(func.max(OrderEvent.sequence_number))
            .where(OrderEvent.correlation_id == correlation_id)
        )
        result = await self.db.execute(stmt)
        max_seq = result.scalar() or 0
        return max_seq + 1


# ============ Convenience Functions ============

async def log_event(
    db: AsyncSession,
    event_type: EventType,
    branch_code: str,
    **kwargs
) -> OrderEvent:
    """Convenience function to log an event"""
    service = EventService(db)
    return await service.log_event(event_type, branch_code, **kwargs)

```

## File ./backend\app\domains\tableorder\models.py:
```python
﻿"""
Order Models - Re-export from legacy models
"""
# Re-export from legacy models
from app.models.order import Order, OrderItem, OrderStatus, TableSession

__all__ = ["Order", "OrderItem", "OrderStatus", "TableSession"]


```

## File ./backend\app\domains\tableorder\router.py:
```python
﻿"""
Order Router - Table Order APIs
Team: table-order
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.domains.tableorder.models import Order, OrderItem, OrderStatus, TableSession
from app.domains.tableorder.schemas import (
    OrderCreate, OrderResponse, OrderListResponse,
    TableSessionCreate, TableSessionResponse
)
from app.domains.shared.models import MenuItem
from app.domains.tableorder.events import EventType, EventSource
from app.domains.tableorder.event_service import EventService

router = APIRouter()


# ============ Session Log Schema ============

class SessionLogEntry(BaseModel):
    type: str
    ts: float
    meta: Optional[dict] = None


class SessionLogRequest(BaseModel):
    session_id: str
    table_id: str
    entries: list[SessionLogEntry]


# ============ Session Log Endpoint ============

@router.post("/session-log")
async def receive_session_log(
    log_data: SessionLogRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive analytics/session log from table-order frontend.
    Fire-and-forget: accepts the data and logs it.
    In production, this would be stored for analytics.
    """
    event_service = EventService(db)

    # Log as a single SESSION_LOG event with all entries
    await event_service.log_event(
        event_type=EventType.SESSION_LOG if hasattr(EventType, 'SESSION_LOG') else EventType.SESSION_STARTED,
        event_source=EventSource.TABLE_ORDER,
        branch_code="hirama",
        table_id=log_data.table_id,
        session_id=log_data.session_id,
        data={
            "entries": [e.model_dump() for e in log_data.entries],
            "entry_count": len(log_data.entries)
        }
    )

    return {"status": "ok", "received": len(log_data.entries)}


# ============ Call Staff Schema ============

class CallStaffRequest(BaseModel):
    table_id: str
    session_id: str
    call_type: str  # "assistance", "water", "bill"


class CallStaffResponse(BaseModel):
    success: bool
    message: str
    call_type: str
    correlation_id: str


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new order from table"""
    event_service = EventService(db)

    # Get next order number for this session
    result = await db.execute(
        select(func.max(Order.order_number))
        .where(Order.session_id == order_data.session_id)
    )
    max_num = result.scalar() or 0

    # Create order
    order = Order(
        branch_code=order_data.branch_code,
        table_id=order_data.table_id,
        session_id=order_data.session_id,
        order_number=max_num + 1,
        status=OrderStatus.PENDING.value
    )

    # Add items
    items_data = []
    for item_data in order_data.items:
        # Get menu item details from database
        result = await db.execute(
            select(MenuItem).where(MenuItem.id == item_data.menu_item_id)
        )
        menu_item = result.scalar_one_or_none()

        # Use DB data if exists, otherwise use demo data from request
        if menu_item:
            item_name = menu_item.name
            item_price = menu_item.price
        elif item_data.item_name and item_data.item_price:
            # Demo mode: use data from request
            item_name = item_data.item_name
            item_price = item_data.item_price
        else:
            # No menu item and no demo data - use placeholder
            item_name = f"Item {item_data.menu_item_id}"
            item_price = 0

        order_item = OrderItem(
            menu_item_id=item_data.menu_item_id,
            item_name=item_name,
            item_price=item_price,
            quantity=item_data.quantity,
            notes=item_data.notes
        )
        order.items.append(order_item)

        items_data.append({
            "menu_item_id": item_data.menu_item_id,
            "name": item_name,
            "price": float(item_price),
            "quantity": item_data.quantity,
            "notes": item_data.notes
        })

    db.add(order)
    await db.commit()
    await db.refresh(order)

    # Reload with items
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order.id)
    )
    order = result.scalar_one()

    # Log ORDER_CREATED event
    correlation_id = await event_service.log_order_created(
        order_id=order.id,
        branch_code=order_data.branch_code,
        table_id=order_data.table_id,
        session_id=order_data.session_id,
        items=items_data,
        source=EventSource.TABLE_ORDER
    )

    # TODO: Send to kitchen via WebSocket and log GATEWAY_SENT
    # await event_service.log_gateway_sent(...)

    return OrderResponse.model_validate(order)


@router.get("/table/{table_id}", response_model=OrderListResponse)
async def get_table_orders(
    table_id: str,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a table (optionally filtered by session)"""
    query = select(Order).options(selectinload(Order.items)).where(Order.table_id == table_id)

    if session_id:
        query = query.where(Order.session_id == session_id)

    query = query.order_by(Order.created_at.desc())

    result = await db.execute(query)
    orders = result.scalars().all()

    return OrderListResponse(
        orders=[OrderResponse.model_validate(o) for o in orders],
        total=len(orders)
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get order by ID"""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse.model_validate(order)


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    """Update order status"""
    event_service = EventService(db)

    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = status

    # Update timestamps based on status
    now = datetime.utcnow()
    if status == OrderStatus.CONFIRMED.value:
        order.confirmed_at = now
    elif status == OrderStatus.READY.value:
        order.ready_at = now
    elif status == OrderStatus.SERVED.value:
        order.served_at = now

    await db.commit()

    # Log status change event
    status_event_map = {
        OrderStatus.CONFIRMED.value: EventType.ORDER_CONFIRMED,
        OrderStatus.PREPARING.value: EventType.ORDER_PREPARING,
        OrderStatus.READY.value: EventType.ORDER_READY,
        OrderStatus.SERVED.value: EventType.ORDER_SERVED,
        OrderStatus.CANCELLED.value: EventType.ORDER_CANCELLED,
    }

    if status in status_event_map:
        await event_service.log_event(
            event_type=status_event_map[status],
            branch_code=order.branch_code,
            event_source=EventSource.API,
            table_id=order.table_id,
            session_id=order.session_id,
            order_id=order.id,
            data={"old_status": old_status, "new_status": status}
        )

    return {"message": "Status updated", "status": status}


# ============ Call Staff Endpoint ============

@router.post("/call-staff", response_model=CallStaffResponse)
async def call_staff(
    request: CallStaffRequest,
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """
    Call staff from table.
    Logs event for tracking and sends notification via WebSocket.
    """
    event_service = EventService(db)

    # Map call type to event type
    call_event_map = {
        "assistance": EventType.CALL_STAFF,
        "water": EventType.CALL_WATER,
        "bill": EventType.CALL_BILL,
    }

    event_type = call_event_map.get(request.call_type, EventType.CALL_STAFF)

    # Log the call event
    event = await event_service.log_event(
        event_type=event_type,
        event_source=EventSource.TABLE_ORDER,
        branch_code=branch_code,
        table_id=request.table_id,
        session_id=request.session_id,
        data={"call_type": request.call_type}
    )

    # TODO: Send notification to staff via WebSocket
    # notification_manager.broadcast(...)

    call_labels = {
        "assistance": "スタッフを呼び出しました",
        "water": "お水をお持ちします",
        "bill": "お会計をお待ちください"
    }

    return CallStaffResponse(
        success=True,
        message=call_labels.get(request.call_type, "スタッフを呼び出しました"),
        call_type=request.call_type,
        correlation_id=event.correlation_id
    )


# Session endpoints
@router.post("/sessions", response_model=TableSessionResponse)
async def create_session(
    session_data: TableSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Start a new table session"""
    event_service = EventService(db)

    session = TableSession(
        branch_code=session_data.branch_code,
        table_id=session_data.table_id,
        booking_id=session_data.booking_id,
        guest_count=session_data.guest_count
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Log session started event
    await event_service.log_event(
        event_type=EventType.SESSION_STARTED,
        event_source=EventSource.TABLE_ORDER,
        branch_code=session_data.branch_code,
        table_id=session_data.table_id,
        session_id=session.id,
        data={
            "guest_count": session_data.guest_count,
            "booking_id": session_data.booking_id
        }
    )

    return TableSessionResponse.model_validate(session)


@router.get("/sessions/{session_id}", response_model=TableSessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session by ID"""
    result = await db.execute(
        select(TableSession).where(TableSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return TableSessionResponse.model_validate(session)

```

## File ./backend\app\domains\tableorder\schemas.py:
```python
﻿"""
Order Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class OrderStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    ready = "ready"
    served = "served"
    cancelled = "cancelled"


class OrderItemCreate(BaseModel):
    menu_item_id: str
    quantity: int = Field(default=1, ge=1)
    notes: Optional[str] = None
    # Optional fields for demo mode (when menu_item doesn't exist in DB)
    item_name: Optional[str] = None
    item_price: Optional[int] = None


class OrderCreate(BaseModel):
    branch_code: str = "hirama"
    table_id: str
    session_id: str
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: str
    menu_item_id: str
    item_name: str
    item_price: Decimal
    quantity: int
    notes: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: str
    branch_code: str
    table_id: str
    session_id: str
    order_number: int
    status: str
    items: list[OrderItemResponse]
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    served_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int


class TableSessionCreate(BaseModel):
    branch_code: str = "hirama"
    table_id: str
    booking_id: Optional[str] = None
    guest_count: int = 1


class TableSessionResponse(BaseModel):
    id: str
    branch_code: str
    table_id: str
    booking_id: Optional[str] = None
    guest_count: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_paid: bool
    total_amount: Decimal

    class Config:
        from_attributes = True

```

## File ./backend\app\domains\tableorder\__init__.py:
```python
﻿"""
Table Order Domain - Table Ordering System
Team: table-order
"""
from app.domains.tableorder.models import Order, OrderItem, OrderStatus, TableSession
from app.domains.tableorder.schemas import (
    OrderCreate, OrderResponse, OrderItemCreate
)
from app.domains.tableorder.router import router
from app.domains.tableorder.events import OrderEvent, EventType, EventSource
from app.domains.tableorder.event_service import EventService

__all__ = [
    # Models
    "Order", "OrderItem", "OrderStatus", "TableSession",
    # Schemas
    "OrderCreate", "OrderResponse", "OrderItemCreate",
    # Router
    "router",
    # Event Sourcing
    "OrderEvent", "EventType", "EventSource", "EventService"
]

```

## File ./backend\app\models\booking.py:
```python
﻿"""
Booking Model
"""
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum


from app.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Booking(Base):
    """Restaurant booking"""
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)
    branch_customer_id = Column(String(36), ForeignKey("branch_customers.id"))

    # Booking details
    date = Column(Date, nullable=False, index=True)
    time = Column(String(5), nullable=False)  # "18:00"
    guests = Column(Integer, nullable=False)

    # Guest info (for non-registered)
    guest_name = Column(String(255))
    guest_phone = Column(String(20))
    guest_email = Column(String(255))

    # Status & notes
    status = Column(String(20), default=BookingStatus.PENDING.value)
    note = Column(String(1000))  # Customer request
    staff_note = Column(String(1000))  # Internal note
    checked_in_at = Column(DateTime(timezone=True))  # Check-in timestamp

    # Metadata
    source = Column(String(50), default="web")  # 'web', 'chat', 'phone'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    branch_customer = relationship("BranchCustomer")


```

## File ./backend\app\models\branch.py:
```python
﻿"""
Branch Model - Multi-tenant support
"""
from sqlalchemy import Column, String, Integer, Time, Boolean, JSON, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Branch(Base):
    """Restaurant branch configuration"""
    __tablename__ = "branches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)  # 'hirama', 'shibuya'
    name = Column(String(255), nullable=False)  # 'Yakiniku 平間本店'
    subdomain = Column(String(100))  # 'hirama', 'shibuya'

    # Contact
    phone = Column(String(20))
    address = Column(String(500))

    # Branding
    theme_primary_color = Column(String(7), default="#d4af37")
    theme_bg_color = Column(String(7), default="#1a1a1a")
    logo_url = Column(String(500))

    # Operations
    opening_time = Column(Time)  # 17:00
    closing_time = Column(Time)  # 23:00
    last_order_time = Column(Time)  # 22:30
    closed_days = Column(JSON, default=[2])  # [2] = Tuesday (0=Sun, 1=Mon, ...)
    max_capacity = Column(Integer, default=30)

    # Features
    features = Column(JSON, default={
        "chat": True,
        "ai_booking": True,
        "customer_insights": True,
    })

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

```

## File ./backend\app\models\category.py:
```python
"""
Item Category Model - Menu categories hierarchy
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ItemCategory(Base):
    """
    Menu category hierarchy
    Examples: 肉類 > 牛肉 > 和牛
              飲み物 > ビール
    """
    __tablename__ = "item_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Identity
    code = Column(String(50), nullable=False)           # 'meat', 'beef', 'drinks'
    name = Column(String(100), nullable=False)          # '肉類', '牛肉', '飲み物'
    name_en = Column(String(100))                       # 'Meat', 'Beef', 'Drinks'
    description = Column(Text)

    # Hierarchy
    parent_id = Column(String(36), ForeignKey('item_categories.id'), nullable=True)

    # Display
    display_order = Column(Integer, default=0)
    icon = Column(String(50))                           # emoji: '🥩', '🍺'
    image_url = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent = relationship("ItemCategory", remote_side=[id], backref="subcategories")
    items = relationship("Item", back_populates="category")

    def __repr__(self):
        return f"<ItemCategory {self.code}: {self.name}>"

```

## File ./backend\app\models\chat.py:
```python
﻿"""
Chat Models - Message History and Extracted Insights
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ChatMessage(Base):
    """Chat message history"""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)
    branch_customer_id = Column(String(36), ForeignKey("branch_customers.id"))
    session_id = Column(String(100), nullable=False, index=True)

    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(String(5000), nullable=False)

    insights_extracted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatInsight(Base):
    """Insights extracted from chat by LLM"""
    __tablename__ = "chat_insights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_customer_id = Column(String(36), ForeignKey("branch_customers.id"))
    message_id = Column(String(36), ForeignKey("chat_messages.id"))

    insight_type = Column(String(50))  # 'preference', 'occasion', 'feedback', 'allergy'
    insight_value = Column(String(500))
    confidence = Column(String(10))  # 'high', 'medium', 'low'

    created_at = Column(DateTime(timezone=True), server_default=func.now())


```

## File ./backend\app\models\combo.py:
```python
"""
Combo Model - Set meals and combo discounts
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Combo(Base):
    """
    Combo deal - multiple items with discount
    Example: 和牛A5 + サラダセット (30% off)
    """
    __tablename__ = "combos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Identity
    code = Column(String(50), nullable=False)              # 'WAGYU-SALAD-30'
    name = Column(String(200), nullable=False)             # '和牛A5 + サラダセット'
    name_en = Column(String(200))                          # 'Wagyu A5 + Salad Set'
    description = Column(Text)

    # Discount
    discount_type = Column(String(20), nullable=False)     # 'percentage', 'fixed', 'new_price'
    discount_value = Column(Numeric(10, 2), nullable=False)  # 30 (%), ¥500, or ¥2800

    # Validity period
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    valid_hours_start = Column(Time, nullable=True)        # 17:00 (dinner only)
    valid_hours_end = Column(Time, nullable=True)          # 22:00
    valid_days = Column(String(50), nullable=True)         # 'mon,tue,wed,thu,fri' or null for all

    # Limits
    max_uses_total = Column(Integer, nullable=True)        # null = unlimited
    max_uses_per_order = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
    min_order_amount = Column(Numeric(10, 0), nullable=True)  # Minimum order to apply

    # Display
    display_order = Column(Integer, default=0)
    image_url = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)           # Show prominently

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    items = relationship("ComboItem", back_populates="combo", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Combo {self.name} {self.discount_value}{'%' if self.discount_type == 'percentage' else '¥'} off>"


class ComboItem(Base):
    """
    Items required to trigger a combo
    Example: Combo needs 1x Wagyu + 1x Any Salad
    """
    __tablename__ = "combo_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    combo_id = Column(String(36), ForeignKey('combos.id'), nullable=False)

    # Item matching
    item_id = Column(String(36), ForeignKey('items.id'), nullable=True)       # Specific item
    category_id = Column(String(36), ForeignKey('item_categories.id'), nullable=True)  # Any item in category

    # Quantity
    quantity = Column(Integer, default=1)                  # Need this many

    # Relationships
    combo = relationship("Combo", back_populates="items")
    item = relationship("Item")
    category = relationship("ItemCategory")

    def __repr__(self):
        return f"<ComboItem combo={self.combo_id} qty={self.quantity}>"

```

## File ./backend\app\models\customer.py:
```python
﻿"""
Customer Models - Global and Per-Branch
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class GlobalCustomer(Base):
    """
    Global customer identity (by phone)
    Shared across all branches
    """
    __tablename__ = "global_customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    branch_customers = relationship("BranchCustomer", back_populates="global_customer")


class BranchCustomer(Base):
    """
    Per-branch customer relationship
    Tracks visits and VIP status per branch
    """
    __tablename__ = "branch_customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    global_customer_id = Column(String(36), ForeignKey("global_customers.id"), nullable=False)
    branch_code = Column(String(50), nullable=False, index=True)

    visit_count = Column(Integer, default=0)
    last_visit = Column(DateTime(timezone=True))
    is_vip = Column(Boolean, default=False)
    notes = Column(String(1000))  # Staff notes

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    global_customer = relationship("GlobalCustomer", back_populates="branch_customers")
    preferences = relationship("CustomerPreference", back_populates="branch_customer")

    # Composite unique constraint
    __table_args__ = (
        # UniqueConstraint('global_customer_id', 'branch_code', name='uq_customer_branch'),
    )


# Alias for backward compatibility
Customer = BranchCustomer


```

## File ./backend\app\models\item.py:
```python
"""
Item Model - Enhanced menu items with options support
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Item(Base):
    """
    Menu item with options support
    Example: 和牛A5サーロイン ¥3,500 (has_options: true)
    """
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey('item_categories.id'), nullable=True)

    # Identity
    sku = Column(String(50), unique=True, nullable=True)  # 'MEAT-WAGYU-A5-001'
    name = Column(String(100), nullable=False)             # '和牛A5サーロイン'
    name_en = Column(String(100))                          # 'Wagyu A5 Sirloin'
    description = Column(Text)

    # Pricing
    base_price = Column(Numeric(10, 0), nullable=False)    # ¥3,500
    tax_rate = Column(Numeric(4, 2), default=10.0)         # 10%

    # Kitchen
    prep_time_minutes = Column(Integer, default=5)
    kitchen_printer = Column(String(50))                   # 'grill', 'drink', 'cold'
    kitchen_note = Column(Text)

    # Display
    display_order = Column(Integer, default=0)
    image_url = Column(String(500))

    # Flags
    is_available = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    is_spicy = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)
    allergens = Column(String(200))                        # 'egg,milk,wheat'

    # Option configuration
    has_options = Column(Boolean, default=False)
    options_required = Column(Boolean, default=False)      # Must select at least 1 option

    # Stock management (future)
    track_stock = Column(Boolean, default=False)
    stock_quantity = Column(Integer, nullable=True)
    low_stock_alert = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("ItemCategory", back_populates="items")
    option_assignments = relationship("ItemOptionAssignment", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Item {self.name} ¥{self.base_price}>"


class ItemOptionGroup(Base):
    """
    Option group - groups related options together
    Examples: 'ご飯の量', '焼き加減', 'トッピング'
    """
    __tablename__ = "item_option_groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Identity
    name = Column(String(100), nullable=False)             # 'ご飯の量'
    name_en = Column(String(100))                          # 'Rice Amount'
    description = Column(Text)

    # Selection rules
    selection_type = Column(String(20), nullable=False, default='single')  # 'single', 'multiple'
    min_selections = Column(Integer, default=0)            # 0 = optional
    max_selections = Column(Integer, default=1)            # for multiple selection

    # Display
    display_order = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    options = relationship("ItemOption", back_populates="group", cascade="all, delete-orphan")
    item_assignments = relationship("ItemOptionAssignment", back_populates="option_group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ItemOptionGroup {self.name}>"


class ItemOption(Base):
    """
    Individual option choice
    Examples: '少なめ +¥0', '大盛り +¥100', 'レア', 'ミディアム'
    """
    __tablename__ = "item_options"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36), ForeignKey('item_option_groups.id'), nullable=False)

    # Identity
    name = Column(String(100), nullable=False)             # '大盛り'
    name_en = Column(String(100))                          # 'Large'

    # Pricing
    price_adjustment = Column(Numeric(10, 0), default=0)   # +¥100 or -¥50

    # Display
    is_default = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)

    # Status
    is_available = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    group = relationship("ItemOptionGroup", back_populates="options")

    def __repr__(self):
        adj = f"+¥{self.price_adjustment}" if self.price_adjustment > 0 else f"¥{self.price_adjustment}"
        return f"<ItemOption {self.name} {adj}>"


class ItemOptionAssignment(Base):
    """
    Links items to their available option groups
    Example: ビビンバ → [ご飯の量, トッピング]
    """
    __tablename__ = "item_option_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String(36), ForeignKey('items.id'), nullable=False)
    option_group_id = Column(String(36), ForeignKey('item_option_groups.id'), nullable=False)

    # Display order within item's options
    display_order = Column(Integer, default=0)

    # Relationships
    item = relationship("Item", back_populates="option_assignments")
    option_group = relationship("ItemOptionGroup", back_populates="item_assignments")

    def __repr__(self):
        return f"<ItemOptionAssignment item={self.item_id} group={self.option_group_id}>"

```

## File ./backend\app\models\menu.py:
```python
"""
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

```

## File ./backend\app\models\order.py:
```python
﻿"""
Order Model - Table orders for in-restaurant dining
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"         # 注文受付中 - Just placed
    CONFIRMED = "confirmed"     # 確認済み - Confirmed by kitchen
    PREPARING = "preparing"     # 調理中 - Being prepared
    READY = "ready"             # 完成 - Ready to serve
    SERVED = "served"           # 提供済み - Delivered to table
    CANCELLED = "cancelled"     # キャンセル


class Order(Base):
    """Order placed from table"""
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Table info (no FK constraint for demo mode)
    table_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), nullable=False, index=True)  # Unique per table session

    # Order number for display (e.g., "001", "002")
    order_number = Column(Integer, nullable=False)

    # Status tracking
    status = Column(String(20), default=OrderStatus.PENDING.value, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    ready_at = Column(DateTime(timezone=True))
    served_at = Column(DateTime(timezone=True))

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order #{self.order_number} - {self.status}>"


class OrderItem(Base):
    """Individual item in an order"""
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)
    menu_item_id = Column(String(36), nullable=False)  # No FK for demo mode

    # Item details (snapshot at time of order)
    item_name = Column(String(100), nullable=False)
    item_price = Column(Numeric(10, 0), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)

    # Special requests
    notes = Column(String(200))  # "よく焼き", "タレ多め"

    # Status (for kitchen tracking individual items)
    status = Column(String(20), default=OrderStatus.PENDING.value)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prepared_at = Column(DateTime(timezone=True))

    # Relationships
    order = relationship("Order", back_populates="items")

    @property
    def subtotal(self):
        return self.item_price * self.quantity

    def __repr__(self):
        return f"<OrderItem {self.item_name} x{self.quantity}>"


class TableSession(Base):
    """Track active table sessions (from sit-down to checkout)"""
    __tablename__ = "table_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)
    table_id = Column(String(36), ForeignKey("tables.id"), nullable=False, index=True)

    # Optional link to booking
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=True)

    # Session info
    guest_count = Column(Integer, default=1)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))

    # Payment
    is_paid = Column(Boolean, default=False)
    total_amount = Column(Numeric(10, 0), default=0)

    # Staff notes
    notes = Column(Text)

    def __repr__(self):
        return f"<TableSession {self.id[:8]} - Table {self.table_id[:8]}>"

```

## File ./backend\app\models\preference.py:
```python
﻿"""
Customer Preference Model
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class CustomerPreference(Base):
    """
    Customer preference/insight
    Can be AI-extracted or manually added
    """
    __tablename__ = "customer_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_customer_id = Column(String(36), ForeignKey("branch_customers.id"), nullable=False)

    preference = Column(String(255), nullable=False)  # 'レバ刺し', '厚切り'
    category = Column(String(50))  # 'meat', 'cooking', 'allergy', 'occasion'
    note = Column(String(500))  # Additional context

    # Source tracking
    confidence = Column(Float, default=1.0)  # 0.0-1.0 (AI=low, manual=1.0)
    source = Column(String(50), default="manual")  # 'chat', 'booking', 'manual'

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    branch_customer = relationship("BranchCustomer", back_populates="preferences")

```

## File ./backend\app\models\promotion.py:
```python
"""
Promotion Model - Order threshold rewards and special offers
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Promotion(Base):
    """
    Promotion/reward based on order conditions
    Examples:
    - Order ≥ ¥30,000 → Free beef tongue
    - Buy 8 large beers → Get 1 free
    """
    __tablename__ = "promotions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Identity
    code = Column(String(50), nullable=False)              # 'ORDER-30K-FREE-TONGUE'
    name = Column(String(200), nullable=False)             # '30,000円以上で牛タン無料'
    name_en = Column(String(200))
    description = Column(Text)

    # Trigger conditions
    trigger_type = Column(String(30), nullable=False)      # 'order_amount', 'item_quantity', 'item_total'
    trigger_item_id = Column(String(36), ForeignKey('items.id'), nullable=True)  # For item-based triggers
    trigger_category_id = Column(String(36), ForeignKey('item_categories.id'), nullable=True)  # Category-based
    trigger_value = Column(Numeric(10, 0), nullable=False) # ¥30,000 or quantity 8

    # Reward
    reward_type = Column(String(30), nullable=False)       # 'free_item', 'discount_item', 'discount_order', 'points_bonus'
    reward_item_id = Column(String(36), ForeignKey('items.id'), nullable=True)  # Item to give free
    reward_value = Column(Numeric(10, 2), nullable=True)   # Discount % or amount
    reward_quantity = Column(Integer, default=1)           # Give 1 free item

    # Validity period
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    valid_hours_start = Column(Time, nullable=True)
    valid_hours_end = Column(Time, nullable=True)
    valid_days = Column(String(50), nullable=True)         # 'sat,sun' for weekend only

    # Limits
    max_uses_per_order = Column(Integer, default=1)
    max_uses_per_customer = Column(Integer, nullable=True)
    max_uses_total = Column(Integer, nullable=True)
    current_uses = Column(Integer, default=0)

    # Stacking rules
    stackable = Column(Boolean, default=False)             # Can combine with other promos?
    priority = Column(Integer, default=0)                  # Higher = apply first

    # Display
    display_order = Column(Integer, default=0)
    image_url = Column(String(500))
    show_on_menu = Column(Boolean, default=True)           # Show as banner/notice

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    trigger_item = relationship("Item", foreign_keys=[trigger_item_id])
    trigger_category = relationship("ItemCategory", foreign_keys=[trigger_category_id])
    reward_item = relationship("Item", foreign_keys=[reward_item_id])

    def __repr__(self):
        return f"<Promotion {self.name}>"


class PromotionUsage(Base):
    """
    Track promotion usage per order/customer
    """
    __tablename__ = "promotion_usages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    promotion_id = Column(String(36), ForeignKey('promotions.id'), nullable=False)
    order_id = Column(String(36), nullable=False)          # Link to order
    customer_id = Column(String(36), nullable=True)        # If customer identified

    # Applied discount
    discount_amount = Column(Numeric(10, 0), nullable=False)

    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    promotion = relationship("Promotion")

    def __repr__(self):
        return f"<PromotionUsage promo={self.promotion_id} order={self.order_id}>"

```

## File ./backend\app\models\staff.py:
```python
﻿"""
Staff Model - Restaurant employees
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from enum import Enum
import uuid

from app.database import Base


class StaffRole(str, Enum):
    """Staff role types"""
    ADMIN = "admin"           # Full access
    MANAGER = "manager"       # Branch management
    CASHIER = "cashier"       # POS access
    WAITER = "waiter"         # Table service
    KITCHEN = "kitchen"       # Kitchen display
    RECEPTIONIST = "receptionist"  # Booking management


class Staff(Base):
    """Restaurant staff member"""
    __tablename__ = "staff"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Identity
    employee_id = Column(String(20), unique=True, nullable=False)  # S001, S002...
    name = Column(String(255), nullable=False)
    name_kana = Column(String(255))  # フリガナ

    # Contact
    phone = Column(String(20))
    email = Column(String(255))

    # Role & Access
    role = Column(String(20), default=StaffRole.WAITER.value)
    pin_code = Column(String(6))  # For quick login on iPad

    # Status
    is_active = Column(Boolean, default=True)
    hire_date = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

```

## File ./backend\app\models\table.py:
```python
﻿"""
Table Model - Restaurant table management
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class TableStatus(str, enum.Enum):
    AVAILABLE = "available"      # Bàn trống
    OCCUPIED = "occupied"        # Đang có khách
    RESERVED = "reserved"        # Đã đặt trước
    CLEANING = "cleaning"        # Đang dọn dẹp
    MAINTENANCE = "maintenance"  # Bảo trì


class TableType(str, enum.Enum):
    REGULAR = "regular"     # Bàn thường
    PRIVATE = "private"     # Phòng riêng / bàn VIP
    COUNTER = "counter"     # Quầy bar
    TERRACE = "terrace"     # Ngoài trời


class Table(Base):
    """Restaurant table configuration"""
    __tablename__ = "tables"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Table identity
    table_number = Column(String(10), nullable=False)  # "A1", "B2", "VIP1"
    name = Column(String(100))  # "窓際席", "個室A"

    # Capacity
    min_capacity = Column(Integer, default=1)   # Tối thiểu 1 người
    max_capacity = Column(Integer, nullable=False)  # 4 hoặc 6 ghế

    # Location & Type
    table_type = Column(String(20), default=TableType.REGULAR.value)
    floor = Column(Integer, default=1)  # Tầng
    zone = Column(String(50))  # "A", "B", "VIP", "Window"

    # Features
    has_window = Column(Boolean, default=False)      # Gần cửa sổ
    is_smoking = Column(Boolean, default=False)      # Khu hút thuốc
    is_wheelchair_accessible = Column(Boolean, default=True)
    has_baby_chair = Column(Boolean, default=False)  # Có ghế trẻ em

    # Status
    status = Column(String(20), default=TableStatus.AVAILABLE.value)
    is_active = Column(Boolean, default=True)  # Bàn có hoạt động không

    # Metadata
    priority = Column(Integer, default=0)  # Ưu tiên xếp khách (VIP = cao hơn)
    notes = Column(String(500))  # Ghi chú nội bộ

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Table {self.table_number} ({self.max_capacity}席)>"


class TableAssignment(Base):
    """Link booking to specific table(s)"""
    __tablename__ = "table_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=False, index=True)
    table_id = Column(String(36), ForeignKey("tables.id"), nullable=False, index=True)

    # Time tracking
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    seated_at = Column(DateTime(timezone=True))   # Khi khách ngồi
    cleared_at = Column(DateTime(timezone=True))  # Khi khách rời đi

    # Notes
    notes = Column(String(500))

    # Relationships
    booking = relationship("Booking", backref="table_assignments")
    table = relationship("Table", backref="assignments")


class TableAvailability(Base):
    """Pre-calculated table availability for fast lookup"""
    __tablename__ = "table_availability"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)
    table_id = Column(String(36), ForeignKey("tables.id"), nullable=False)

    # Time slot
    date = Column(DateTime, nullable=False, index=True)
    time_slot = Column(String(5), nullable=False)  # "18:00"

    # Status
    is_available = Column(Boolean, default=True)
    booking_id = Column(String(36), ForeignKey("bookings.id"))

    # Composite index for fast lookup
    __table_args__ = (
        # Index for finding availability
        # CREATE INDEX ix_availability_lookup ON table_availability(branch_code, date, time_slot, is_available)
    )


```

## File ./backend\app\models\__init__.py:
```python
﻿"""
SQLAlchemy Models
"""
from app.models.branch import Branch
from app.models.customer import Customer, GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference
from app.models.booking import Booking
from app.models.chat import ChatMessage, ChatInsight
from app.models.table import Table, TableAssignment, TableAvailability
from app.models.menu import MenuItem, MenuCategory
from app.models.order import Order, OrderItem, TableSession, OrderStatus
from app.models.staff import Staff, StaffRole

# New enhanced menu models
from app.models.category import ItemCategory
from app.models.item import Item, ItemOptionGroup, ItemOption, ItemOptionAssignment
from app.models.combo import Combo, ComboItem
from app.models.promotion import Promotion, PromotionUsage

__all__ = [
    # Branch & Customer
    "Branch",
    "Customer",
    "GlobalCustomer",
    "BranchCustomer",
    "CustomerPreference",

    # Booking & Chat
    "Booking",
    "ChatMessage",
    "ChatInsight",

    # Tables
    "Table",
    "TableAssignment",
    "TableAvailability",

    # Menu (legacy)
    "MenuItem",
    "MenuCategory",

    # Menu (new - enhanced)
    "ItemCategory",
    "Item",
    "ItemOptionGroup",
    "ItemOption",
    "ItemOptionAssignment",

    # Combos & Promotions
    "Combo",
    "ComboItem",
    "Promotion",
    "PromotionUsage",

    # Orders
    "Order",
    "OrderItem",
    "TableSession",
    "OrderStatus",

    # Staff
    "Staff",
    "StaffRole",
]

```

## File ./backend\app\routers\bookings.py:
```python
﻿"""
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

```

## File ./backend\app\routers\branches.py:
```python
﻿"""
Branches Router - Branch management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchResponse

router = APIRouter()


@router.get("/", response_model=List[BranchResponse])
async def list_branches(
    db: AsyncSession = Depends(get_db),
):
    """List all active branches"""
    result = await db.execute(
        select(Branch).where(Branch.is_active == True).order_by(Branch.code)
    )
    branches = result.scalars().all()

    return [
        BranchResponse(
            id=b.id,
            code=b.code,
            name=b.name,
            subdomain=b.subdomain,
            phone=b.phone,
            address=b.address,
            theme_primary_color=b.theme_primary_color or "#d4af37",
            theme_bg_color=b.theme_bg_color or "#1a1a1a",
            opening_time=str(b.opening_time) if b.opening_time else "17:00",
            closing_time=str(b.closing_time) if b.closing_time else "23:00",
            closed_days=b.closed_days or [2],
            max_capacity=b.max_capacity or 30,
            features=b.features or {},
            is_active=b.is_active,
        )
        for b in branches
    ]


@router.get("/{branch_code}", response_model=BranchResponse)
async def get_branch(
    branch_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Get branch by code"""
    result = await db.execute(select(Branch).where(Branch.code == branch_code))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    return BranchResponse(
        id=branch.id,
        code=branch.code,
        name=branch.name,
        subdomain=branch.subdomain,
        phone=branch.phone,
        address=branch.address,
        theme_primary_color=branch.theme_primary_color or "#d4af37",
        theme_bg_color=branch.theme_bg_color or "#1a1a1a",
        opening_time=str(branch.opening_time) if branch.opening_time else "17:00",
        closing_time=str(branch.closing_time) if branch.closing_time else "23:00",
        closed_days=branch.closed_days or [2],
        max_capacity=branch.max_capacity or 30,
        features=branch.features or {},
        is_active=branch.is_active,
    )


@router.post("/", response_model=BranchResponse, status_code=201)
async def create_branch(
    branch: BranchCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new branch"""
    # Check if code already exists
    existing = await db.execute(select(Branch).where(Branch.code == branch.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Branch code already exists")

    db_branch = Branch(
        code=branch.code,
        name=branch.name,
        subdomain=branch.subdomain or branch.code,
        phone=branch.phone,
        address=branch.address,
        theme_primary_color=branch.theme_primary_color,
        theme_bg_color=branch.theme_bg_color,
        closed_days=branch.closed_days,
        max_capacity=branch.max_capacity,
    )

    db.add(db_branch)
    await db.commit()
    await db.refresh(db_branch)

    return BranchResponse(
        id=db_branch.id,
        code=db_branch.code,
        name=db_branch.name,
        subdomain=db_branch.subdomain,
        phone=db_branch.phone,
        address=db_branch.address,
        theme_primary_color=db_branch.theme_primary_color or "#d4af37",
        theme_bg_color=db_branch.theme_bg_color or "#1a1a1a",
        opening_time=str(db_branch.opening_time) if db_branch.opening_time else "17:00",
        closing_time=str(db_branch.closing_time) if db_branch.closing_time else "23:00",
        closed_days=db_branch.closed_days or [2],
        max_capacity=db_branch.max_capacity or 30,
        features=db_branch.features or {},
        is_active=db_branch.is_active,
    )


@router.post("/seed")
async def seed_default_branch(
    db: AsyncSession = Depends(get_db),
):
    """Seed default Hirama branch"""
    existing = await db.execute(select(Branch).where(Branch.code == "hirama"))
    if existing.scalar_one_or_none():
        return {"message": "Default branch already exists"}

    hirama = Branch(
        code="hirama",
        name="Yakiniku 平間本店",
        subdomain="hirama",
        phone="044-789-8413",
        address="〒211-0013 神奈川県川崎市中原区上平間XXXX",
        theme_primary_color="#d4af37",
        theme_bg_color="#1a1a1a",
        closed_days=[2],
        max_capacity=30,
        features={
            "chat": True,
            "ai_booking": True,
            "customer_insights": True,
        },
    )

    db.add(hirama)
    await db.commit()

    return {"message": "Default branch created", "code": "hirama"}

```

## File ./backend\app\routers\chat.py:
```python
﻿"""
Chat Router - AI-powered customer chat with automatic insight extraction
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service, insight_extractor
from app.models.customer import BranchCustomer, GlobalCustomer

router = APIRouter()


async def get_branch_customer_id(
    db: AsyncSession,
    phone: Optional[str],
    branch_code: str = "hirama"
) -> Optional[str]:
    """Get branch_customer_id from phone number"""
    if not phone:
        return None

    # Get global customer by phone
    result = await db.execute(
        select(GlobalCustomer).where(GlobalCustomer.phone == phone)
    )
    global_customer = result.scalar_one_or_none()
    if not global_customer:
        return None

    # Get branch customer for this global customer and branch
    result = await db.execute(
        select(BranchCustomer)
        .where(BranchCustomer.global_customer_id == global_customer.id)
        .where(BranchCustomer.branch_code == branch_code)
    )
    bc = result.scalar_one_or_none()
    return bc.id if bc else None


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Process a chat message and return AI response.

    - Uses OpenAI GPT for intelligent responses
    - Falls back to keyword matching if OpenAI unavailable
    - Includes customer context for personalized responses
    - Extracts customer preferences automatically
    """
    # Convert conversation history to dict format
    history = None
    if request.conversation_history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

    # Get AI response
    response_text = await chat_service.chat(
        message=request.message,
        db=db,
        phone=request.customer_phone,
        customer_name=request.customer_name,
        branch_code=request.branch_code,
        conversation_history=history,
    )

    # Check if customer was recognized
    customer_recognized = False
    insights_extracted = 0

    if request.customer_phone or request.customer_name:
        customer_recognized = True

        # Extract insights from conversation (including current message)
        if request.customer_phone:
            try:
                # Build full conversation for extraction
                messages_for_extraction = history or []
                messages_for_extraction.append({
                    "role": "user",
                    "content": request.message
                })

                # Extract insights
                insights = await insight_extractor.extract_insights(
                    messages=messages_for_extraction
                )

                # Save if customer exists
                if insights:
                    branch_customer_id = await get_branch_customer_id(
                        db=db,
                        phone=request.customer_phone,
                        branch_code=request.branch_code or "hirama"
                    )

                    if branch_customer_id:
                        insights_extracted = await insight_extractor.save_insights(
                            db=db,
                            branch_customer_id=branch_customer_id,
                            insights=insights
                        )

            except Exception as e:
                print(f"Insight extraction failed: {e}")

    return ChatResponse(
        response=response_text,
        customer_recognized=customer_recognized,
        customer_name=request.customer_name,
        insights_extracted=insights_extracted,
    )


@router.get("/health")
async def chat_health():
    """Check if chat service is available"""
    has_openai = chat_service.client is not None
    return {
        "status": "healthy",
        "openai_configured": has_openai,
        "fallback_available": True,
    }


```

## File ./backend\app\routers\customers.py:
```python
﻿"""
Customers Router - Customer lookup and preferences
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.customer import GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference
from app.schemas.customer import CustomerCreate, CustomerResponse, PreferenceCreate, PreferenceResponse

router = APIRouter()


@router.post("/identify", response_model=CustomerResponse)
async def identify_customer(
    customer: CustomerCreate,
    branch_code: str = Query(default="hirama"),
    db: AsyncSession = Depends(get_db),
):
    """
    Identify or create customer by phone.
    Returns customer with preferences for the branch.
    """
    # Find or create global customer
    result = await db.execute(
        select(GlobalCustomer).where(GlobalCustomer.phone == customer.phone)
    )
    global_customer = result.scalar_one_or_none()

    if not global_customer:
        # Create new global customer
        global_customer = GlobalCustomer(
            phone=customer.phone,
            name=customer.name,
            email=customer.email,
        )
        db.add(global_customer)
        await db.commit()
        await db.refresh(global_customer)

    # Find or create branch customer relationship
    result = await db.execute(
        select(BranchCustomer)
        .options(selectinload(BranchCustomer.preferences))
        .where(
            BranchCustomer.global_customer_id == global_customer.id,
            BranchCustomer.branch_code == branch_code,
        )
    )
    branch_customer = result.scalar_one_or_none()

    if not branch_customer:
        branch_customer = BranchCustomer(
            global_customer_id=global_customer.id,
            branch_code=branch_code,
        )
        db.add(branch_customer)
        await db.commit()
        await db.refresh(branch_customer)
        # Reload with preferences
        result = await db.execute(
            select(BranchCustomer)
            .options(selectinload(BranchCustomer.preferences))
            .where(BranchCustomer.id == branch_customer.id)
        )
        branch_customer = result.scalar_one()

    return CustomerResponse(
        id=branch_customer.id,
        phone=global_customer.phone,
        name=global_customer.name,
        email=global_customer.email,
        visit_count=branch_customer.visit_count or 0,
        is_vip=branch_customer.is_vip or False,
        preferences=[
            PreferenceResponse(
                id=p.id,
                preference=p.preference,
                category=p.category,
                note=p.note,
                confidence=p.confidence or 1.0,
                source=p.source or "manual",
            )
            for p in (branch_customer.preferences or [])
        ],
    )


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    branch_code: str = Query(default="hirama"),
    vip_only: bool = Query(default=False),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List customers for a branch"""
    query = (
        select(BranchCustomer, GlobalCustomer)
        .join(GlobalCustomer, BranchCustomer.global_customer_id == GlobalCustomer.id)
        .options(selectinload(BranchCustomer.preferences))
        .where(BranchCustomer.branch_code == branch_code)
    )

    if vip_only:
        query = query.where(BranchCustomer.is_vip == True)

    if search:
        query = query.where(
            GlobalCustomer.name.ilike(f"%{search}%")
            | GlobalCustomer.phone.ilike(f"%{search}%")
        )

    query = query.order_by(BranchCustomer.visit_count.desc())

    result = await db.execute(query)
    rows = result.all()

    return [
        CustomerResponse(
            id=bc.id,
            phone=gc.phone,
            name=gc.name,
            email=gc.email,
            visit_count=bc.visit_count or 0,
            is_vip=bc.is_vip or False,
            preferences=[
                PreferenceResponse(
                    id=p.id,
                    preference=p.preference,
                    category=p.category,
                    note=p.note,
                    confidence=p.confidence or 1.0,
                    source=p.source or "manual",
                )
                for p in (bc.preferences or [])
            ],
        )
        for bc, gc in rows
    ]


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get customer by ID"""
    result = await db.execute(
        select(BranchCustomer, GlobalCustomer)
        .join(GlobalCustomer, BranchCustomer.global_customer_id == GlobalCustomer.id)
        .options(selectinload(BranchCustomer.preferences))
        .where(BranchCustomer.id == customer_id)
    )
    row = result.one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")

    bc, gc = row
    return CustomerResponse(
        id=bc.id,
        phone=gc.phone,
        name=gc.name,
        email=gc.email,
        visit_count=bc.visit_count or 0,
        is_vip=bc.is_vip or False,
        preferences=[
            PreferenceResponse(
                id=p.id,
                preference=p.preference,
                category=p.category,
                note=p.note,
                confidence=p.confidence or 1.0,
                source=p.source or "manual",
            )
            for p in (bc.preferences or [])
        ],
    )


@router.post("/{customer_id}/preferences", response_model=PreferenceResponse, status_code=201)
async def add_preference(
    customer_id: str,
    preference: PreferenceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a preference to customer"""
    # Check customer exists
    result = await db.execute(
        select(BranchCustomer).where(BranchCustomer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create preference
    db_preference = CustomerPreference(
        branch_customer_id=customer_id,
        preference=preference.preference,
        category=preference.category,
        note=preference.note,
        confidence=preference.confidence,
        source=preference.source,
    )

    db.add(db_preference)
    await db.commit()
    await db.refresh(db_preference)

    return PreferenceResponse(
        id=db_preference.id,
        preference=db_preference.preference,
        category=db_preference.category,
        note=db_preference.note,
        confidence=db_preference.confidence or 1.0,
        source=db_preference.source or "manual",
    )


@router.patch("/{customer_id}/vip")
async def toggle_vip(
    customer_id: str,
    is_vip: bool = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Toggle VIP status"""
    result = await db.execute(
        select(BranchCustomer).where(BranchCustomer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.is_vip = is_vip
    await db.commit()

    return {"id": customer_id, "is_vip": is_vip}


```

## File ./backend\app\routers\dashboard.py:
```python
﻿"""
Dashboard Router - Staff management interface
HTMX-powered for real-time updates
"""
from fastapi import APIRouter, Depends, Request, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.booking import Booking
from app.models.customer import GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference

router = APIRouter()

# Templates - relative to backend folder
templates = Jinja2Templates(directory="../dashboard/templates")


# ============================================
# MAIN DASHBOARD
# ============================================
@router.get("/", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
):
    """Main dashboard with today's overview"""
    today = date.today()

    # Get today's bookings
    result = await db.execute(
        select(Booking)
        .where(
            Booking.branch_code == branch_code,
            Booking.date == today
        )
        .order_by(Booking.time)
    )
    today_bookings = result.scalars().all()

    # Get upcoming bookings (next 7 days)
    result = await db.execute(
        select(Booking)
        .where(
            Booking.branch_code == branch_code,
            Booking.date > today,
            Booking.date <= today + timedelta(days=7)
        )
        .order_by(Booking.date, Booking.time)
    )
    upcoming_bookings = result.scalars().all()

    # Stats
    total_guests_today = sum(b.guests for b in today_bookings)
    confirmed_count = sum(1 for b in today_bookings if b.status == "confirmed")
    pending_count = sum(1 for b in today_bookings if b.status == "pending")

    return templates.TemplateResponse("dashboard/home.html", {
        "request": request,
        "active": "home",
        "today": today,
        "today_bookings": today_bookings,
        "upcoming_bookings": upcoming_bookings,
        "stats": {
            "total_bookings": len(today_bookings),
            "total_guests": total_guests_today,
            "confirmed": confirmed_count,
            "pending": pending_count,
        },
        "branch_code": branch_code,
    })


# ============================================
# BOOKINGS MANAGEMENT
# ============================================
@router.get("/bookings", response_class=HTMLResponse)
async def bookings_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    booking_date: Optional[str] = None,
    status: Optional[str] = None,
):
    """Bookings list with filters"""
    query = select(Booking).where(Booking.branch_code == branch_code)

    # Date filter
    filter_date = date.today()
    if booking_date:
        try:
            filter_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    query = query.where(Booking.date == filter_date)

    if status:
        query = query.where(Booking.status == status)

    query = query.order_by(Booking.time)

    result = await db.execute(query)
    bookings = result.scalars().all()

    return templates.TemplateResponse("dashboard/bookings.html", {
        "request": request,
        "active": "bookings",
        "bookings": bookings,
        "filter_date": filter_date,
        "filter_status": status,
        "branch_code": branch_code,
    })


@router.get("/bookings/{booking_id}", response_class=HTMLResponse)
async def booking_detail(
    request: Request,
    booking_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Booking detail modal content"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        return HTMLResponse("<p>予約が見つかりません</p>", status_code=404)

    # Get customer info if exists
    customer = None
    if booking.guest_phone:
        result = await db.execute(
            select(GlobalCustomer).where(GlobalCustomer.phone == booking.guest_phone)
        )
        customer = result.scalar_one_or_none()

    return templates.TemplateResponse("dashboard/partials/booking_detail.html", {
        "request": request,
        "booking": booking,
        "customer": customer,
    })


@router.put("/bookings/{booking_id}/status", response_class=HTMLResponse)
async def update_booking_status(
    request: Request,
    booking_id: str,
    status: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Update booking status (HTMX)"""
    from app.services.notification_service import notify_booking_confirmed, notify_booking_cancelled

    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        return HTMLResponse("<p>エラー</p>", status_code=404)

    old_status = booking.status
    booking.status = status
    await db.commit()
    await db.refresh(booking)

    # Send notification for status change
    if status == "confirmed" and old_status != "confirmed":
        await notify_booking_confirmed(
            branch_code=booking.branch_code,
            guest_name=booking.guest_name or "ゲスト",
            booking_date=booking.date.isoformat(),
            booking_time=booking.time,
            booking_id=booking.id,
        )
    elif status == "cancelled" and old_status != "cancelled":
        await notify_booking_cancelled(
            branch_code=booking.branch_code,
            guest_name=booking.guest_name or "ゲスト",
            booking_date=booking.date.isoformat(),
            booking_time=booking.time,
            booking_id=booking.id,
        )

    return templates.TemplateResponse("dashboard/partials/booking_row.html", {
        "request": request,
        "booking": booking,
    })


@router.put("/bookings/{booking_id}/note", response_class=HTMLResponse)
async def update_booking_note(
    request: Request,
    booking_id: str,
    staff_note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Update staff note on booking"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if booking:
        booking.staff_note = staff_note
        await db.commit()

    return HTMLResponse(f'<span class="text-green-400">✓ 保存しました</span>')


# ============================================
# CUSTOMER INSIGHTS
# ============================================
@router.get("/customers", response_class=HTMLResponse)
async def customers_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    search: Optional[str] = None,
    id: Optional[str] = Query(default=None),
):
    """Customer list with search. If id is provided, show customer detail."""
    # If id is provided, redirect to customer detail
    if id:
        return await customer_detail(request, id, db, branch_code)
    query = (
        select(BranchCustomer)
        .options(
            selectinload(BranchCustomer.global_customer),
            selectinload(BranchCustomer.preferences)
        )
        .where(BranchCustomer.branch_code == branch_code)
    )

    if search:
        # Search by phone or name via global_customer
        query = query.join(GlobalCustomer).where(
            (GlobalCustomer.phone.ilike(f"%{search}%")) |
            (GlobalCustomer.name.ilike(f"%{search}%"))
        )

    query = query.order_by(BranchCustomer.visit_count.desc())

    result = await db.execute(query)
    customers = result.scalars().all()

    return templates.TemplateResponse("dashboard/customers.html", {
        "request": request,
        "active": "customers",
        "customers": customers,
        "search": search,
        "branch_code": branch_code,
    })


@router.get("/customers/{customer_id}", response_class=HTMLResponse)
async def customer_detail(
    request: Request,
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
):
    """Customer detail with history"""
    # Get branch customer
    result = await db.execute(
        select(BranchCustomer)
        .options(
            selectinload(BranchCustomer.global_customer),
            selectinload(BranchCustomer.preferences)
        )
        .where(BranchCustomer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        return HTMLResponse("<p>顧客が見つかりません</p>", status_code=404)

    # Get booking history
    result = await db.execute(
        select(Booking)
        .where(Booking.guest_phone == customer.global_customer.phone)
        .order_by(Booking.date.desc())
        .limit(10)
    )
    bookings = result.scalars().all()

    return templates.TemplateResponse("dashboard/partials/customer_detail.html", {
        "request": request,
        "customer": customer,
        "bookings": bookings,
    })


@router.post("/customers/{customer_id}/preference", response_class=HTMLResponse)
async def add_customer_preference(
    request: Request,
    customer_id: str,
    preference: str = Form(...),
    category: str = Form(default="meat"),
    note: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
):
    """Add preference to customer"""
    new_pref = CustomerPreference(
        branch_customer_id=customer_id,
        preference=preference,
        category=category,
        note=note,
        source="dashboard",
        confidence=1.0,
    )
    db.add(new_pref)
    await db.commit()

    return templates.TemplateResponse("dashboard/partials/preference_tag.html", {
        "request": request,
        "pref": new_pref,
    })


@router.put("/customers/{customer_id}/vip", response_class=HTMLResponse)
async def toggle_vip_status(
    request: Request,
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Toggle VIP status"""
    result = await db.execute(
        select(BranchCustomer).where(BranchCustomer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if customer:
        customer.is_vip = not customer.is_vip
        await db.commit()

        status = "VIP に設定しました ⭐" if customer.is_vip else "VIP を解除しました"
        return HTMLResponse(f'<span class="text-primary">{status}</span>')

    return HTMLResponse("<span>エラー</span>", status_code=404)


# ============================================
# QUICK SEARCH (HTMX)
# ============================================
@router.get("/search", response_class=HTMLResponse)
async def quick_search(
    request: Request,
    q: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
):
    """Quick search for customers by phone/name"""
    if len(q) < 2:
        return HTMLResponse("")

    result = await db.execute(
        select(GlobalCustomer)
        .where(
            (GlobalCustomer.phone.ilike(f"%{q}%")) |
            (GlobalCustomer.name.ilike(f"%{q}%"))
        )
        .limit(5)
    )
    customers = result.scalars().all()

    return templates.TemplateResponse("dashboard/partials/search_results.html", {
        "request": request,
        "customers": customers,
        "query": q,
    })


# ============================================
# TABLE MANAGEMENT (Dashboard Views)
# ============================================

@router.get("/tables", response_class=HTMLResponse)
async def tables_management(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
):
    """Table management with AI insights"""
    from app.models.table import Table
    from app.services.table_optimization import TableOptimizationService

    if target_date is None:
        target_date = date.today()

    # Get tables
    result = await db.execute(
        select(Table)
        .where(Table.branch_code == branch_code)
        .order_by(Table.zone, Table.table_number)
    )
    tables = result.scalars().all()

    # Convert to response format
    tables_data = [
        {
            "id": t.id,
            "table_number": t.table_number,
            "name": t.name,
            "max_capacity": t.max_capacity,
            "table_type": t.table_type,
            "zone": t.zone,
            "status": t.status,
            "is_active": t.is_active,
            "features": {
                "has_window": t.has_window,
                "has_baby_chair": t.has_baby_chair,
            }
        }
        for t in tables
    ]

    # Get AI insights
    insights = []
    slot_summaries = []
    gantt_data = {"tables": [], "time_slots": [], "unassigned_bookings": []}
    if tables:
        try:
            optimizer = TableOptimizationService(db, branch_code)
            insights_raw = await optimizer.generate_insights(target_date)
            insights = [
                {
                    "type": i.type,
                    "title": i.title,
                    "message": i.message,
                    "priority": i.priority,
                    "action": i.action,
                }
                for i in insights_raw
            ]

            summaries_raw = await optimizer.get_time_slot_summary(target_date)
            slot_summaries = [
                {
                    "time_slot": s.time_slot,
                    "total_tables": s.total_tables,
                    "available_tables": s.available_tables,
                    "utilization_rate": s.utilization_rate,
                }
                for s in summaries_raw
            ]

            # Get Gantt chart data
            gantt_data = await optimizer.get_gantt_data(target_date)
        except Exception as e:
            print(f"Error generating insights: {e}")
            import traceback
            traceback.print_exc()

    # Stats
    total_capacity = sum(t.max_capacity for t in tables)
    tables_4_seat = sum(1 for t in tables if t.max_capacity == 4)
    tables_6_seat = sum(1 for t in tables if t.max_capacity >= 6)

    return templates.TemplateResponse("dashboard/tables.html", {
        "request": request,
        "active": "tables",
        "tables": tables_data,
        "insights": insights,
        "slot_summaries": slot_summaries,
        "gantt_data": gantt_data,
        "target_date": target_date,
        "branch_code": branch_code,
        "total_tables": len(tables),
        "total_capacity": total_capacity,
        "tables_4_seat": tables_4_seat,
        "tables_6_seat": tables_6_seat,
    })


@router.get("/tables/gantt", response_class=HTMLResponse)
async def get_gantt_partial(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
):
    """Get Gantt chart as HTMX partial for real-time updates"""
    from app.models.table import Table
    from app.services.table_optimization import TableOptimizationService

    if target_date is None:
        target_date = date.today()

    # Get tables
    result = await db.execute(
        select(Table)
        .where(Table.branch_code == branch_code)
        .order_by(Table.zone, Table.table_number)
    )
    tables = result.scalars().all()

    # Get Gantt data
    gantt_data = {"tables": [], "time_slots": [], "unassigned_bookings": []}
    if tables:
        try:
            optimizer = TableOptimizationService(db, branch_code)
            gantt_data = await optimizer.get_gantt_data(target_date)
        except Exception as e:
            print(f"Error getting gantt data: {e}")

    return templates.TemplateResponse("dashboard/partials/gantt.html", {
        "request": request,
        "gantt_data": gantt_data,
        "target_date": target_date,
        "branch_code": branch_code,
    })


@router.get("/tables/insights", response_class=HTMLResponse)
async def get_table_insights_partial(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
):
    """Get AI insights as HTMX partial"""
    from app.services.table_optimization import TableOptimizationService

    if target_date is None:
        target_date = date.today()

    optimizer = TableOptimizationService(db, branch_code)
    insights_raw = await optimizer.generate_insights(target_date)
    insights = [
        {
            "type": i.type,
            "title": i.title,
            "message": i.message,
            "priority": i.priority,
            "action": i.action,
        }
        for i in insights_raw
    ]

    return templates.TemplateResponse("dashboard/partials/insights.html", {
        "request": request,
        "insights": insights,
    })


@router.post("/tables/seed", response_class=HTMLResponse)
async def seed_tables_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
):
    """Seed sample tables via dashboard"""
    from app.models.table import Table

    # Check if already seeded
    existing = await db.execute(
        select(Table).where(Table.branch_code == branch_code).limit(1)
    )
    if existing.scalar_one_or_none():
        return HTMLResponse('<div class="text-yellow-400 p-4">テーブルは既に設定されています。ページを更新してください。</div>')

    tables_config = [
        {"table_number": "A1", "name": "窓際席A", "max_capacity": 4, "zone": "A", "has_window": True},
        {"table_number": "A2", "name": "窓際席B", "max_capacity": 4, "zone": "A", "has_window": True},
        {"table_number": "B1", "name": "中央席A", "max_capacity": 4, "zone": "B"},
        {"table_number": "B2", "name": "中央席B", "max_capacity": 4, "zone": "B"},
        {"table_number": "C1", "name": "グループ席A", "max_capacity": 6, "zone": "C"},
        {"table_number": "C2", "name": "グループ席B", "max_capacity": 6, "zone": "C"},
        {"table_number": "C3", "name": "グループ席C", "max_capacity": 6, "zone": "C"},
        {"table_number": "VIP1", "name": "個室", "max_capacity": 8, "zone": "VIP", "table_type": "private", "priority": 10},
    ]

    for config in tables_config:
        table = Table(
            branch_code=branch_code,
            table_number=config["table_number"],
            name=config.get("name"),
            min_capacity=1,
            max_capacity=config["max_capacity"],
            table_type=config.get("table_type", "regular"),
            floor=1,
            zone=config.get("zone"),
            has_window=config.get("has_window", False),
            priority=config.get("priority", 0),
        )
        db.add(table)

    await db.commit()

    return HTMLResponse('<div class="text-green-400 p-4">✅ 8テーブルを生成しました。ページを更新してください。</div>')


@router.post("/tables/create", response_class=HTMLResponse)
async def create_table_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    table_number: str = Form(...),
    name: str = Form(default=None),
    max_capacity: int = Form(default=4),
    table_type: str = Form(default="regular"),
    zone: str = Form(default=None),
    has_window: bool = Form(default=False),
    has_baby_chair: bool = Form(default=False),
):
    """Create new table via dashboard form"""
    from app.models.table import Table

    # Check for duplicate
    existing = await db.execute(
        select(Table).where(
            and_(
                Table.branch_code == branch_code,
                Table.table_number == table_number
            )
        )
    )
    if existing.scalar_one_or_none():
        return HTMLResponse('<div class="text-red-400 p-4">❌ このテーブル番号は既に存在します</div>')

    table = Table(
        branch_code=branch_code,
        table_number=table_number,
        name=name,
        min_capacity=1,
        max_capacity=max_capacity,
        table_type=table_type,
        floor=1,
        zone=zone,
        has_window=has_window,
        has_baby_chair=has_baby_chair,
    )
    db.add(table)
    await db.commit()

    return HTMLResponse(f'<div class="text-green-400 p-4">✅ {table_number} を追加しました。ページを更新してください。</div>')

```

## File ./backend\app\routers\menu.py:
```python
﻿"""
Menu Router - Menu items API for table ordering
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.menu import MenuItem, MenuCategory
from app.schemas.menu import MenuItemResponse, MenuCategoryResponse, MenuResponse

router = APIRouter()

# Category labels and icons for UI
CATEGORY_INFO = {
    "meat": {"label": "肉類", "icon": "🥩"},
    "drinks": {"label": "飲物", "icon": "🍺"},
    "salad": {"label": "サラダ", "icon": "🥗"},
    "rice": {"label": "ご飯・麺", "icon": "🍚"},
    "side": {"label": "サイドメニュー", "icon": "🍟"},
    "dessert": {"label": "デザート", "icon": "🍨"},
    "set": {"label": "セットメニュー", "icon": "🍱"},
}


@router.get("", response_model=List[MenuItemResponse])
async def get_menu_items(
    branch_code: str = "hirama",
    category: str = None,
    available_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items for a branch"""
    query = select(MenuItem).where(MenuItem.branch_code == branch_code)

    if category:
        query = query.where(MenuItem.category == category)

    if available_only:
        query = query.where(MenuItem.is_available == True)

    query = query.order_by(MenuItem.category, MenuItem.display_order, MenuItem.name)

    result = await db.execute(query)
    items = result.scalars().all()

    return items


@router.get("/categories", response_model=MenuResponse)
async def get_menu_by_category(
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """Get menu items grouped by category"""
    query = select(MenuItem).where(
        MenuItem.branch_code == branch_code,
        MenuItem.is_available == True
    ).order_by(MenuItem.category, MenuItem.display_order)

    result = await db.execute(query)
    items = result.scalars().all()

    # Group by category
    categories_dict = {}
    for item in items:
        cat = item.category
        if cat not in categories_dict:
            info = CATEGORY_INFO.get(cat, {"label": cat, "icon": "📦"})
            categories_dict[cat] = {
                "category": cat,
                "category_label": info["label"],
                "icon": info["icon"],
                "items": []
            }
        categories_dict[cat]["items"].append(item)

    # Maintain order
    category_order = ["meat", "drinks", "salad", "rice", "side", "dessert", "set"]
    categories = []
    for cat in category_order:
        if cat in categories_dict:
            categories.append(MenuCategoryResponse(**categories_dict[cat]))

    return MenuResponse(
        branch_code=branch_code,
        categories=categories,
        updated_at=datetime.now()
    )


@router.get("/popular", response_model=List[MenuItemResponse])
async def get_popular_items(
    branch_code: str = "hirama",
    limit: int = 6,
    db: AsyncSession = Depends(get_db)
):
    """Get popular/recommended menu items"""
    query = select(MenuItem).where(
        MenuItem.branch_code == branch_code,
        MenuItem.is_available == True,
        MenuItem.is_popular == True
    ).order_by(MenuItem.display_order).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    return items


@router.get("/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get single menu item details"""
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return item

```

## File ./backend\app\routers\notifications.py:
```python
﻿"""
Notification Router - SSE endpoint for real-time notifications
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse
import asyncio

from app.services.notification_service import notification_manager

router = APIRouter()


async def event_generator(request: Request, branch_code: str):
    """Generate SSE events for connected clients"""
    queue = await notification_manager.connect(branch_code)

    try:
        # Send initial connection message
        yield "event: connected\ndata: {\"status\": \"connected\"}\n\n"

        while True:
            # Check if server is shutting down (checked frequently)
            if notification_manager.shutdown_event.is_set():
                yield "event: shutdown\ndata: {\"status\": \"server_shutdown\"}\n\n"
                break

            # Check if client disconnected
            try:
                if await request.is_disconnected():
                    break
            except asyncio.CancelledError:
                # Server shutting down - exit gracefully
                break

            try:
                # Wait for notification with SHORT timeout for responsive shutdown
                notification = await asyncio.wait_for(
                    queue.get(),
                    timeout=1.0  # Check shutdown every 1 second
                )
                # None means shutdown signal
                if notification is None:
                    yield "event: shutdown\ndata: {\"status\": \"server_shutdown\"}\n\n"
                    break
                yield notification.to_sse()
            except asyncio.TimeoutError:
                # Every 30 timeouts (~30 seconds), send keepalive
                pass
            except asyncio.CancelledError:
                # Server shutting down - exit gracefully
                break

    except asyncio.CancelledError:
        # Outer catch for any remaining CancelledError
        pass
    finally:
        try:
            await notification_manager.disconnect(branch_code, queue)
        except asyncio.CancelledError:
            # Ignore CancelledError during cleanup
            pass


@router.get("/stream")
async def notification_stream(
    request: Request,
    branch_code: str = Query(default="hirama"),
):
    """
    SSE endpoint for real-time notifications.

    Connect to this endpoint to receive notifications:
    - new_booking: New booking created
    - booking_cancelled: Booking cancelled
    - booking_confirmed: Booking confirmed
    - vip_arrived: VIP customer arrived

    Usage:
    ```javascript
    const eventSource = new EventSource('/api/notifications/stream?branch_code=JIAN');
    eventSource.onmessage = (event) => {
        const notification = JSON.parse(event.data);
        console.log(notification);
    };
    ```
    """
    return StreamingResponse(
        event_generator(request, branch_code),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/clients")
async def get_connected_clients(
    branch_code: str = Query(default=None),
):
    """Get number of connected notification clients"""
    return {
        "branch_code": branch_code,
        "connected_clients": notification_manager.get_client_count(branch_code),
    }

```

## File ./backend\app\routers\orders.py:
```python
﻿"""
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


```

## File ./backend\app\routers\tables.py:
```python
﻿"""
Tables Router - Table management and AI optimization API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.table import Table, TableAssignment, TableStatus, TableType
from app.models.booking import Booking
from app.services.table_optimization import TableOptimizationService


router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class TableCreate(BaseModel):
    table_number: str
    name: Optional[str] = None
    min_capacity: int = 1
    max_capacity: int
    table_type: str = "regular"
    floor: int = 1
    zone: Optional[str] = None
    has_window: bool = False
    is_smoking: bool = False
    is_wheelchair_accessible: bool = True
    has_baby_chair: bool = False
    priority: int = 0
    notes: Optional[str] = None


class TableUpdate(BaseModel):
    name: Optional[str] = None
    min_capacity: Optional[int] = None
    max_capacity: Optional[int] = None
    table_type: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    notes: Optional[str] = None


class TableResponse(BaseModel):
    id: str
    table_number: str
    name: Optional[str]
    min_capacity: int
    max_capacity: int
    table_type: str
    floor: int
    zone: Optional[str]
    status: str
    is_active: bool
    features: dict

    class Config:
        from_attributes = True


class SlotSummaryResponse(BaseModel):
    time_slot: str
    total_tables: int
    available_tables: int
    occupied_tables: int
    total_capacity: int
    used_capacity: int
    available_capacity: int
    utilization_rate: float


class InsightResponse(BaseModel):
    type: str
    title: str
    message: str
    priority: int
    action: Optional[str]
    data: Optional[dict]


# ============================================
# TABLE CRUD
# ============================================

@router.get("/", response_model=List[TableResponse])
async def list_tables(
    branch_code: str = Query(default="hirama"),
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    """List all tables for a branch"""
    query = select(Table).where(Table.branch_code == branch_code)

    if not include_inactive:
        query = query.where(Table.is_active == True)

    query = query.order_by(Table.floor, Table.zone, Table.table_number)

    result = await db.execute(query)
    tables = result.scalars().all()

    return [
        TableResponse(
            id=t.id,
            table_number=t.table_number,
            name=t.name,
            min_capacity=t.min_capacity,
            max_capacity=t.max_capacity,
            table_type=t.table_type,
            floor=t.floor,
            zone=t.zone,
            status=t.status,
            is_active=t.is_active,
            features={
                "has_window": t.has_window,
                "is_smoking": t.is_smoking,
                "is_wheelchair_accessible": t.is_wheelchair_accessible,
                "has_baby_chair": t.has_baby_chair,
            }
        )
        for t in tables
    ]


@router.post("/", response_model=TableResponse, status_code=201)
async def create_table(
    table: TableCreate,
    branch_code: str = Query(default="hirama"),
    db: AsyncSession = Depends(get_db),
):
    """Create a new table"""
    # Check for duplicate table number
    existing = await db.execute(
        select(Table).where(
            and_(
                Table.branch_code == branch_code,
                Table.table_number == table.table_number
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Table number already exists")

    db_table = Table(
        branch_code=branch_code,
        table_number=table.table_number,
        name=table.name,
        min_capacity=table.min_capacity,
        max_capacity=table.max_capacity,
        table_type=table.table_type,
        floor=table.floor,
        zone=table.zone,
        has_window=table.has_window,
        is_smoking=table.is_smoking,
        is_wheelchair_accessible=table.is_wheelchair_accessible,
        has_baby_chair=table.has_baby_chair,
        priority=table.priority,
        notes=table.notes,
    )

    db.add(db_table)
    await db.commit()
    await db.refresh(db_table)

    return TableResponse(
        id=db_table.id,
        table_number=db_table.table_number,
        name=db_table.name,
        min_capacity=db_table.min_capacity,
        max_capacity=db_table.max_capacity,
        table_type=db_table.table_type,
        floor=db_table.floor,
        zone=db_table.zone,
        status=db_table.status,
        is_active=db_table.is_active,
        features={
            "has_window": db_table.has_window,
            "is_smoking": db_table.is_smoking,
            "is_wheelchair_accessible": db_table.is_wheelchair_accessible,
            "has_baby_chair": db_table.has_baby_chair,
        }
    )


@router.patch("/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: str,
    update: TableUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a table"""
    result = await db.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    if update.name is not None:
        table.name = update.name
    if update.min_capacity is not None:
        table.min_capacity = update.min_capacity
    if update.max_capacity is not None:
        table.max_capacity = update.max_capacity
    if update.table_type is not None:
        table.table_type = update.table_type
    if update.status is not None:
        table.status = update.status
    if update.is_active is not None:
        table.is_active = update.is_active
    if update.priority is not None:
        table.priority = update.priority
    if update.notes is not None:
        table.notes = update.notes

    await db.commit()
    await db.refresh(table)

    return TableResponse(
        id=table.id,
        table_number=table.table_number,
        name=table.name,
        min_capacity=table.min_capacity,
        max_capacity=table.max_capacity,
        table_type=table.table_type,
        floor=table.floor,
        zone=table.zone,
        status=table.status,
        is_active=table.is_active,
        features={
            "has_window": table.has_window,
            "is_smoking": table.is_smoking,
            "is_wheelchair_accessible": table.is_wheelchair_accessible,
            "has_baby_chair": table.has_baby_chair,
        }
    )


@router.delete("/{table_id}", status_code=204)
async def delete_table(
    table_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a table (soft delete - sets is_active=False)"""
    result = await db.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table.is_active = False
    await db.commit()


# ============================================
# AI OPTIMIZATION ENDPOINTS
# ============================================

@router.get("/optimization/summary", response_model=List[SlotSummaryResponse])
async def get_slot_summary(
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Get utilization summary for all time slots"""
    if target_date is None:
        target_date = date.today()

    optimizer = TableOptimizationService(db, branch_code)
    summaries = await optimizer.get_time_slot_summary(target_date)

    return [
        SlotSummaryResponse(
            time_slot=s.time_slot,
            total_tables=s.total_tables,
            available_tables=s.available_tables,
            occupied_tables=s.occupied_tables,
            total_capacity=s.total_capacity,
            used_capacity=s.used_capacity,
            available_capacity=s.available_capacity,
            utilization_rate=s.utilization_rate,
        )
        for s in summaries
    ]


@router.get("/optimization/insights", response_model=List[InsightResponse])
async def get_ai_insights(
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated insights and suggestions"""
    if target_date is None:
        target_date = date.today()

    optimizer = TableOptimizationService(db, branch_code)
    insights = await optimizer.generate_insights(target_date)

    return [
        InsightResponse(
            type=i.type,
            title=i.title,
            message=i.message,
            priority=i.priority,
            action=i.action,
            data=i.data,
        )
        for i in insights
    ]


@router.get("/optimization/check")
async def check_table_availability(
    branch_code: str = Query(default="hirama"),
    booking_date: date = Query(...),
    time_slot: str = Query(...),
    guests: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Check if tables are available and get suggestions"""
    optimizer = TableOptimizationService(db, branch_code)
    result = await optimizer.check_availability(guests, booking_date, time_slot)

    return {
        "available": result["available"],
        "message": result["message"],
        "suggestions": [
            {
                "table_number": t.table_number,
                "capacity": t.capacity,
                "score": t.score,
                "reason": t.reason,
                "waste": t.waste,
            }
            for t in result["tables"]
        ],
        "alternatives": [
            {
                "time": a["time"],
                "diff_minutes": a["diff_minutes"],
            }
            for a in result.get("alternatives", [])
        ]
    }


@router.post("/optimization/assign/{booking_id}")
async def assign_table_to_booking(
    booking_id: str,
    table_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Assign a table to a booking (manual or auto)"""
    # Get booking
    booking_result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = booking_result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    optimizer = TableOptimizationService(db, booking.branch_code)

    if table_id:
        # Manual assignment
        assignment = await optimizer.reassign_table(booking_id, table_id, "Manual assignment")
    else:
        # Auto assignment
        assignment = await optimizer.auto_assign_table(
            booking_id,
            booking.guests,
            booking.date,
            booking.time
        )

    if not assignment:
        raise HTTPException(status_code=400, detail="No suitable table found")

    # Get table info
    table_result = await db.execute(
        select(Table).where(Table.id == assignment.table_id)
    )
    table = table_result.scalar_one_or_none()

    return {
        "success": True,
        "assignment_id": assignment.id,
        "table": {
            "id": table.id,
            "table_number": table.table_number,
            "capacity": table.max_capacity,
        } if table else None,
        "notes": assignment.notes,
    }


# ============================================
# SEED DATA FOR TESTING
# ============================================

@router.post("/seed", status_code=201)
async def seed_tables(
    branch_code: str = Query(default="hirama"),
    db: AsyncSession = Depends(get_db),
):
    """
    Seed sample tables for testing.
    Creates 8 tables: 4x 4-seat, 3x 6-seat, 1x 8-seat VIP
    """
    # Check if already seeded
    existing = await db.execute(
        select(Table).where(Table.branch_code == branch_code).limit(1)
    )
    if existing.scalar_one_or_none():
        return {"message": "Tables already exist", "seeded": False}

    tables_config = [
        # 4-seat regular tables
        {"table_number": "A1", "name": "窓際席A", "max_capacity": 4, "zone": "A", "has_window": True},
        {"table_number": "A2", "name": "窓際席B", "max_capacity": 4, "zone": "A", "has_window": True},
        {"table_number": "B1", "name": "中央席A", "max_capacity": 4, "zone": "B"},
        {"table_number": "B2", "name": "中央席B", "max_capacity": 4, "zone": "B"},
        # 6-seat tables
        {"table_number": "C1", "name": "グループ席A", "max_capacity": 6, "zone": "C"},
        {"table_number": "C2", "name": "グループ席B", "max_capacity": 6, "zone": "C"},
        {"table_number": "C3", "name": "グループ席C", "max_capacity": 6, "zone": "C"},
        # VIP room
        {"table_number": "VIP1", "name": "個室", "max_capacity": 8, "zone": "VIP",
         "table_type": "private", "priority": 10},
    ]

    created = []
    for config in tables_config:
        table = Table(
            branch_code=branch_code,
            table_number=config["table_number"],
            name=config.get("name"),
            min_capacity=1,
            max_capacity=config["max_capacity"],
            table_type=config.get("table_type", "regular"),
            floor=1,
            zone=config.get("zone"),
            has_window=config.get("has_window", False),
            priority=config.get("priority", 0),
        )
        db.add(table)
        created.append(config["table_number"])

    await db.commit()

    return {
        "message": f"Created {len(created)} tables",
        "seeded": True,
        "tables": created,
    }

```

## File ./backend\app\routers\websocket.py:
```python
﻿"""
WebSocket Router for Real-time Dashboard Communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections per branch"""

    def __init__(self):
        # branch_code -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> subscribed channels
        self.subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket, branch_code: str):
        """Accept and register a new connection"""
        await websocket.accept()

        if branch_code not in self.active_connections:
            self.active_connections[branch_code] = set()

        self.active_connections[branch_code].add(websocket)
        self.subscriptions[websocket] = set()

        print(f"📡 WebSocket connected: branch={branch_code}, total={len(self.active_connections[branch_code])}")

        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "data": {
                "branch": branch_code,
                "timestamp": datetime.now().isoformat()
            }
        })

    def disconnect(self, websocket: WebSocket, branch_code: str):
        """Remove a connection"""
        if branch_code in self.active_connections:
            self.active_connections[branch_code].discard(websocket)

        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

        print(f"📡 WebSocket disconnected: branch={branch_code}")

    def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe to a channel"""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].add(channel)
            print(f"📡 Subscribed to channel: {channel}")

    def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe from a channel"""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(channel)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"❌ Failed to send personal message: {e}")

    async def broadcast_to_branch(self, branch_code: str, message: dict, channel: str = None):
        """Broadcast message to all connections in a branch"""
        if branch_code not in self.active_connections:
            return

        disconnected = set()

        for websocket in self.active_connections[branch_code]:
            # If channel specified, only send to subscribed connections
            if channel and websocket in self.subscriptions:
                if channel not in self.subscriptions[websocket]:
                    continue

            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        # Clean up disconnected
        for ws in disconnected:
            self.disconnect(ws, branch_code)

    async def broadcast_all(self, message: dict, channel: str = None):
        """Broadcast to all branches"""
        for branch_code in list(self.active_connections.keys()):
            await self.broadcast_to_branch(branch_code, message, channel)

    def get_connection_count(self, branch_code: str = None) -> int:
        """Get number of active connections"""
        if branch_code:
            return len(self.active_connections.get(branch_code, set()))
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()


@router.websocket("")
async def table_websocket(
    websocket: WebSocket,
    branch_code: str = Query(default="hirama"),
    table_id: str = Query(default="")
):
    """WebSocket endpoint for table-order app real-time updates"""
    await manager.connect(websocket, branch_code)

    # Auto-subscribe to orders channel for this table
    manager.subscribe(websocket, "orders")
    if table_id:
        manager.subscribe(websocket, f"table:{table_id}")

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type")

                if msg_type == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})
                elif msg_type == "subscribe":
                    channel = message.get("channel")
                    if channel:
                        manager.subscribe(websocket, channel)
                else:
                    print(f"📨 Table WS received: {msg_type}")

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, branch_code)
    except Exception as e:
        print(f"❌ Table WebSocket error: {e}")
        manager.disconnect(websocket, branch_code)


@router.websocket("/dashboard")
async def dashboard_websocket(
    websocket: WebSocket,
    branch: str = Query(default="hirama")
):
    """WebSocket endpoint for dashboard real-time updates"""
    await manager.connect(websocket, branch)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                msg_type = message.get("type")

                if msg_type == "subscribe":
                    channel = message.get("channel")
                    if channel:
                        manager.subscribe(websocket, channel)
                        await manager.send_personal(websocket, {
                            "type": "subscribed",
                            "channel": channel
                        })

                elif msg_type == "unsubscribe":
                    channel = message.get("channel")
                    if channel:
                        manager.unsubscribe(websocket, channel)
                        await manager.send_personal(websocket, {
                            "type": "unsubscribed",
                            "channel": channel
                        })

                elif msg_type == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})

                else:
                    # Handle other message types
                    print(f"📨 Received: {msg_type}")

            except json.JSONDecodeError:
                print(f"❌ Invalid JSON received")

    except WebSocketDisconnect:
        manager.disconnect(websocket, branch)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket, branch)


# Helper functions to broadcast events from other parts of the app

async def broadcast_order_event(branch_code: str, event_type: str, data: dict):
    """Broadcast order-related events to table-order clients"""
    await manager.broadcast_to_branch(branch_code, {
        "type": event_type,
        "data": data,
        "channel": "orders"
    }, channel="orders")


async def broadcast_booking_created(branch_code: str, booking: dict):
    """Broadcast new booking event"""
    await manager.broadcast_to_branch(branch_code, {
        "type": "booking:created",
        "data": booking,
        "channel": "bookings"
    }, channel="bookings")


async def broadcast_booking_updated(branch_code: str, booking: dict):
    """Broadcast booking update event"""
    await manager.broadcast_to_branch(branch_code, {
        "type": "booking:updated",
        "data": booking,
        "channel": "bookings"
    }, channel="bookings")


async def broadcast_table_status(branch_code: str, table: dict):
    """Broadcast table status change"""
    await manager.broadcast_to_branch(branch_code, {
        "type": "table:status",
        "data": table,
        "channel": "tables"
    }, channel="tables")


async def broadcast_notification(branch_code: str, title: str, message: str):
    """Broadcast notification"""
    await manager.broadcast_to_branch(branch_code, {
        "type": "notification",
        "data": {
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    })

```

## File ./backend\app\routers\__init__.py:
```python
﻿"""
API Routers
"""
from app.routers.bookings import router as bookings_router
from app.routers.customers import router as customers_router
from app.routers.branches import router as branches_router
from app.routers.chat import router as chat_router

__all__ = ["bookings_router", "customers_router", "branches_router", "chat_router"]


```

## File ./backend\app\schemas\booking.py:
```python
﻿"""
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


```

## File ./backend\app\schemas\branch.py:
```python
﻿"""
Branch Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class BranchCreate(BaseModel):
    """Schema for creating a branch"""
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    subdomain: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    theme_primary_color: str = "#d4af37"
    theme_bg_color: str = "#1a1a1a"
    opening_time: Optional[str] = "17:00"
    closing_time: Optional[str] = "23:00"
    closed_days: List[int] = [2]  # Tuesday
    max_capacity: int = 30


class BranchResponse(BaseModel):
    """Schema for branch response"""
    id: str
    code: str
    name: str
    subdomain: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    theme_primary_color: str
    theme_bg_color: str
    opening_time: Optional[str]
    closing_time: Optional[str]
    closed_days: List[int]
    max_capacity: int
    features: Dict[str, Any]
    is_active: bool

    model_config = {"from_attributes": True}


```

## File ./backend\app\schemas\chat.py:
```python
﻿"""
Chat Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    """Request for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=1000)
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = None
    branch_code: str = "hirama"


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    response: str
    customer_recognized: bool = False
    customer_name: Optional[str] = None
    insights_extracted: int = 0  # Number of new insights saved
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class InsightExtraction(BaseModel):
    """Extracted customer insight from chat"""
    preference: str
    category: str  # meat, cooking, allergy, occasion
    confidence: float = 0.8


```

## File ./backend\app\schemas\customer.py:
```python
﻿"""
Customer Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class PreferenceCreate(BaseModel):
    """Schema for creating customer preference"""
    preference: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = None  # meat, cooking, allergy, occasion
    note: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "manual"  # chat, booking, manual


class PreferenceResponse(BaseModel):
    """Schema for preference response"""
    id: str
    preference: str
    category: Optional[str]
    note: Optional[str]
    confidence: float
    source: str

    model_config = {"from_attributes": True}


class CustomerCreate(BaseModel):
    """Schema for creating/identifying customer"""
    phone: str = Field(..., min_length=10, max_length=20)
    name: Optional[str] = None
    email: Optional[str] = None


class CustomerResponse(BaseModel):
    """Schema for customer response"""
    id: str
    phone: str
    name: Optional[str]
    email: Optional[str]
    visit_count: int
    is_vip: bool
    preferences: List[PreferenceResponse] = []

    model_config = {"from_attributes": True}


```

## File ./backend\app\schemas\menu.py:
```python
﻿"""
Menu Schemas - Pydantic models for menu items
"""
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class MenuItemBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    is_available: bool = True
    is_popular: bool = False
    is_spicy: bool = False
    is_vegetarian: bool = False
    allergens: Optional[str] = None
    prep_time_minutes: int = 5


class MenuItemCreate(MenuItemBase):
    branch_code: str


class MenuItemResponse(MenuItemBase):
    id: str
    branch_code: str
    display_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class MenuCategoryResponse(BaseModel):
    category: str
    category_label: str
    icon: str
    items: List[MenuItemResponse]


class MenuResponse(BaseModel):
    branch_code: str
    categories: List[MenuCategoryResponse]
    updated_at: datetime


```

## File ./backend\app\schemas\order.py:
```python
﻿"""
Order Schemas - Pydantic models for orders
"""
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


# ============ Order Item Schemas ============

class OrderItemCreate(BaseModel):
    menu_item_id: str
    quantity: int = 1
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: str
    menu_item_id: str
    item_name: str
    item_price: Decimal
    quantity: int
    notes: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItemKitchen(BaseModel):
    """Simplified item for kitchen display"""
    id: str
    item_name: str
    quantity: int
    notes: Optional[str] = None
    status: str


# ============ Order Schemas ============

class OrderCreate(BaseModel):
    table_id: str
    session_id: str
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: str
    branch_code: str
    table_id: str
    session_id: str
    order_number: int
    status: str
    items: List[OrderItemResponse]
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    served_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderKitchen(BaseModel):
    """Order view for kitchen display (KDS)"""
    id: str
    order_number: int
    table_number: str
    status: str
    items: List[OrderItemKitchen]
    created_at: datetime
    elapsed_minutes: float


class OrderStatusUpdate(BaseModel):
    status: str


# ============ Table Session Schemas ============

class TableSessionCreate(BaseModel):
    table_id: str
    guest_count: int = 1
    booking_id: Optional[str] = None


class TableSessionResponse(BaseModel):
    id: str
    branch_code: str
    table_id: str
    booking_id: Optional[str] = None
    guest_count: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_paid: bool
    total_amount: Decimal

    class Config:
        from_attributes = True


class TableSessionSummary(BaseModel):
    """Summary for POS checkout"""
    session_id: str
    table_number: str
    guest_count: int
    started_at: datetime
    orders: List[OrderResponse]
    subtotal: Decimal
    tax: Decimal
    total: Decimal


# ============ Staff Call ============

class StaffCallRequest(BaseModel):
    table_id: str
    session_id: str
    call_type: str = "assistance"  # assistance, water, bill, etc.
    message: Optional[str] = None


```

## File ./backend\app\schemas\__init__.py:
```python
﻿"""
Pydantic Schemas
"""
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.schemas.customer import CustomerCreate, CustomerResponse, PreferenceCreate
from app.schemas.branch import BranchCreate, BranchResponse

__all__ = [
    "BookingCreate",
    "BookingUpdate",
    "BookingResponse",
    "CustomerCreate",
    "CustomerResponse",
    "PreferenceCreate",
    "BranchCreate",
    "BranchResponse",
]


```

## File ./backend\app\services\chat_service.py:
```python
"""
AI Chat Service - OpenAI Integration
Handles chat conversations with customer context
Extracts customer preferences automatically
"""
from openai import AsyncOpenAI
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json

from app.config import settings
from app.models.customer import GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference


# System prompt for the restaurant assistant
SYSTEM_PROMPT = """あなたは「焼肉レストラン」のAIアシスタントです。丁寧で温かい接客を心がけてください。

## 店舗情報
- 店名: 焼肉レストラン（平間本店）
- 住所: 〒211-0013 神奈川県川崎市中原区上平間
- 電話: 044-789-8413
- 営業時間: 17:00 - 23:00（L.O. 22:30）
- 定休日: 火曜日
- 席数: 30席（個室あり）

## メニュー（税込価格）
【極上和牛】
- 特選黒毛和牛カルビ ¥2,800
- 和牛上ハラミ ¥1,800
- 特選盛り合わせ ¥4,500〜

【タン・赤身】
- 厚切り上タン塩 ¥2,200
- 上タン塩 ¥1,600
- 牛ハレ ¥2,400

【ホルモン】
- 上ミノ ¥980
- シマチョウ ¥880
- ハツ ¥780
- テッチャン ¥880

【その他】
- ビビンバ ¥980
- 冷麺 ¥1,100
- 各種サラダ ¥580〜

## ルール
1. 日本語で丁寧に応答
2. 絵文字を適度に使用（🥩🖐🔥✨など）
3. 予約は電話またはウェブサイトを案内
4. レバ刺しなど生肉の提供は法律上できないことを説明
5. アレルギー対応可能だが、詳細は来店時に確認を推奨
6. 記念日・接待の特別対応可能
7. 回答は簡潔に（3-4文以内）
8. 不明な質問は電話での問い合わせを案内

## 顧客情報
{customer_context}
"""


class ChatService:
    """AI-powered chat service with customer context"""

    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_customer_context(
        self,
        db: AsyncSession,
        phone: Optional[str] = None,
        name: Optional[str] = None,
        branch_code: str = "hirama"
    ) -> str:
        """Build customer context string for the AI"""
        if not phone and not name:
            return "新規のお客様です。"

        # Try to find customer by phone first
        query = select(GlobalCustomer)
        if phone:
            query = query.where(GlobalCustomer.phone == phone)
        elif name:
            query = query.where(GlobalCustomer.name.ilike(f"%{name}%"))

        result = await db.execute(query)
        global_customer = result.scalar_one_or_none()

        if not global_customer:
            if name:
                return f"お名前: {name}様（新規のお客様）"
            return "新規のお客様です。"

        # Get branch-specific data
        result = await db.execute(
            select(BranchCustomer)
            .options(selectinload(BranchCustomer.preferences))
            .where(
                BranchCustomer.global_customer_id == global_customer.id,
                BranchCustomer.branch_code == branch_code
            )
        )
        branch_customer = result.scalar_one_or_none()

        context_parts = [f"お名前: {global_customer.name}様"]

        if branch_customer:
            context_parts.append(f"来店回数: {branch_customer.visit_count}回")

            if branch_customer.is_vip:
                context_parts.append("VIPのお客様です 🌟")

            if branch_customer.preferences:
                prefs = [p.preference for p in branch_customer.preferences]
                context_parts.append(f"お好みの部位: {', '.join(prefs)}")

                # Add notes
                notes = [p.note for p in branch_customer.preferences if p.note]
                if notes:
                    context_parts.append(f"備考: {'; '.join(notes)}")

        return "\n".join(context_parts)

    async def chat(
        self,
        message: str,
        db: AsyncSession,
        phone: Optional[str] = None,
        customer_name: Optional[str] = None,
        branch_code: str = "hirama",
        conversation_history: Optional[List[dict]] = None
    ) -> str:
        """
        Process a chat message and return AI response.
        Falls back to keyword matching if OpenAI is not configured.
        """
        # Get customer context
        customer_context = await self.get_customer_context(
            db, phone, customer_name, branch_code
        )

        # If no OpenAI key, use fallback
        if not self.client:
            return self._fallback_response(message, customer_name)

        # Build messages for OpenAI
        system_message = SYSTEM_PROMPT.format(customer_context=customer_context)

        messages = [{"role": "system", "content": system_message}]

        # Add conversation history (last 10 messages)
        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Add current message
        messages.append({"role": "user", "content": message})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._fallback_response(message, customer_name)

    def _fallback_response(self, message: str, customer_name: Optional[str] = None) -> str:
        """Keyword-based fallback when OpenAI is unavailable"""
        lower = message.lower()

        responses = {
            'おすすめ': '本日のおすすめは：\n\n🥇 特選黒毛和牛カルビ ¥2,800\n🥈 厚切り上タン塩 ¥2,200\n🥉 和牛上ハラミ ¥1,800\n\nどれも新鮮で絶品です！',
            'レバ刺し': '申し訳ございませんが、現在レバ刺しは法律により提供できません。代わりに低温調理のレバーはいかがですか？',
            'アレルギー': 'アレルギー対応可能です。ご来店時にスタッフにお申し付けください。詳細はお電話（044-789-8413）でもご相談いただけます。',
            '記念日': '記念日のご予定ですね！🎉 特別デザートプレート・お花のご用意・個室のご予約など承ります。',
            '予約': 'ご予約はこのページの「ご予約」セクションから、またはお電話（044-789-8413）で承っております。',
            '営業': '営業時間: 17:00 - 23:00（L.O. 22:30）\n定休日: 火曜日\n\n皆様のご来店をお待ちしております！',
            'ホルモン': 'ホルモンメニュー：\n・上ミノ ¥980\n・シマチョウ ¥880\n・ハツ ¥780\n\n新鮮なホルモンをご用意しております！',
            'タン': '厚切り上タン塩（¥2,200）が大人気です！🔥 歯ごたえと肉汁が溢れる逸品です。',
            'カルビ': '特選黒毛和牛カルビ（¥2,800）は口の中でとろける美味しさです！✨',
            '個室': '個室は4名様〜ご利用いただけます。接待やご家族でのお食事に最適です。ご予約時にお申し付けください。',
            'コース': 'コース料理は¥5,000〜ご用意しております。詳細はお電話にてお問い合わせください。',
        }

        for keyword, response in responses.items():
            if keyword in lower:
                return response

        # Default response
        greeting = f"{customer_name}様、" if customer_name else ""
        return f'{greeting}ありがとうございます！ご質問を承りました。\n\n詳しくはお電話（044-789-8413）でお問い合わせください。'


# Singleton instance
chat_service = ChatService()


# ============================================
# INSIGHT EXTRACTION PROMPT
# ============================================
EXTRACTION_PROMPT = """会話からお客様の好みや重要な情報を抽出してください。

抽出するカテゴリ:
- meat: お肉の好み（例: タン好き、ハラミが好き、厚切り派）
- cooking: 調理法の好み（例: レア派、よく焼き、塩派、タレ派）
- allergy: アレルギーや食事制限（例: 甲殻類アレルギー、ベジタリアン）
- occasion: 利用シーン（例: 記念日、接待、家族連れ）
- other: その他の重要情報（例: 個室希望、子供連れ）

会話内容:
{conversation}

JSONで回答してください。該当がなければ空配列を返してください:
{
  "insights": [
    {"preference": "抽出した好み", "category": "カテゴリ", "confidence": 0.0-1.0}
  ]
}
"""


class InsightExtractor:
    """Extract customer preferences from chat conversations"""

    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def extract_insights(
        self,
        messages: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Extract customer insights from conversation.
        Returns list of {preference, category, confidence}
        """
        if not self.client or not messages:
            return self._fallback_extract(messages)

        # Build conversation text
        conversation = "\n".join([
            f"{'お客様' if m.get('role') == 'user' else 'スタッフ'}: {m.get('content', '')}"
            for m in messages[-10:]
        ])

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "あなたは顧客分析AIです。会話から顧客の好みを抽出してJSON形式で返してください。"},
                    {"role": "user", "content": EXTRACTION_PROMPT.format(conversation=conversation)}
                ],
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            # Clean up potential whitespace issues
            content = content.strip()
            result = json.loads(content)
            return result.get("insights", [])

        except Exception as e:
            print(f"Insight extraction error: {e}")
            return self._fallback_extract(messages)

    def _fallback_extract(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Keyword-based fallback extraction"""
        insights = []

        # Keywords to detect
        keywords = {
            # Meat preferences
            'タン': ('タン好き', 'meat'),
            'ハラミ': ('ハラミ好き', 'meat'),
            'カルビ': ('カルビ好き', 'meat'),
            'ホルモン': ('ホルモン好き', 'meat'),
            'ミノ': ('ミノ好き', 'meat'),
            '赤身': ('赤身派', 'meat'),
            '厚切り': ('厚切り派', 'meat'),
            # Cooking preferences
            'レア': ('レア派', 'cooking'),
            'ウェルダン': ('よく焼き派', 'cooking'),
            '塩': ('塩派', 'cooking'),
            'タレ': ('タレ派', 'cooking'),
            '辛い': ('辛いもの好き', 'cooking'),
            # Allergies
            'アレルギー': ('アレルギーあり要確認', 'allergy'),
            'ベジタリアン': ('ベジタリアン', 'allergy'),
            # Occasions
            '記念日': ('記念日利用', 'occasion'),
            '誕生日': ('誕生日利用', 'occasion'),
            '接待': ('接待利用', 'occasion'),
            'デート': ('デート利用', 'occasion'),
            '家族': ('家族連れ', 'occasion'),
            # Other
            '個室': ('個室希望', 'other'),
            '子供': ('子供連れ', 'other'),
        }

        # Check all user messages
        for msg in messages:
            if msg.get('role') != 'user':
                continue
            content = msg.get('content', '')

            for keyword, (preference, category) in keywords.items():
                if keyword in content:
                    # Avoid duplicates
                    if not any(i['preference'] == preference for i in insights):
                        insights.append({
                            'preference': preference,
                            'category': category,
                            'confidence': 0.7
                        })

        return insights

    async def save_insights(
        self,
        db: AsyncSession,
        branch_customer_id: str,
        insights: List[Dict[str, Any]],
    ) -> int:
        """Save extracted insights to database. Returns count of new insights."""
        if not insights or not branch_customer_id:
            return 0

        # Get existing preferences
        result = await db.execute(
            select(CustomerPreference.preference)
            .where(CustomerPreference.branch_customer_id == branch_customer_id)
        )
        existing = {row[0] for row in result.fetchall()}

        new_count = 0
        for insight in insights:
            pref_text = insight.get('preference', '')
            if not pref_text or pref_text in existing:
                continue

            new_pref = CustomerPreference(
                branch_customer_id=branch_customer_id,
                preference=pref_text,
                category=insight.get('category', 'other'),
                confidence=insight.get('confidence', 0.8),
                source='chat',
                note='AI extracted from chat'
            )
            db.add(new_pref)
            existing.add(pref_text)
            new_count += 1

        if new_count > 0:
            await db.commit()

        return new_count


# Singleton instance
insight_extractor = InsightExtractor()

```

## File ./backend\app\services\notification_service.py:
```python
﻿"""
Notification Service - Real-time notifications using SSE
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class NotificationType(str, Enum):
    NEW_BOOKING = "new_booking"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_CONFIRMED = "booking_confirmed"
    VIP_ARRIVED = "vip_arrived"
    CHAT_MESSAGE = "chat_message"


@dataclass
class Notification:
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_sse(self) -> str:
        """Format as SSE event"""
        payload = {
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "data": self.data or {},
            "timestamp": self.timestamp,
        }
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


class NotificationManager:
    """
    Manages SSE connections and broadcasts notifications to connected clients.
    Each branch can have multiple connected staff members.
    """

    def __init__(self):
        # branch_code -> set of asyncio.Queue for each connected client
        self._clients: Dict[str, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()

    @property
    def shutdown_event(self) -> asyncio.Event:
        """Get the shutdown event for SSE connections to check"""
        return self._shutdown_event

    async def shutdown(self):
        """Signal all SSE connections to close gracefully"""
        print("📡 Shutting down SSE connections...")
        self._shutdown_event.set()

        # Send shutdown signal to all queues
        async with self._lock:
            for branch_code, clients in self._clients.items():
                for queue in clients:
                    try:
                        # Put None to signal shutdown
                        await queue.put(None)
                    except Exception:
                        pass
            # Clear all clients
            self._clients.clear()

        print("📡 All SSE connections closed")

    async def connect(self, branch_code: str) -> asyncio.Queue:
        """Register a new SSE client connection"""
        queue = asyncio.Queue()

        async with self._lock:
            if branch_code not in self._clients:
                self._clients[branch_code] = set()
            self._clients[branch_code].add(queue)

        print(f"📡 SSE client connected for branch: {branch_code} (total: {len(self._clients[branch_code])})")
        return queue

    async def disconnect(self, branch_code: str, queue: asyncio.Queue):
        """Remove a client connection"""
        async with self._lock:
            if branch_code in self._clients:
                self._clients[branch_code].discard(queue)
                if not self._clients[branch_code]:
                    del self._clients[branch_code]

        print(f"📡 SSE client disconnected from branch: {branch_code}")

    async def broadcast(self, branch_code: str, notification: Notification):
        """Send notification to all connected clients for a branch"""
        async with self._lock:
            clients = self._clients.get(branch_code, set()).copy()

        if not clients:
            print(f"📡 No clients connected for branch: {branch_code}")
            return

        print(f"📡 Broadcasting to {len(clients)} clients: {notification.title}")

        for queue in clients:
            try:
                await queue.put(notification)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")

    async def broadcast_all(self, notification: Notification):
        """Broadcast to all connected clients across all branches"""
        async with self._lock:
            all_clients = []
            for clients in self._clients.values():
                all_clients.extend(clients)

        for queue in all_clients:
            try:
                await queue.put(notification)
            except Exception as e:
                print(f"Error broadcasting: {e}")

    def get_client_count(self, branch_code: str = None) -> int:
        """Get number of connected clients"""
        if branch_code:
            return len(self._clients.get(branch_code, set()))
        return sum(len(clients) for clients in self._clients.values())


# Singleton instance
notification_manager = NotificationManager()


# ============================================
# HELPER FUNCTIONS
# ============================================

async def notify_new_booking(
    branch_code: str,
    guest_name: str,
    booking_date: str,
    booking_time: str,
    guests: int,
    booking_id: str = None,
    table_number: str = None,
):
    """Send notification for new booking"""
    message = f"{guest_name}様 {guests}名様 - {booking_date} {booking_time}"
    if table_number:
        message += f" ({table_number})"

    notification = Notification(
        type=NotificationType.NEW_BOOKING,
        title="🔔 新規予約",
        message=message,
        data={
            "booking_id": booking_id,
            "guest_name": guest_name,
            "date": booking_date,
            "time": booking_time,
            "guests": guests,
            "table_number": table_number,
        }
    )
    await notification_manager.broadcast(branch_code, notification)


async def notify_booking_cancelled(
    branch_code: str,
    guest_name: str,
    booking_date: str,
    booking_time: str,
    booking_id: str = None,
):
    """Send notification for cancelled booking"""
    notification = Notification(
        type=NotificationType.BOOKING_CANCELLED,
        title="❌ 予約キャンセル",
        message=f"{guest_name}様 - {booking_date} {booking_time}",
        data={
            "booking_id": booking_id,
            "guest_name": guest_name,
            "date": booking_date,
            "time": booking_time,
        }
    )
    await notification_manager.broadcast(branch_code, notification)


async def notify_booking_confirmed(
    branch_code: str,
    guest_name: str,
    booking_date: str,
    booking_time: str,
    booking_id: str = None,
):
    """Send notification for confirmed booking"""
    notification = Notification(
        type=NotificationType.BOOKING_CONFIRMED,
        title="✅ 予約確認完了",
        message=f"{guest_name}様 - {booking_date} {booking_time}",
        data={
            "booking_id": booking_id,
            "guest_name": guest_name,
            "date": booking_date,
            "time": booking_time,
        }
    )
    await notification_manager.broadcast(branch_code, notification)


async def notify_vip_arrived(
    branch_code: str,
    customer_name: str,
    preferences: List[str] = None,
):
    """Send notification when VIP customer arrives"""
    notification = Notification(
        type=NotificationType.VIP_ARRIVED,
        title="⭐ VIP来店",
        message=f"{customer_name}様がご来店です",
        data={
            "customer_name": customer_name,
            "preferences": preferences or [],
        }
    )
    await notification_manager.broadcast(branch_code, notification)

```

## File ./backend\app\services\table_optimization.py:
```python
﻿"""
AI Table Optimization Service
Tối ưu hóa việc xếp bàn và quản lý capacity nhà hàng
"""
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import selectinload

from app.models.table import Table, TableAssignment, TableStatus
from app.models.booking import Booking, BookingStatus


class OptimizationStrategy(str, Enum):
    """Chiến lược tối ưu hóa"""
    MAXIMIZE_CAPACITY = "maximize_capacity"      # Tối đa số khách
    MINIMIZE_WASTE = "minimize_waste"            # Giảm lãng phí ghế
    VIP_PRIORITY = "vip_priority"                # Ưu tiên VIP
    QUICK_TURNOVER = "quick_turnover"            # Tối đa vòng quay bàn


@dataclass
class TableSlot:
    """Thông tin 1 slot thời gian của bàn"""
    table_id: str
    table_number: str
    max_capacity: int
    time_slot: str
    is_available: bool
    booking_id: Optional[str] = None
    guests: int = 0


@dataclass
class TimeSlotSummary:
    """Tổng hợp tình trạng 1 khung giờ"""
    time_slot: str
    total_tables: int
    available_tables: int
    occupied_tables: int
    total_capacity: int
    used_capacity: int
    available_capacity: int
    utilization_rate: float  # 0-100%
    tables: List[TableSlot] = field(default_factory=list)


@dataclass
class TableSuggestion:
    """Đề xuất bàn cho booking"""
    table_id: str
    table_number: str
    capacity: int
    score: float  # 0-100, điểm phù hợp
    reason: str
    waste: int  # Số ghế thừa


@dataclass
class OptimizationInsight:
    """Insight từ AI về tình trạng nhà hàng"""
    type: str  # "warning", "suggestion", "opportunity"
    title: str
    message: str
    priority: int  # 1-5
    action: Optional[str] = None
    data: Optional[Dict] = None


class TableOptimizationService:
    """
    AI Service để tối ưu hóa việc xếp bàn

    Features:
    1. Đề xuất bàn phù hợp cho số khách
    2. Cảnh báo khi sắp full
    3. Gợi ý thời gian thay thế
    4. Phân tích utilization
    """

    # Thời gian trung bình 1 bữa ăn (phút)
    AVERAGE_DINING_TIME = 90

    # Thời gian buffer giữa các booking (phút)
    TURNOVER_BUFFER = 30

    # Slot duration (phút)
    SLOT_DURATION = 30

    def __init__(self, db: AsyncSession, branch_code: str):
        self.db = db
        self.branch_code = branch_code

    # ==========================================
    # CORE: Tìm bàn phù hợp
    # ==========================================

    async def find_best_tables(
        self,
        guests: int,
        booking_date: date,
        time_slot: str,
        strategy: OptimizationStrategy = OptimizationStrategy.MINIMIZE_WASTE
    ) -> List[TableSuggestion]:
        """
        Tìm bàn phù hợp nhất cho số khách

        Strategy:
        - MINIMIZE_WASTE: Chọn bàn có capacity gần nhất với số khách
        - MAXIMIZE_CAPACITY: Ưu tiên bàn lớn để có chỗ nếu khách thêm
        - VIP_PRIORITY: Ưu tiên bàn VIP/private
        """
        # Lấy tất cả bàn available cho slot này
        available_tables = await self._get_available_tables(booking_date, time_slot)

        if not available_tables:
            return []

        suggestions = []

        for table in available_tables:
            # Bỏ qua bàn quá nhỏ
            if table.max_capacity < guests:
                continue

            # Tính điểm dựa trên strategy
            score, reason = self._calculate_table_score(
                table, guests, strategy
            )

            waste = table.max_capacity - guests

            suggestions.append(TableSuggestion(
                table_id=table.id,
                table_number=table.table_number,
                capacity=table.max_capacity,
                score=score,
                reason=reason,
                waste=waste
            ))

        # Sắp xếp theo score giảm dần
        suggestions.sort(key=lambda x: x.score, reverse=True)

        return suggestions[:5]  # Top 5 đề xuất

    def _calculate_table_score(
        self,
        table: Table,
        guests: int,
        strategy: OptimizationStrategy
    ) -> Tuple[float, str]:
        """Tính điểm phù hợp của bàn"""
        base_score = 100.0
        reason_parts = []

        waste = table.max_capacity - guests

        if strategy == OptimizationStrategy.MINIMIZE_WASTE:
            # Giảm điểm theo số ghế thừa
            waste_penalty = waste * 10
            base_score -= waste_penalty

            if waste == 0:
                reason_parts.append("完璧にマッチ")
            elif waste <= 2:
                reason_parts.append(f"余り{waste}席")
            else:
                reason_parts.append(f"余り{waste}席(大きめ)")

        elif strategy == OptimizationStrategy.MAXIMIZE_CAPACITY:
            # Ưu tiên bàn lớn hơn
            capacity_bonus = table.max_capacity * 5
            base_score += capacity_bonus
            reason_parts.append(f"最大{table.max_capacity}名まで対応")

        # Bonus cho các features
        if table.table_type == "private":
            base_score += 15
            reason_parts.append("個室")

        if table.has_window:
            base_score += 5
            reason_parts.append("窓際")

        # Priority bonus
        base_score += table.priority * 2

        reason = "・".join(reason_parts) if reason_parts else "標準席"

        return max(0, min(100, base_score)), reason

    async def _get_available_tables(
        self,
        booking_date: date,
        time_slot: str
    ) -> List[Table]:
        """Lấy danh sách bàn còn trống cho slot"""
        # Lấy tất cả bàn của branch
        tables_query = select(Table).where(
            and_(
                Table.branch_code == self.branch_code,
                Table.is_active == True
            )
        )
        tables_result = await self.db.execute(tables_query)
        all_tables = tables_result.scalars().all()

        # Lấy các bàn đã được assign cho slot này
        booked_tables_query = select(TableAssignment.table_id).join(
            Booking
        ).where(
            and_(
                Booking.branch_code == self.branch_code,
                Booking.date == booking_date,
                Booking.time == time_slot,
                Booking.status.in_(["pending", "confirmed"])
            )
        )
        booked_result = await self.db.execute(booked_tables_query)
        booked_table_ids = {r[0] for r in booked_result.fetchall()}

        # Lọc ra bàn còn trống
        available = [t for t in all_tables if t.id not in booked_table_ids]

        return available

    # ==========================================
    # AVAILABILITY CHECK
    # ==========================================

    async def check_availability(
        self,
        guests: int,
        booking_date: date,
        time_slot: str
    ) -> Dict[str, Any]:
        """
        Kiểm tra xem có thể đặt bàn không

        Returns:
            {
                "available": True/False,
                "tables": [TableSuggestion],
                "alternatives": [{"time": "18:30", "tables": [...]}],
                "message": "..."
            }
        """
        suggestions = await self.find_best_tables(guests, booking_date, time_slot)

        if suggestions:
            return {
                "available": True,
                "tables": suggestions,
                "alternatives": [],
                "message": f"{len(suggestions)}席ご案内可能です"
            }

        # Không có bàn -> tìm alternatives
        alternatives = await self._find_alternative_slots(guests, booking_date, time_slot)

        return {
            "available": False,
            "tables": [],
            "alternatives": alternatives,
            "message": "申し訳ございません、ご希望の時間は満席です。" +
                      (f"代わりに{len(alternatives)}つの時間帯がございます。" if alternatives else "")
        }

    async def _find_alternative_slots(
        self,
        guests: int,
        booking_date: date,
        requested_slot: str,
        range_hours: int = 2
    ) -> List[Dict]:
        """Tìm các slot thay thế trong vòng ±range_hours"""
        alternatives = []

        # Parse requested time
        req_hour, req_min = map(int, requested_slot.split(":"))
        req_minutes = req_hour * 60 + req_min

        # Generate slots to check
        all_slots = [
            f"{h:02d}:{m:02d}"
            for h in range(17, 23)
            for m in [0, 30]
            if not (h == 22 and m == 30)
        ]

        for slot in all_slots:
            if slot == requested_slot:
                continue

            # Check if within range
            slot_hour, slot_min = map(int, slot.split(":"))
            slot_minutes = slot_hour * 60 + slot_min

            if abs(slot_minutes - req_minutes) > range_hours * 60:
                continue

            # Check availability
            tables = await self.find_best_tables(guests, booking_date, slot)

            if tables:
                alternatives.append({
                    "time": slot,
                    "tables": tables[:2],  # Top 2
                    "diff_minutes": slot_minutes - req_minutes
                })

        # Sort by closest to requested time
        alternatives.sort(key=lambda x: abs(x["diff_minutes"]))

        return alternatives[:5]  # Top 5 alternatives

    # ==========================================
    # ANALYTICS & INSIGHTS
    # ==========================================

    async def get_time_slot_summary(
        self,
        target_date: date
    ) -> List[TimeSlotSummary]:
        """Tổng hợp tình trạng tất cả các slot trong ngày"""
        # Lấy tất cả bàn
        tables_query = select(Table).where(
            and_(
                Table.branch_code == self.branch_code,
                Table.is_active == True
            )
        )
        tables_result = await self.db.execute(tables_query)
        all_tables = list(tables_result.scalars().all())

        total_capacity = sum(t.max_capacity for t in all_tables)

        # Lấy tất cả booking trong ngày
        bookings_query = select(Booking).where(
            and_(
                Booking.branch_code == self.branch_code,
                Booking.date == target_date,
                Booking.status.in_(["pending", "confirmed"])
            )
        )
        bookings_result = await self.db.execute(bookings_query)
        bookings = list(bookings_result.scalars().all())

        # Group bookings by time
        bookings_by_time: Dict[str, List[Booking]] = {}
        for b in bookings:
            if b.time not in bookings_by_time:
                bookings_by_time[b.time] = []
            bookings_by_time[b.time].append(b)

        # Generate all slots
        all_slots = [
            f"{h:02d}:{m:02d}"
            for h in range(17, 23)
            for m in [0, 30]
            if not (h == 22 and m == 30)
        ]

        summaries = []

        for slot in all_slots:
            slot_bookings = bookings_by_time.get(slot, [])
            used_capacity = sum(b.guests for b in slot_bookings)
            available_capacity = total_capacity - used_capacity

            occupied = len(slot_bookings)
            available = len(all_tables) - occupied

            utilization = (used_capacity / total_capacity * 100) if total_capacity > 0 else 0

            summaries.append(TimeSlotSummary(
                time_slot=slot,
                total_tables=len(all_tables),
                available_tables=available,
                occupied_tables=occupied,
                total_capacity=total_capacity,
                used_capacity=used_capacity,
                available_capacity=available_capacity,
                utilization_rate=round(utilization, 1),
                tables=[]  # Populate if needed
            ))

        return summaries

    async def generate_insights(
        self,
        target_date: date
    ) -> List[OptimizationInsight]:
        """
        Tạo insights và suggestions cho staff

        Examples:
        - "20:00 sắp full (7/8 bàn), cân nhắc từ chối booking mới"
        - "18:00 còn nhiều bàn 6 ghế, khách 2 người nên chuyển sang 4 ghế"
        - "Hôm nay có 3 VIP, đã reserve phòng riêng"
        """
        insights = []

        # Get slot summaries
        summaries = await self.get_time_slot_summary(target_date)

        for summary in summaries:
            # Warning: Sắp full
            if summary.utilization_rate >= 80:
                insights.append(OptimizationInsight(
                    type="warning",
                    title=f"⚠️ {summary.time_slot} 混雑注意",
                    message=f"利用率{summary.utilization_rate}% - 残り{summary.available_tables}席",
                    priority=4 if summary.utilization_rate >= 90 else 3,
                    action="新規予約を控えるか、代替時間をご案内ください",
                    data={
                        "time_slot": summary.time_slot,
                        "utilization": summary.utilization_rate,
                        "available": summary.available_tables
                    }
                ))

            # Opportunity: Slot trống
            elif summary.utilization_rate < 30 and summary.time_slot >= "18:00":
                insights.append(OptimizationInsight(
                    type="opportunity",
                    title=f"📈 {summary.time_slot} 空き多め",
                    message=f"利用率{summary.utilization_rate}% - {summary.available_tables}席空き",
                    priority=2,
                    action="プロモーションや予約転換の機会",
                    data={
                        "time_slot": summary.time_slot,
                        "available": summary.available_tables
                    }
                ))

        # Check for table waste (big table for small group)
        waste_insights = await self._check_capacity_waste(target_date)
        insights.extend(waste_insights)

        # Sort by priority
        insights.sort(key=lambda x: x.priority, reverse=True)

        return insights

    async def _check_capacity_waste(
        self,
        target_date: date
    ) -> List[OptimizationInsight]:
        """Kiểm tra lãng phí capacity"""
        insights = []

        # Lấy bookings với table assignment
        query = select(Booking, TableAssignment, Table).join(
            TableAssignment, Booking.id == TableAssignment.booking_id
        ).join(
            Table, TableAssignment.table_id == Table.id
        ).where(
            and_(
                Booking.branch_code == self.branch_code,
                Booking.date == target_date,
                Booking.status.in_(["pending", "confirmed"])
            )
        )

        result = await self.db.execute(query)
        rows = result.fetchall()

        waste_cases = []

        for booking, assignment, table in rows:
            waste = table.max_capacity - booking.guests
            if waste >= 3:  # 3+ ghế thừa
                waste_cases.append({
                    "booking": booking,
                    "table": table,
                    "waste": waste
                })

        if waste_cases:
            total_waste = sum(c["waste"] for c in waste_cases)
            insights.append(OptimizationInsight(
                type="suggestion",
                title=f"💡 席効率の改善可能",
                message=f"{len(waste_cases)}件の予約で合計{total_waste}席の余裕あり",
                priority=2,
                action="小さい席への変更を検討",
                data={
                    "waste_cases": [
                        {
                            "time": c["booking"].time,
                            "guests": c["booking"].guests,
                            "table": c["table"].table_number,
                            "capacity": c["table"].max_capacity
                        }
                        for c in waste_cases
                    ]
                }
            ))

        return insights

    # ==========================================
    # TABLE ASSIGNMENT
    # ==========================================

    async def auto_assign_table(
        self,
        booking_id: str,
        guests: int,
        booking_date: date,
        time_slot: str
    ) -> Optional[TableAssignment]:
        """Tự động assign bàn cho booking"""
        suggestions = await self.find_best_tables(guests, booking_date, time_slot)

        if not suggestions:
            return None

        best_table = suggestions[0]

        # Create assignment
        assignment = TableAssignment(
            booking_id=booking_id,
            table_id=best_table.table_id,
            notes=f"Auto-assigned: {best_table.reason}"
        )

        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)

        return assignment

    async def reassign_table(
        self,
        booking_id: str,
        new_table_id: str,
        reason: str = ""
    ) -> Optional[TableAssignment]:
        """Đổi bàn cho booking"""
        # Delete old assignment
        old_query = select(TableAssignment).where(
            TableAssignment.booking_id == booking_id
        )
        old_result = await self.db.execute(old_query)
        old_assignment = old_result.scalar_one_or_none()

        if old_assignment:
            await self.db.delete(old_assignment)

        # Create new assignment
        new_assignment = TableAssignment(
            booking_id=booking_id,
            table_id=new_table_id,
            notes=f"Reassigned: {reason}"
        )

        self.db.add(new_assignment)
        await self.db.commit()
        await self.db.refresh(new_assignment)

        return new_assignment

    # ==========================================
    # GANTT CHART DATA
    # ==========================================

    async def get_gantt_data(
        self,
        target_date: date
    ) -> Dict[str, Any]:
        """
        Get data for Gantt chart visualization

        Returns:
        - tables: List of tables with their bookings
        - time_slots: List of time slots (17:00-22:00)
        - bookings_map: Dict mapping table_id -> list of booking blocks
        """
        # Get all tables
        tables_query = select(Table).where(
            and_(
                Table.branch_code == self.branch_code,
                Table.is_active == True
            )
        ).order_by(Table.zone, Table.table_number)
        tables_result = await self.db.execute(tables_query)
        tables = tables_result.scalars().all()

        # Get all bookings for the date
        bookings_query = (
            select(Booking)
            .options(selectinload(Booking.table_assignments))
            .where(
                and_(
                    Booking.branch_code == self.branch_code,
                    Booking.date == target_date,
                    Booking.status.not_in([BookingStatus.CANCELLED, BookingStatus.NO_SHOW])
                )
            )
            .order_by(Booking.time)
        )
        bookings_result = await self.db.execute(bookings_query)
        bookings = bookings_result.scalars().all()

        # Time slots from 17:00 to 22:30 (30 min intervals)
        time_slots = []
        start_hour = 17
        end_hour = 23
        for hour in range(start_hour, end_hour):
            time_slots.append(f"{hour:02d}:00")
            if hour < end_hour - 1 or (hour == end_hour - 1 and hour == 22):
                time_slots.append(f"{hour:02d}:30")

        # Build bookings map by table
        bookings_by_table: Dict[str, List[Dict]] = {str(t.id): [] for t in tables}

        # Create time_slot to index map for quick lookup
        slot_index_map = {slot: idx for idx, slot in enumerate(time_slots)}

        # Also track unassigned bookings
        unassigned_bookings = []

        for booking in bookings:
            time_str = booking.time[:5] if len(booking.time) >= 5 else booking.time
            slot_index = slot_index_map.get(time_str, -1)

            booking_block = {
                "id": str(booking.id),
                "time": booking.time,
                "time_str": time_str,
                "slot_index": slot_index,  # Pre-calculated slot index
                "guests": booking.guests,
                "customer_name": booking.guest_name or "ゲスト",
                "status": booking.status,
                "duration_slots": 3,  # 90 min = 3 slots of 30 min
                "notes": booking.note or "",
            }

            # Find table assignment
            if booking.table_assignments:
                for assignment in booking.table_assignments:
                    table_id = str(assignment.table_id)
                    if table_id in bookings_by_table:
                        bookings_by_table[table_id].append(booking_block)
            else:
                unassigned_bookings.append(booking_block)

        # Convert tables to response format
        tables_data = []
        for table in tables:
            table_bookings = bookings_by_table.get(str(table.id), [])
            tables_data.append({
                "id": str(table.id),
                "table_number": table.table_number,
                "name": table.name or "",
                "max_capacity": table.max_capacity,
                "table_type": table.table_type,
                "zone": table.zone or "",
                "bookings": table_bookings,
            })

        return {
            "tables": tables_data,
            "time_slots": time_slots,
            "unassigned_bookings": unassigned_bookings,
            "slot_duration": self.SLOT_DURATION,
        }


# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def get_optimization_service(
    db: AsyncSession,
    branch_code: str
) -> TableOptimizationService:
    """Factory function to get optimization service"""
    return TableOptimizationService(db, branch_code)

```

## File ./backend\app\services\__init__.py:
```python
﻿"""
Services module
"""
from app.services.chat_service import chat_service

__all__ = ["chat_service"]


```

## File ./backend\scripts\fix_encoding_all.py:
```python
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

```

## File ./backend\scripts\seed_enhanced_menu.py:
```python
"""
Seed data for enhanced menu system
- Categories, Items, Options, Combos, Promotions
"""
import asyncio
from app.database import async_session_factory
from app.models import (
    ItemCategory, Item, ItemOptionGroup, ItemOption, ItemOptionAssignment,
    Combo, ComboItem, Promotion
)


# ============================================
# CATEGORIES
# ============================================
CATEGORIES = [
    # Top-level categories
    {"id": "cat-meat", "code": "meat", "name": "肉類", "name_en": "Meat", "icon": "🥩", "order": 1},
    {"id": "cat-drinks", "code": "drinks", "name": "飲み物", "name_en": "Drinks", "icon": "🍺", "order": 2},
    {"id": "cat-salad", "code": "salad", "name": "サラダ", "name_en": "Salad", "icon": "🥗", "order": 3},
    {"id": "cat-rice", "code": "rice", "name": "ご飯・麺", "name_en": "Rice & Noodles", "icon": "🍚", "order": 4},
    {"id": "cat-side", "code": "side", "name": "サイドメニュー", "name_en": "Side Menu", "icon": "🍢", "order": 5},
    {"id": "cat-dessert", "code": "dessert", "name": "デザート", "name_en": "Dessert", "icon": "🍨", "order": 6},

    # Sub-categories - Meat
    {"id": "cat-beef", "code": "beef", "name": "牛肉", "name_en": "Beef", "parent": "cat-meat", "order": 1},
    {"id": "cat-wagyu", "code": "wagyu", "name": "和牛", "name_en": "Wagyu", "parent": "cat-meat", "order": 2},
    {"id": "cat-pork", "code": "pork", "name": "豚肉", "name_en": "Pork", "parent": "cat-meat", "order": 3},
    {"id": "cat-chicken", "code": "chicken", "name": "鶏肉", "name_en": "Chicken", "parent": "cat-meat", "order": 4},
    {"id": "cat-offal", "code": "offal", "name": "ホルモン", "name_en": "Offal", "parent": "cat-meat", "order": 5},

    # Sub-categories - Drinks
    {"id": "cat-beer", "code": "beer", "name": "ビール", "name_en": "Beer", "parent": "cat-drinks", "order": 1},
    {"id": "cat-sour", "code": "sour", "name": "サワー", "name_en": "Sour", "parent": "cat-drinks", "order": 2},
    {"id": "cat-shochu", "code": "shochu", "name": "焼酎", "name_en": "Shochu", "parent": "cat-drinks", "order": 3},
    {"id": "cat-sake", "code": "sake", "name": "日本酒", "name_en": "Sake", "parent": "cat-drinks", "order": 4},
    {"id": "cat-soft", "code": "soft", "name": "ソフトドリンク", "name_en": "Soft Drinks", "parent": "cat-drinks", "order": 5},
]

# ============================================
# ITEMS (Menu Items)
# ============================================
ITEMS = [
    # === WAGYU / Premium Beef ===
    {"id": "item-001", "sku": "WAGYU-A5-SIRLOIN", "cat": "cat-wagyu",
     "name": "和牛A5サーロイン", "name_en": "Wagyu A5 Sirloin",
     "desc": "最高級A5ランクの和牛サーロイン。口の中でとろける極上の味わい",
     "price": 4500, "prep": 6, "printer": "grill",
     "popular": True, "has_options": True, "order": 1},

    {"id": "item-002", "sku": "WAGYU-A5-KALBI", "cat": "cat-wagyu",
     "name": "和牛A5カルビ", "name_en": "Wagyu A5 Kalbi",
     "desc": "霜降りが美しい最高級カルビ。濃厚な旨味が特徴",
     "price": 3800, "prep": 5, "printer": "grill",
     "popular": True, "has_options": True, "order": 2},

    {"id": "item-003", "sku": "WAGYU-HARAMI", "cat": "cat-wagyu",
     "name": "和牛上ハラミ", "name_en": "Premium Wagyu Harami",
     "desc": "口の中でほどける柔らかさと濃厚な味わい。当店自慢の一品",
     "price": 2800, "prep": 5, "printer": "grill",
     "popular": True, "has_options": True, "order": 3},

    # === Regular Beef ===
    {"id": "item-010", "sku": "BEEF-KALBI", "cat": "cat-beef",
     "name": "カルビ", "name_en": "Kalbi",
     "desc": "定番の人気メニュー。ジューシーな味わい",
     "price": 1500, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 1},

    {"id": "item-011", "sku": "BEEF-ROSU", "cat": "cat-beef",
     "name": "ロース", "name_en": "Sirloin",
     "desc": "あっさりとした赤身の美味しさ",
     "price": 1400, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 2},

    {"id": "item-012", "sku": "BEEF-TAN", "cat": "cat-beef",
     "name": "厚切り上タン塩", "name_en": "Thick Sliced Beef Tongue",
     "desc": "贅沢な厚切り。歯ごたえと肉汁が溢れます",
     "price": 2200, "prep": 6, "printer": "grill",
     "popular": True, "has_options": True, "order": 3},

    {"id": "item-013", "sku": "BEEF-TAN-THIN", "cat": "cat-beef",
     "name": "牛タン（6枚）", "name_en": "Beef Tongue 6pcs",
     "desc": "薄切り牛タン6枚盛り",
     "price": 1200, "prep": 5, "printer": "grill",
     "popular": False, "has_options": False, "order": 4},

    # === Pork ===
    {"id": "item-020", "sku": "PORK-KALBI", "cat": "cat-pork",
     "name": "豚カルビ", "name_en": "Pork Kalbi",
     "desc": "甘みのある豚バラ肉",
     "price": 900, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 1},

    {"id": "item-021", "sku": "PORK-TORO", "cat": "cat-pork",
     "name": "豚トロ", "name_en": "Pork Jowl",
     "desc": "脂の甘みが絶品。とろける食感",
     "price": 1100, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 2},

    # === Chicken ===
    {"id": "item-030", "sku": "CHICKEN-MOMO", "cat": "cat-chicken",
     "name": "鶏もも", "name_en": "Chicken Thigh",
     "desc": "柔らかくジューシーな鶏もも肉",
     "price": 800, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 1},

    # === Offal ===
    {"id": "item-040", "sku": "OFFAL-MIX", "cat": "cat-offal",
     "name": "ホルモン盛り合わせ", "name_en": "Offal Assortment",
     "desc": "新鮮なホルモンをたっぷり。ミノ・ハチノス・シマチョウ",
     "price": 1400, "prep": 7, "printer": "grill",
     "popular": False, "has_options": False, "order": 1},

    # === BEER ===
    {"id": "item-100", "sku": "BEER-DRAFT-M", "cat": "cat-beer",
     "name": "生ビール（中）", "name_en": "Draft Beer (Medium)",
     "desc": "キンキンに冷えた生ビール",
     "price": 600, "prep": 1, "printer": "drink",
     "popular": True, "has_options": False, "order": 1},

    {"id": "item-101", "sku": "BEER-DRAFT-L", "cat": "cat-beer",
     "name": "生ビール（大）", "name_en": "Draft Beer (Large)",
     "desc": "大ジョッキの生ビール",
     "price": 800, "prep": 1, "printer": "drink",
     "popular": True, "has_options": False, "order": 2},

    {"id": "item-102", "sku": "BEER-BOTTLE", "cat": "cat-beer",
     "name": "瓶ビール", "name_en": "Bottled Beer",
     "desc": "アサヒスーパードライ",
     "price": 650, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 3},

    # === SOUR ===
    {"id": "item-110", "sku": "SOUR-LEMON", "cat": "cat-sour",
     "name": "レモンサワー", "name_en": "Lemon Sour",
     "desc": "自家製レモンサワー。さっぱり飲みやすい",
     "price": 500, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 1},

    {"id": "item-111", "sku": "SOUR-UME", "cat": "cat-sour",
     "name": "梅酒サワー", "name_en": "Plum Wine Sour",
     "desc": "甘酸っぱい梅酒ソーダ割り",
     "price": 550, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 2},

    {"id": "item-112", "sku": "HIGHBALL", "cat": "cat-sour",
     "name": "ハイボール", "name_en": "Highball",
     "desc": "すっきり爽やかなウイスキーソーダ",
     "price": 500, "prep": 1, "printer": "drink",
     "popular": True, "has_options": False, "order": 3},

    # === SHOCHU ===
    {"id": "item-120", "sku": "SHOCHU-IMO", "cat": "cat-shochu",
     "name": "焼酎（芋）", "name_en": "Sweet Potato Shochu",
     "desc": "本格芋焼酎",
     "price": 500, "prep": 1, "printer": "drink",
     "popular": False, "has_options": True, "order": 1},  # has options: ロック/水割り/お湯割り

    {"id": "item-121", "sku": "SHOCHU-MUGI", "cat": "cat-shochu",
     "name": "焼酎（麦）", "name_en": "Barley Shochu",
     "desc": "本格麦焼酎",
     "price": 500, "prep": 1, "printer": "drink",
     "popular": False, "has_options": True, "order": 2},

    # === SOFT DRINKS ===
    {"id": "item-130", "sku": "SOFT-OOLONG", "cat": "cat-soft",
     "name": "ウーロン茶", "name_en": "Oolong Tea",
     "desc": "ソフトドリンク",
     "price": 300, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 1},

    {"id": "item-131", "sku": "SOFT-COLA", "cat": "cat-soft",
     "name": "コーラ", "name_en": "Cola",
     "desc": "コカ・コーラ",
     "price": 300, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 2},

    {"id": "item-132", "sku": "SOFT-ORANGE", "cat": "cat-soft",
     "name": "オレンジジュース", "name_en": "Orange Juice",
     "desc": "100%果汁オレンジジュース",
     "price": 350, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 3},

    # === SALADS ===
    {"id": "item-200", "sku": "SALAD-CHOREGI", "cat": "cat-salad",
     "name": "チョレギサラダ", "name_en": "Korean Salad",
     "desc": "韓国風ピリ辛サラダ。ごま油が香る",
     "price": 600, "prep": 3, "printer": "cold",
     "popular": False, "spicy": True, "vegetarian": True, "order": 1},

    {"id": "item-201", "sku": "SALAD-CAESAR", "cat": "cat-salad",
     "name": "シーザーサラダ", "name_en": "Caesar Salad",
     "desc": "パルメザンチーズたっぷり",
     "price": 700, "prep": 3, "printer": "cold",
     "popular": False, "vegetarian": True, "allergens": "milk", "order": 2},

    {"id": "item-202", "sku": "SALAD-NAMUL", "cat": "cat-salad",
     "name": "ナムル盛り合わせ", "name_en": "Namul Assortment",
     "desc": "3種のナムル（もやし・ほうれん草・大根）",
     "price": 500, "prep": 3, "printer": "cold",
     "popular": False, "vegetarian": True, "order": 3},

    {"id": "item-203", "sku": "SALAD-KIMCHI", "cat": "cat-salad",
     "name": "キムチ盛り合わせ", "name_en": "Kimchi Assortment",
     "desc": "白菜・カクテキ・オイキムチ",
     "price": 550, "prep": 2, "printer": "cold",
     "popular": False, "spicy": True, "vegetarian": True, "order": 4},

    # === RICE & NOODLES ===
    {"id": "item-300", "sku": "RICE-PLAIN", "cat": "cat-rice",
     "name": "ライス", "name_en": "Rice",
     "desc": "国産コシヒカリ使用",
     "price": 200, "prep": 2, "printer": "rice",
     "popular": False, "vegetarian": True, "has_options": True, "order": 1},  # size options

    {"id": "item-301", "sku": "RICE-BIBIMBAP", "cat": "cat-rice",
     "name": "石焼ビビンバ", "name_en": "Stone Pot Bibimbap",
     "desc": "熱々の石鍋で提供。おこげが美味しい",
     "price": 1200, "prep": 8, "printer": "grill",
     "popular": True, "spicy": True, "allergens": "egg", "has_options": True, "order": 2},

    {"id": "item-302", "sku": "RICE-REIMEN", "cat": "cat-rice",
     "name": "冷麺", "name_en": "Cold Noodles",
     "desc": "韓国冷麺。さっぱりとした味わい",
     "price": 900, "prep": 5, "printer": "cold",
     "popular": False, "allergens": "wheat", "order": 3},

    {"id": "item-303", "sku": "RICE-KUPPA", "cat": "cat-rice",
     "name": "カルビクッパ", "name_en": "Kalbi Rice Soup",
     "desc": "カルビ入りの韓国風スープご飯",
     "price": 950, "prep": 6, "printer": "grill",
     "popular": False, "spicy": True, "has_options": True, "order": 4},

    # === DESSERTS ===
    {"id": "item-400", "sku": "DESSERT-ICE", "cat": "cat-dessert",
     "name": "バニラアイス", "name_en": "Vanilla Ice Cream",
     "desc": "濃厚バニラアイス",
     "price": 300, "prep": 2, "printer": "cold",
     "popular": False, "vegetarian": True, "allergens": "milk", "order": 1},

    {"id": "item-401", "sku": "DESSERT-SHERBET", "cat": "cat-dessert",
     "name": "柚子シャーベット", "name_en": "Yuzu Sherbet",
     "desc": "さっぱり柚子シャーベット",
     "price": 350, "prep": 2, "printer": "cold",
     "popular": False, "vegetarian": True, "order": 2},
]

# ============================================
# OPTION GROUPS & OPTIONS
# ============================================
OPTION_GROUPS = [
    # Rice amount
    {"id": "og-rice-amount", "name": "ご飯の量", "name_en": "Rice Amount",
     "type": "single", "min": 0, "max": 1, "order": 1},

    # Doneness (for meat)
    {"id": "og-doneness", "name": "焼き加減", "name_en": "Doneness",
     "type": "single", "min": 0, "max": 1, "order": 2},

    # Toppings
    {"id": "og-toppings", "name": "トッピング", "name_en": "Toppings",
     "type": "multiple", "min": 0, "max": 3, "order": 3},

    # Shochu style
    {"id": "og-shochu-style", "name": "飲み方", "name_en": "Drinking Style",
     "type": "single", "min": 1, "max": 1, "order": 1},  # required

    # Spicy level
    {"id": "og-spicy", "name": "辛さ", "name_en": "Spicy Level",
     "type": "single", "min": 0, "max": 1, "order": 4},
]

OPTIONS = [
    # Rice amount options
    {"id": "opt-rice-small", "group": "og-rice-amount", "name": "少なめ", "name_en": "Less", "price": 0, "order": 1},
    {"id": "opt-rice-normal", "group": "og-rice-amount", "name": "普通", "name_en": "Normal", "price": 0, "default": True, "order": 2},
    {"id": "opt-rice-large", "group": "og-rice-amount", "name": "大盛り", "name_en": "Large", "price": 100, "order": 3},
    {"id": "opt-rice-extra", "group": "og-rice-amount", "name": "特盛り", "name_en": "Extra Large", "price": 200, "order": 4},

    # Doneness options
    {"id": "opt-rare", "group": "og-doneness", "name": "レア", "name_en": "Rare", "price": 0, "order": 1},
    {"id": "opt-medium-rare", "group": "og-doneness", "name": "ミディアムレア", "name_en": "Medium Rare", "price": 0, "order": 2},
    {"id": "opt-medium", "group": "og-doneness", "name": "ミディアム", "name_en": "Medium", "price": 0, "default": True, "order": 3},
    {"id": "opt-well", "group": "og-doneness", "name": "ウェルダン", "name_en": "Well Done", "price": 0, "order": 4},

    # Toppings
    {"id": "opt-egg", "group": "og-toppings", "name": "卵黄", "name_en": "Egg Yolk", "price": 100, "order": 1},
    {"id": "opt-negi", "group": "og-toppings", "name": "ネギ増し", "name_en": "Extra Green Onion", "price": 50, "order": 2},
    {"id": "opt-garlic", "group": "og-toppings", "name": "にんにく", "name_en": "Garlic", "price": 50, "order": 3},
    {"id": "opt-cheese", "group": "og-toppings", "name": "チーズ", "name_en": "Cheese", "price": 150, "order": 4},

    # Shochu style
    {"id": "opt-rock", "group": "og-shochu-style", "name": "ロック", "name_en": "On the Rocks", "price": 0, "default": True, "order": 1},
    {"id": "opt-mizuwari", "group": "og-shochu-style", "name": "水割り", "name_en": "Mizuwari", "price": 0, "order": 2},
    {"id": "opt-oyuwari", "group": "og-shochu-style", "name": "お湯割り", "name_en": "Oyuwari", "price": 0, "order": 3},
    {"id": "opt-straight", "group": "og-shochu-style", "name": "ストレート", "name_en": "Straight", "price": 0, "order": 4},

    # Spicy level
    {"id": "opt-mild", "group": "og-spicy", "name": "控えめ", "name_en": "Mild", "price": 0, "order": 1},
    {"id": "opt-normal-spicy", "group": "og-spicy", "name": "普通", "name_en": "Normal", "price": 0, "default": True, "order": 2},
    {"id": "opt-hot", "group": "og-spicy", "name": "辛め", "name_en": "Hot", "price": 0, "order": 3},
    {"id": "opt-extra-hot", "group": "og-spicy", "name": "激辛", "name_en": "Extra Hot", "price": 100, "order": 4},
]

# Item -> Option Group assignments
ITEM_OPTIONS = [
    # Wagyu items get doneness options
    {"item": "item-001", "group": "og-doneness"},  # A5 Sirloin
    {"item": "item-002", "group": "og-doneness"},  # A5 Kalbi
    {"item": "item-003", "group": "og-doneness"},  # Harami
    {"item": "item-010", "group": "og-doneness"},  # Kalbi
    {"item": "item-011", "group": "og-doneness"},  # Rosu
    {"item": "item-012", "group": "og-doneness"},  # Tan
    {"item": "item-020", "group": "og-doneness"},  # Pork Kalbi
    {"item": "item-021", "group": "og-doneness"},  # Pork Toro
    {"item": "item-030", "group": "og-doneness"},  # Chicken

    # Rice items get rice amount options
    {"item": "item-300", "group": "og-rice-amount"},  # Rice
    {"item": "item-301", "group": "og-rice-amount"},  # Bibimbap
    {"item": "item-303", "group": "og-rice-amount"},  # Kuppa

    # Bibimbap gets toppings
    {"item": "item-301", "group": "og-toppings"},

    # Spicy items get spicy level
    {"item": "item-301", "group": "og-spicy"},  # Bibimbap
    {"item": "item-303", "group": "og-spicy"},  # Kuppa

    # Shochu gets drinking style
    {"item": "item-120", "group": "og-shochu-style"},  # Imo
    {"item": "item-121", "group": "og-shochu-style"},  # Mugi
]

# ============================================
# COMBOS
# ============================================
COMBOS = [
    {
        "id": "combo-001",
        "code": "WAGYU-SALAD-30",
        "name": "和牛A5 + サラダセット",
        "name_en": "Wagyu A5 + Salad Set",
        "desc": "和牛A5（サーロインまたはカルビ）とサラダを一緒にご注文で30%OFF！",
        "discount_type": "percentage",
        "discount_value": 30,
        "featured": True,
        "items": [
            {"item_id": "item-001", "qty": 1},  # A5 Sirloin
            {"category_id": "cat-salad", "qty": 1},  # Any salad
        ]
    },
    {
        "id": "combo-002",
        "code": "YAKINIKU-SET-A",
        "name": "焼肉セットA（2名様）",
        "name_en": "Yakiniku Set A (2 persons)",
        "desc": "カルビ・ロース・ハラミ・サラダ・ライス×2のお得なセット",
        "discount_type": "new_price",
        "discount_value": 4500,  # Instead of individual total
        "featured": True,
        "items": [
            {"item_id": "item-010", "qty": 1},  # Kalbi
            {"item_id": "item-011", "qty": 1},  # Rosu
            {"item_id": "item-003", "qty": 1},  # Harami
            {"category_id": "cat-salad", "qty": 1},  # Any salad
            {"item_id": "item-300", "qty": 2},  # Rice x2
        ]
    },
    {
        "id": "combo-003",
        "code": "BEER-SNACK",
        "name": "ビール＋おつまみセット",
        "name_en": "Beer + Snack Set",
        "desc": "生ビール（中）2杯とキムチ盛り合わせで¥500 OFF",
        "discount_type": "fixed",
        "discount_value": 500,
        "items": [
            {"item_id": "item-100", "qty": 2},  # Draft beer x2
            {"item_id": "item-203", "qty": 1},  # Kimchi
        ]
    },
]

# ============================================
# PROMOTIONS
# ============================================
PROMOTIONS = [
    {
        "id": "promo-001",
        "code": "ORDER-30K-FREE-TONGUE",
        "name": "30,000円以上で牛タン無料",
        "name_en": "Free beef tongue for orders over ¥30,000",
        "desc": "お会計30,000円以上で牛タン（6枚）を1皿プレゼント！",
        "trigger_type": "order_amount",
        "trigger_value": 30000,
        "reward_type": "free_item",
        "reward_item_id": "item-013",  # Beef tongue 6pcs
        "reward_quantity": 1,
        "show_on_menu": True,
    },
    {
        "id": "promo-002",
        "code": "BEER-8-FREE-1",
        "name": "生ビール8杯で1杯無料",
        "name_en": "Buy 8 draft beers, get 1 free",
        "desc": "生ビール（大）を8杯ご注文で、1杯無料！",
        "trigger_type": "item_quantity",
        "trigger_item_id": "item-101",  # Draft beer large
        "trigger_value": 8,
        "reward_type": "free_item",
        "reward_item_id": "item-101",  # Same beer
        "reward_quantity": 1,
        "show_on_menu": True,
    },
    {
        "id": "promo-003",
        "code": "LUNCH-20OFF",
        "name": "ランチタイム20%OFF",
        "name_en": "Lunch 20% discount",
        "desc": "平日11:00-15:00のお食事が20%OFF（ドリンク除く）",
        "trigger_type": "order_amount",
        "trigger_value": 0,  # No minimum
        "reward_type": "discount_order",
        "reward_value": 20,  # 20%
        "valid_hours_start": "11:00",
        "valid_hours_end": "15:00",
        "valid_days": "mon,tue,wed,thu,fri",
        "show_on_menu": True,
    },
]


async def seed_enhanced_menu(branch_code: str = "hirama"):
    """Seed all enhanced menu data for a branch"""
    async with async_session_factory() as session:
        print(f"\n🍖 Seeding enhanced menu for branch: {branch_code}")

        # 1. Categories
        print("  📁 Creating categories...")
        for cat in CATEGORIES:
            category = ItemCategory(
                id=cat["id"],
                branch_code=branch_code,
                code=cat["code"],
                name=cat["name"],
                name_en=cat.get("name_en"),
                parent_id=cat.get("parent"),
                icon=cat.get("icon"),
                display_order=cat.get("order", 0),
                is_active=True
            )
            session.add(category)
        await session.commit()
        print(f"    ✅ Created {len(CATEGORIES)} categories")

        # 2. Items
        print("  🥩 Creating items...")
        for item in ITEMS:
            new_item = Item(
                id=item["id"],
                branch_code=branch_code,
                category_id=item["cat"],
                sku=item.get("sku"),
                name=item["name"],
                name_en=item.get("name_en"),
                description=item.get("desc"),
                base_price=item["price"],
                prep_time_minutes=item.get("prep", 5),
                kitchen_printer=item.get("printer"),
                display_order=item.get("order", 0),
                is_available=True,
                is_popular=item.get("popular", False),
                is_spicy=item.get("spicy", False),
                is_vegetarian=item.get("vegetarian", False),
                allergens=item.get("allergens"),
                has_options=item.get("has_options", False),
            )
            session.add(new_item)
        await session.commit()
        print(f"    ✅ Created {len(ITEMS)} items")

        # 3. Option Groups
        print("  ⚙️ Creating option groups...")
        for og in OPTION_GROUPS:
            group = ItemOptionGroup(
                id=og["id"],
                branch_code=branch_code,
                name=og["name"],
                name_en=og.get("name_en"),
                selection_type=og["type"],
                min_selections=og.get("min", 0),
                max_selections=og.get("max", 1),
                display_order=og.get("order", 0),
                is_active=True
            )
            session.add(group)
        await session.commit()
        print(f"    ✅ Created {len(OPTION_GROUPS)} option groups")

        # 4. Options
        print("  📋 Creating options...")
        for opt in OPTIONS:
            option = ItemOption(
                id=opt["id"],
                group_id=opt["group"],
                name=opt["name"],
                name_en=opt.get("name_en"),
                price_adjustment=opt.get("price", 0),
                is_default=opt.get("default", False),
                display_order=opt.get("order", 0),
                is_available=True
            )
            session.add(option)
        await session.commit()
        print(f"    ✅ Created {len(OPTIONS)} options")

        # 5. Item-Option Assignments
        print("  🔗 Linking items to options...")
        for i, assignment in enumerate(ITEM_OPTIONS):
            link = ItemOptionAssignment(
                id=f"ioa-{i+1:03d}",
                item_id=assignment["item"],
                option_group_id=assignment["group"],
                display_order=i
            )
            session.add(link)
        await session.commit()
        print(f"    ✅ Created {len(ITEM_OPTIONS)} item-option links")

        # 6. Combos
        print("  🎁 Creating combos...")
        for combo_data in COMBOS:
            combo = Combo(
                id=combo_data["id"],
                branch_code=branch_code,
                code=combo_data["code"],
                name=combo_data["name"],
                name_en=combo_data.get("name_en"),
                description=combo_data.get("desc"),
                discount_type=combo_data["discount_type"],
                discount_value=combo_data["discount_value"],
                is_active=True,
                is_featured=combo_data.get("featured", False)
            )
            session.add(combo)

            # Combo items
            for j, ci in enumerate(combo_data.get("items", [])):
                combo_item = ComboItem(
                    id=f"{combo_data['id']}-item-{j+1}",
                    combo_id=combo_data["id"],
                    item_id=ci.get("item_id"),
                    category_id=ci.get("category_id"),
                    quantity=ci.get("qty", 1)
                )
                session.add(combo_item)
        await session.commit()
        print(f"    ✅ Created {len(COMBOS)} combos")

        # 7. Promotions
        print("  🎉 Creating promotions...")
        for promo_data in PROMOTIONS:
            promo = Promotion(
                id=promo_data["id"],
                branch_code=branch_code,
                code=promo_data["code"],
                name=promo_data["name"],
                name_en=promo_data.get("name_en"),
                description=promo_data.get("desc"),
                trigger_type=promo_data["trigger_type"],
                trigger_item_id=promo_data.get("trigger_item_id"),
                trigger_value=promo_data["trigger_value"],
                reward_type=promo_data["reward_type"],
                reward_item_id=promo_data.get("reward_item_id"),
                reward_value=promo_data.get("reward_value"),
                reward_quantity=promo_data.get("reward_quantity", 1),
                show_on_menu=promo_data.get("show_on_menu", False),
                is_active=True
            )
            session.add(promo)
        await session.commit()
        print(f"    ✅ Created {len(PROMOTIONS)} promotions")

        print(f"\n✅ Enhanced menu seeding complete for {branch_code}!")
        print(f"   - {len(CATEGORIES)} categories")
        print(f"   - {len(ITEMS)} items")
        print(f"   - {len(OPTION_GROUPS)} option groups")
        print(f"   - {len(OPTIONS)} options")
        print(f"   - {len(ITEM_OPTIONS)} item-option links")
        print(f"   - {len(COMBOS)} combos")
        print(f"   - {len(PROMOTIONS)} promotions")


if __name__ == "__main__":
    asyncio.run(seed_enhanced_menu())

```

## File ./backend\scripts\__init__.py:
```python
﻿# Scripts package


```

