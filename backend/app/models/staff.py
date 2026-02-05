"""
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
