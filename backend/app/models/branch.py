"""
Branch Model - Multi-tenant support
"""
from sqlalchemy import Column, String, Integer, Time, Boolean, JSON, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Branch(Base):
    """Restaurant branch configuration"""
    __tablename__ = "branches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)  # 'jinan', 'shibuya'
    name = Column(String(255), nullable=False)  # '焼肉ジナン 平間本店'
    subdomain = Column(String(100))  # 'jinan', 'shibuya'

    # Contact
    phone = Column(String(20))
    address = Column(String(500))

    # Branding
    theme_primary_color = Column(String(7), default="#d4af37")
    theme_bg_color = Column(String(7), default="#1a1a1a")
    logo_url = Column(String(500))

    # Operations
    opening_time = Column(Time)  # 17:00
    closing_time = Column(Time)  # 23:00
    last_order_time = Column(Time)  # 22:30
    closed_days = Column(JSON, default=[2])  # [2] = Tuesday (0=Sun, 1=Mon, ...)
    max_capacity = Column(Integer, default=30)

    # Features
    features = Column(JSON, default={
        "chat": True,
        "ai_booking": True,
        "customer_insights": True,
    })

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
