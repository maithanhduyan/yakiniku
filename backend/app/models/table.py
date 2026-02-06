"""
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

