"""
Menu Schemas - Pydantic models for menu items
"""
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class MenuItemBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    is_available: bool = True
    is_popular: bool = False
    is_spicy: bool = False
    is_vegetarian: bool = False
    allergens: Optional[str] = None
    prep_time_minutes: int = 5


class MenuItemCreate(MenuItemBase):
    branch_code: str


class MenuItemResponse(MenuItemBase):
    id: str
    branch_code: str
    display_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class MenuCategoryResponse(BaseModel):
    category: str
    category_label: str
    icon: str
    items: List[MenuItemResponse]


class MenuResponse(BaseModel):
    branch_code: str
    categories: List[MenuCategoryResponse]
    updated_at: datetime

