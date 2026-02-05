"""
Item Category Model - Menu categories hierarchy
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ItemCategory(Base):
    """
    Menu category hierarchy
    Examples: 肉類 > 牛肉 > 和牛
              飲み物 > ビール
    """
    __tablename__ = "item_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Identity
    code = Column(String(50), nullable=False)           # 'meat', 'beef', 'drinks'
    name = Column(String(100), nullable=False)          # '肉類', '牛肉', '飲み物'
    name_en = Column(String(100))                       # 'Meat', 'Beef', 'Drinks'
    description = Column(Text)

    # Hierarchy
    parent_id = Column(String(36), ForeignKey('item_categories.id'), nullable=True)

    # Display
    display_order = Column(Integer, default=0)
    icon = Column(String(50))                           # emoji: '🥩', '🍺'
    image_url = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent = relationship("ItemCategory", remote_side=[id], backref="subcategories")
    items = relationship("Item", back_populates="category")

    def __repr__(self):
        return f"<ItemCategory {self.code}: {self.name}>"
