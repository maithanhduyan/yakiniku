"""
Chat Models - Message History and Extracted Insights
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ChatMessage(Base):
    """Chat message history"""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)
    branch_customer_id = Column(String(36), ForeignKey("branch_customers.id"))
    session_id = Column(String(100), nullable=False, index=True)

    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(String(5000), nullable=False)

    insights_extracted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatInsight(Base):
    """Insights extracted from chat by LLM"""
    __tablename__ = "chat_insights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_customer_id = Column(String(36), ForeignKey("branch_customers.id"))
    message_id = Column(String(36), ForeignKey("chat_messages.id"))

    insight_type = Column(String(50))  # 'preference', 'occasion', 'feedback', 'allergy'
    insight_value = Column(String(500))
    confidence = Column(String(10))  # 'high', 'medium', 'low'

    created_at = Column(DateTime(timezone=True), server_default=func.now())

