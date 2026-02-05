"""
POS Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    paypay = "paypay"
    linepay = "linepay"


class TableStatusEnum(str, Enum):
    available = "available"    # ç©ºå¸­
    occupied = "occupied"      # ä½¿ç”¨ä¸­
    pending_payment = "pending_payment"  # æœªä¼šè¨ˆ
    cleaning = "cleaning"      # æ¸…æŽƒä¸­


class CheckoutRequest(BaseModel):
    session_id: str
    payment_method: PaymentMethod
    discount_amount: Decimal = Decimal("0")
    discount_reason: Optional[str] = None
    received_amount: Optional[Decimal] = None  # For cash payment


class CheckoutResponse(BaseModel):
    session_id: str
    table_number: str
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    payment_method: str
    change: Optional[Decimal] = None
    receipt_number: str
    completed_at: datetime


class TableOverview(BaseModel):
    id: str
    table_number: str
    capacity: int
    zone: Optional[str] = None
    status: TableStatusEnum
    session_id: Optional[str] = None
    guest_count: Optional[int] = None
    current_total: Decimal = Decimal("0")
    started_at: Optional[datetime] = None
    order_count: int = 0


class POSDashboard(BaseModel):
    tables: list[TableOverview]
    summary: dict  # occupied, available, pending_payment counts

