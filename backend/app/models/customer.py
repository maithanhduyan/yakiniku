"""
Customer Models - Global and Per-Branch
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class GlobalCustomer(Base):
    """
    Global customer identity (by phone)
    Shared across all branches
    """
    __tablename__ = "global_customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    branch_customers = relationship("BranchCustomer", back_populates="global_customer")


class BranchCustomer(Base):
    """
    Per-branch customer relationship
    Tracks visits and VIP status per branch
    """
    __tablename__ = "branch_customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    global_customer_id = Column(String(36), ForeignKey("global_customers.id"), nullable=False)
    branch_code = Column(String(50), nullable=False, index=True)

    visit_count = Column(Integer, default=0)
    last_visit = Column(DateTime(timezone=True))
    is_vip = Column(Boolean, default=False)
    notes = Column(String(1000))  # Staff notes

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    global_customer = relationship("GlobalCustomer", back_populates="branch_customers")
    preferences = relationship("CustomerPreference", back_populates="branch_customer")

    # Composite unique constraint
    __table_args__ = (
        # UniqueConstraint('global_customer_id', 'branch_code', name='uq_customer_branch'),
    )


# Alias for backward compatibility
Customer = BranchCustomer

