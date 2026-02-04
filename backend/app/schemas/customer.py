"""
Customer Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class PreferenceCreate(BaseModel):
    """Schema for creating customer preference"""
    preference: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = None  # meat, cooking, allergy, occasion
    note: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "manual"  # chat, booking, manual


class PreferenceResponse(BaseModel):
    """Schema for preference response"""
    id: str
    preference: str
    category: Optional[str]
    note: Optional[str]
    confidence: float
    source: str

    model_config = {"from_attributes": True}


class CustomerCreate(BaseModel):
    """Schema for creating/identifying customer"""
    phone: str = Field(..., min_length=10, max_length=20)
    name: Optional[str] = None
    email: Optional[str] = None


class CustomerResponse(BaseModel):
    """Schema for customer response"""
    id: str
    phone: str
    name: Optional[str]
    email: Optional[str]
    visit_count: int
    is_vip: bool
    preferences: List[PreferenceResponse] = []

    model_config = {"from_attributes": True}
