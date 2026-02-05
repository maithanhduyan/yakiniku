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
    AVAILABLE = "available"      # BÃ n trá»‘ng
    OCCUPIED = "occupied"        # Äang cÃ³ khÃ¡ch
    RESERVED = "reserved"        # ÄÃ£ Ä‘áº·t trÆ°á»›c
    CLEANING = "cleaning"        # Äang dá»n dáº¹p
    MAINTENANCE = "maintenance"  # Báº£o trÃ¬


class TableType(str, enum.Enum):
    REGULAR = "regular"     # BÃ n thÆ°á»ng
    PRIVATE = "private"     # PhÃ²ng riÃªng / bÃ n VIP
    COUNTER = "counter"     # Quáº§y bar
    TERRACE = "terrace"     # NgoÃ i trá»i


class Table(Base):
    """Restaurant table configuration"""
    __tablename__ = "tables"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Table identity
    table_number = Column(String(10), nullable=False)  # "A1", "B2", "VIP1"
    name = Column(String(100))  # "çª“éš›å¸­", "å€‹å®¤A"

    # Capacity
    min_capacity = Column(Integer, default=1)   # Tá»‘i thiá»ƒu 1 ngÆ°á»i
    max_capacity = Column(Integer, nullable=False)  # 4 hoáº·c 6 gháº¿

    # Location & Type
    table_type = Column(String(20), default=TableType.REGULAR.value)
    floor = Column(Integer, default=1)  # Táº§ng
    zone = Column(String(50))  # "A", "B", "VIP", "Window"

    # Features
    has_window = Column(Boolean, default=False)      # Gáº§n cá»­a sá»•
    is_smoking = Column(Boolean, default=False)      # Khu hÃºt thuá»‘c
    is_wheelchair_accessible = Column(Boolean, default=True)
    has_baby_chair = Column(Boolean, default=False)  # CÃ³ gháº¿ tráº» em

    # Status
    status = Column(String(20), default=TableStatus.AVAILABLE.value)
    is_active = Column(Boolean, default=True)  # BÃ n cÃ³ hoáº¡t Ä‘á»™ng khÃ´ng

    # Metadata
    priority = Column(Integer, default=0)  # Æ¯u tiÃªn xáº¿p khÃ¡ch (VIP = cao hÆ¡n)
    notes = Column(String(500))  # Ghi chÃº ná»™i bá»™

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Table {self.table_number} ({self.max_capacity}å¸­)>"


class TableAssignment(Base):
    """Link booking to specific table(s)"""
    __tablename__ = "table_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=False, index=True)
    table_id = Column(String(36), ForeignKey("tables.id"), nullable=False, index=True)

    # Time tracking
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    seated_at = Column(DateTime(timezone=True))   # Khi khÃ¡ch ngá»“i
    cleared_at = Column(DateTime(timezone=True))  # Khi khÃ¡ch rá»i Ä‘i

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

