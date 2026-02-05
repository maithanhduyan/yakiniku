"""
Combo Model - Set meals and combo discounts
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Combo(Base):
    """
    Combo deal - multiple items with discount
    Example: 和牛A5 + サラダセット (30% off)
    """
    __tablename__ = "combos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Identity
    code = Column(String(50), nullable=False)              # 'WAGYU-SALAD-30'
    name = Column(String(200), nullable=False)             # '和牛A5 + サラダセット'
    name_en = Column(String(200))                          # 'Wagyu A5 + Salad Set'
    description = Column(Text)

    # Discount
    discount_type = Column(String(20), nullable=False)     # 'percentage', 'fixed', 'new_price'
    discount_value = Column(Numeric(10, 2), nullable=False)  # 30 (%), ¥500, or ¥2800

    # Validity period
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    valid_hours_start = Column(Time, nullable=True)        # 17:00 (dinner only)
    valid_hours_end = Column(Time, nullable=True)          # 22:00
    valid_days = Column(String(50), nullable=True)         # 'mon,tue,wed,thu,fri' or null for all

    # Limits
    max_uses_total = Column(Integer, nullable=True)        # null = unlimited
    max_uses_per_order = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
    min_order_amount = Column(Numeric(10, 0), nullable=True)  # Minimum order to apply

    # Display
    display_order = Column(Integer, default=0)
    image_url = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)           # Show prominently

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    items = relationship("ComboItem", back_populates="combo", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Combo {self.name} {self.discount_value}{'%' if self.discount_type == 'percentage' else '¥'} off>"


class ComboItem(Base):
    """
    Items required to trigger a combo
    Example: Combo needs 1x Wagyu + 1x Any Salad
    """
    __tablename__ = "combo_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    combo_id = Column(String(36), ForeignKey('combos.id'), nullable=False)

    # Item matching
    item_id = Column(String(36), ForeignKey('items.id'), nullable=True)       # Specific item
    category_id = Column(String(36), ForeignKey('item_categories.id'), nullable=True)  # Any item in category

    # Quantity
    quantity = Column(Integer, default=1)                  # Need this many

    # Relationships
    combo = relationship("Combo", back_populates="items")
    item = relationship("Item")
    category = relationship("ItemCategory")

    def __repr__(self):
        return f"<ComboItem combo={self.combo_id} qty={self.quantity}>"
