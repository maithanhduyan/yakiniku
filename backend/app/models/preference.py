"""
Customer Preference Model
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class CustomerPreference(Base):
    """
    Customer preference/insight
    Can be AI-extracted or manually added
    """
    __tablename__ = "customer_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_customer_id = Column(String(36), ForeignKey("branch_customers.id"), nullable=False)

    preference = Column(String(255), nullable=False)  # 'ãƒ¬ãƒåˆºã—', 'åŽšåˆ‡ã‚Š'
    category = Column(String(50))  # 'meat', 'cooking', 'allergy', 'occasion'
    note = Column(String(500))  # Additional context

    # Source tracking
    confidence = Column(Float, default=1.0)  # 0.0-1.0 (AI=low, manual=1.0)
    source = Column(String(50), default="manual")  # 'chat', 'booking', 'manual'

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    branch_customer = relationship("BranchCustomer", back_populates="preferences")

