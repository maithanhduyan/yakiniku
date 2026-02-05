"""
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
