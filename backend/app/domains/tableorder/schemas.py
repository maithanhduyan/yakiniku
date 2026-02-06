"""
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
