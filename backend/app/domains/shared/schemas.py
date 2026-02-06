"""
Shared Schemas - Base schemas for cross-domain use
"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class BranchBase(BaseModel):
    code: str
    name: str
    subdomain: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class MenuItemBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    image_url: Optional[str] = None
    is_available: bool = True
    is_popular: bool = False
    is_spicy: bool = False

    class Config:
        from_attributes = True


class TableBase(BaseModel):
    id: str
    table_number: str
    capacity: int
    zone: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True

