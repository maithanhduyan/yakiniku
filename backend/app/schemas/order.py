"""
Order Schemas - Pydantic models for orders
"""
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


# ============ Order Item Schemas ============

class OrderItemCreate(BaseModel):
    menu_item_id: str
    quantity: int = 1
    notes: Optional[str] = None


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


class OrderItemKitchen(BaseModel):
    """Simplified item for kitchen display"""
    id: str
    item_name: str
    quantity: int
    notes: Optional[str] = None
    status: str


# ============ Order Schemas ============

class OrderCreate(BaseModel):
    table_id: str
    session_id: str
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: str
    branch_code: str
    table_id: str
    session_id: str
    order_number: int
    status: str
    items: List[OrderItemResponse]
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    served_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderKitchen(BaseModel):
    """Order view for kitchen display (KDS)"""
    id: str
    order_number: int
    table_number: str
    status: str
    items: List[OrderItemKitchen]
    created_at: datetime
    elapsed_minutes: float


class OrderStatusUpdate(BaseModel):
    status: str


# ============ Table Session Schemas ============

class TableSessionCreate(BaseModel):
    table_id: str
    guest_count: int = 1
    booking_id: Optional[str] = None


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


class TableSessionSummary(BaseModel):
    """Summary for POS checkout"""
    session_id: str
    table_number: str
    guest_count: int
    started_at: datetime
    orders: List[OrderResponse]
    subtotal: Decimal
    tax: Decimal
    total: Decimal


# ============ Staff Call ============

class StaffCallRequest(BaseModel):
    table_id: str
    session_id: str
    call_type: str = "assistance"  # assistance, water, bill, etc.
    message: Optional[str] = None

