"""
Chat Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    """Request for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=1000)
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = None
    branch_code: str = "hirama"


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    response: str
    customer_recognized: bool = False
    customer_name: Optional[str] = None
    insights_extracted: int = 0  # Number of new insights saved
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class InsightExtraction(BaseModel):
    """Extracted customer insight from chat"""
    preference: str
    category: str  # meat, cooking, allergy, occasion
    confidence: float = 0.8

