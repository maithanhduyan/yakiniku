"""
Promotion Model - Order threshold rewards and special offers
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Promotion(Base):
    """
    Promotion/reward based on order conditions
    Examples:
    - Order ≥ ¥30,000 → Free beef tongue
    - Buy 8 large beers → Get 1 free
    """
    __tablename__ = "promotions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Identity
    code = Column(String(50), nullable=False)              # 'ORDER-30K-FREE-TONGUE'
    name = Column(String(200), nullable=False)             # '30,000円以上で牛タン無料'
    name_en = Column(String(200))
    description = Column(Text)

    # Trigger conditions
    trigger_type = Column(String(30), nullable=False)      # 'order_amount', 'item_quantity', 'item_total'
    trigger_item_id = Column(String(36), ForeignKey('items.id'), nullable=True)  # For item-based triggers
    trigger_category_id = Column(String(36), ForeignKey('item_categories.id'), nullable=True)  # Category-based
    trigger_value = Column(Numeric(10, 0), nullable=False) # ¥30,000 or quantity 8

    # Reward
    reward_type = Column(String(30), nullable=False)       # 'free_item', 'discount_item', 'discount_order', 'points_bonus'
    reward_item_id = Column(String(36), ForeignKey('items.id'), nullable=True)  # Item to give free
    reward_value = Column(Numeric(10, 2), nullable=True)   # Discount % or amount
    reward_quantity = Column(Integer, default=1)           # Give 1 free item

    # Validity period
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    valid_hours_start = Column(Time, nullable=True)
    valid_hours_end = Column(Time, nullable=True)
    valid_days = Column(String(50), nullable=True)         # 'sat,sun' for weekend only

    # Limits
    max_uses_per_order = Column(Integer, default=1)
    max_uses_per_customer = Column(Integer, nullable=True)
    max_uses_total = Column(Integer, nullable=True)
    current_uses = Column(Integer, default=0)

    # Stacking rules
    stackable = Column(Boolean, default=False)             # Can combine with other promos?
    priority = Column(Integer, default=0)                  # Higher = apply first

    # Display
    display_order = Column(Integer, default=0)
    image_url = Column(String(500))
    show_on_menu = Column(Boolean, default=True)           # Show as banner/notice

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    trigger_item = relationship("Item", foreign_keys=[trigger_item_id])
    trigger_category = relationship("ItemCategory", foreign_keys=[trigger_category_id])
    reward_item = relationship("Item", foreign_keys=[reward_item_id])

    def __repr__(self):
        return f"<Promotion {self.name}>"


class PromotionUsage(Base):
    """
    Track promotion usage per order/customer
    """
    __tablename__ = "promotion_usages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    promotion_id = Column(String(36), ForeignKey('promotions.id'), nullable=False)
    order_id = Column(String(36), nullable=False)          # Link to order
    customer_id = Column(String(36), nullable=True)        # If customer identified

    # Applied discount
    discount_amount = Column(Numeric(10, 0), nullable=False)

    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    promotion = relationship("Promotion")

    def __repr__(self):
        return f"<PromotionUsage promo={self.promotion_id} order={self.order_id}>"
