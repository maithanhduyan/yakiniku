"""
Branch Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class BranchCreate(BaseModel):
    """Schema for creating a branch"""
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    subdomain: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    theme_primary_color: str = "#d4af37"
    theme_bg_color: str = "#1a1a1a"
    opening_time: Optional[str] = "17:00"
    closing_time: Optional[str] = "23:00"
    closed_days: List[int] = [2]  # Tuesday
    max_capacity: int = 30


class BranchResponse(BaseModel):
    """Schema for branch response"""
    id: str
    code: str
    name: str
    subdomain: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    theme_primary_color: str
    theme_bg_color: str
    opening_time: Optional[str]
    closing_time: Optional[str]
    closed_days: List[int]
    max_capacity: int
    features: Dict[str, Any]
    is_active: bool

    model_config = {"from_attributes": True}
