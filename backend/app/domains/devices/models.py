"""
Device Management Models
Manage authorized devices (table-order, kitchen, pos, checkin)
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class DeviceType(str, enum.Enum):
    TABLE_ORDER = "table-order"     # iPad注文端末
    KITCHEN = "kitchen"             # KDS表示
    POS = "pos"                     # レジ
    CHECKIN = "checkin"             # チェックイン端末


class DeviceStatus(str, enum.Enum):
    ACTIVE = "active"               # 有効
    INACTIVE = "inactive"           # 無効化
    PENDING = "pending"             # QRスキャン待ち


class Device(Base):
    """Authorized device for the restaurant system"""
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Device identity
    name = Column(String(100), nullable=False)           # "テーブルB1端末", "キッチン1F"
    device_type = Column(String(20), nullable=False)     # table-order, kitchen, pos, checkin

    # Authorization token (embedded in QR code)
    token = Column(String(64), unique=True, nullable=False, index=True)

    # Config payload — stored as JSON text
    # table-order: {"table_id": "...", "table_number": "B1"}
    # kitchen:     {"station": "all", "floor": 1}
    # pos:         {"register_number": 1}
    # checkin:     {}
    config = Column(Text, default="{}")

    # Table link (table-order only)
    table_id = Column(String(36), ForeignKey("tables.id", ondelete="SET NULL"), nullable=True)
    table_number = Column(String(10), nullable=True)     # Denormalized for quick display

    # Status
    status = Column(String(20), default=DeviceStatus.PENDING.value, index=True)

    # Session binding (1 QR = 1 device only)
    device_fingerprint = Column(String(64), nullable=True)     # SHA-256 of browser/device info
    session_token = Column(String(64), unique=True, nullable=True, index=True)  # Active session token
    session_expires_at = Column(DateTime(timezone=True))       # 1 year from activation

    # Audit
    last_seen_at = Column(DateTime(timezone=True))       # Last heartbeat
    activated_at = Column(DateTime(timezone=True))       # First successful login
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100))                     # Staff who created

    # Notes
    notes = Column(String(500))

    def __repr__(self):
        return f"<Device {self.name} ({self.device_type}) [{self.status}]>"
