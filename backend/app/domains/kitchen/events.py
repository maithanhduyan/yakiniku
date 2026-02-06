"""
Event Sourcing for Kitchen Domain
Tracks all kitchen staff actions for quality improvement

Event Types:
- ITEM_SERVED : Item marked as served/delivered
- ITEM_CANCELLED : Item cancelled (by customer or kitchen)
- ITEM_STARTED : Item preparation started
- ITEM_RECALLED : Item recalled / sent back
- STATION_SWITCHED : Staff switched active station view
- CONFIG_CHANGED : Kitchen config changed (thresholds etc.)
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Index
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum
import uuid

from app.database import Base


# ============ Event Types ============

class KitchenEventType(str, Enum):
    # Item lifecycle in kitchen
    ITEM_SERVED = "kitchen.item.served"           # Item marked as done/delivered
    ITEM_CANCELLED = "kitchen.item.cancelled"     # Item cancelled
    ITEM_STARTED = "kitchen.item.started"         # Started preparing
    ITEM_RECALLED = "kitchen.item.recalled"       # Item returned/recalled

    # Station events
    STATION_SWITCHED = "kitchen.station.switched"

    # System events
    CONFIG_CHANGED = "kitchen.config.changed"
    DISPLAY_CONNECTED = "kitchen.display.connected"
    DISPLAY_DISCONNECTED = "kitchen.display.disconnected"


class KitchenEventSource(str, Enum):
    """Where the kitchen event originated"""
    KITCHEN_DISPLAY = "kitchen-display"   # Kitchen staff via KDS
    POS = "pos"                           # POS override
    TABLE_ORDER = "table-order"           # Customer action (cancel)
    SYSTEM = "system"                     # Backend automation


# ============ SQLAlchemy Model ============

class KitchenEvent(Base):
    """
    Event log for kitchen actions.
    Immutable append-only log for tracking kitchen performance.
    """
    __tablename__ = "kitchen_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Event metadata
    event_type = Column(String(50), nullable=False, index=True)
    event_source = Column(String(30), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Context
    branch_code = Column(String(50), nullable=False, index=True)
    table_id = Column(String(36), index=True)
    table_number = Column(String(20))
    session_id = Column(String(36), index=True)
    order_id = Column(String(36), index=True)
    order_item_id = Column(String(36), index=True)

    # Item snapshot (denormalized for history display)
    item_name = Column(String(100))
    item_quantity = Column(Integer)
    station = Column(String(20))  # meat, side, drink

    # Actor (who triggered)
    actor_type = Column(String(20))  # staff, customer, system
    actor_id = Column(String(36))

    # Extra data (JSON)
    data = Column(JSON, default=dict)

    # Performance tracking
    wait_time_seconds = Column(Integer)  # How long item waited before action

    # Composite indexes
    __table_args__ = (
        Index('ix_kitchen_events_branch_time', 'branch_code', 'timestamp'),
        Index('ix_kitchen_events_type_time', 'event_type', 'timestamp'),
        Index('ix_kitchen_events_station_time', 'station', 'timestamp'),
        Index('ix_kitchen_events_order', 'order_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<KitchenEvent {self.event_type} {self.item_name} @ {self.timestamp}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_source": self.event_source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "branch_code": self.branch_code,
            "table_number": self.table_number,
            "order_id": self.order_id,
            "item_name": self.item_name,
            "item_quantity": self.item_quantity,
            "station": self.station,
            "wait_time_seconds": self.wait_time_seconds,
            "data": self.data,
        }


# ============ Pydantic Schemas ============

class KitchenEventCreate(BaseModel):
    """Schema for creating a kitchen event from frontend"""
    event_type: KitchenEventType
    event_source: KitchenEventSource = KitchenEventSource.KITCHEN_DISPLAY
    branch_code: str
    table_id: Optional[str] = None
    table_number: Optional[str] = None
    session_id: Optional[str] = None
    order_id: Optional[str] = None
    order_item_id: Optional[str] = None
    item_name: Optional[str] = None
    item_quantity: Optional[int] = None
    station: Optional[str] = None
    actor_type: Optional[str] = "staff"
    actor_id: Optional[str] = None
    data: dict = Field(default_factory=dict)
    wait_time_seconds: Optional[int] = None


class KitchenEventResponse(BaseModel):
    """Schema for event response"""
    id: str
    event_type: str
    event_source: str
    timestamp: datetime
    branch_code: str
    table_number: Optional[str] = None
    order_id: Optional[str] = None
    item_name: Optional[str] = None
    item_quantity: Optional[int] = None
    station: Optional[str] = None
    wait_time_seconds: Optional[int] = None
    data: dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class KitchenHistoryResponse(BaseModel):
    """History response with events grouped"""
    events: list[KitchenEventResponse]
    total: int
    summary: dict = Field(default_factory=dict)
