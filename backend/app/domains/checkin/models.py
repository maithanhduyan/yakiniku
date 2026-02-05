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
