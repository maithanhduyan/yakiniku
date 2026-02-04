"""
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

    # Metadata
    source = Column(String(50), default="web")  # 'web', 'chat', 'phone'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    branch_customer = relationship("BranchCustomer")
