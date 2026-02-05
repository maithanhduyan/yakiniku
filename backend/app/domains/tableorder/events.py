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
