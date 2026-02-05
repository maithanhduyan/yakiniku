"""
Item Model - Enhanced menu items with options support
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Item(Base):
    """
    Menu item with options support
    Example: 和牛A5サーロイン ¥3,500 (has_options: true)
    """
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey('item_categories.id'), nullable=True)

    # Identity
    sku = Column(String(50), unique=True, nullable=True)  # 'MEAT-WAGYU-A5-001'
    name = Column(String(100), nullable=False)             # '和牛A5サーロイン'
    name_en = Column(String(100))                          # 'Wagyu A5 Sirloin'
    description = Column(Text)

    # Pricing
    base_price = Column(Numeric(10, 0), nullable=False)    # ¥3,500
    tax_rate = Column(Numeric(4, 2), default=10.0)         # 10%

    # Kitchen
    prep_time_minutes = Column(Integer, default=5)
    kitchen_printer = Column(String(50))                   # 'grill', 'drink', 'cold'
    kitchen_note = Column(Text)

    # Display
    display_order = Column(Integer, default=0)
    image_url = Column(String(500))

    # Flags
    is_available = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    is_spicy = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)
    allergens = Column(String(200))                        # 'egg,milk,wheat'

    # Option configuration
    has_options = Column(Boolean, default=False)
    options_required = Column(Boolean, default=False)      # Must select at least 1 option

    # Stock management (future)
    track_stock = Column(Boolean, default=False)
    stock_quantity = Column(Integer, nullable=True)
    low_stock_alert = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("ItemCategory", back_populates="items")
    option_assignments = relationship("ItemOptionAssignment", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Item {self.name} ¥{self.base_price}>"


class ItemOptionGroup(Base):
    """
    Option group - groups related options together
    Examples: 'ご飯の量', '焼き加減', 'トッピング'
    """
    __tablename__ = "item_option_groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Identity
    name = Column(String(100), nullable=False)             # 'ご飯の量'
    name_en = Column(String(100))                          # 'Rice Amount'
    description = Column(Text)

    # Selection rules
    selection_type = Column(String(20), nullable=False, default='single')  # 'single', 'multiple'
    min_selections = Column(Integer, default=0)            # 0 = optional
    max_selections = Column(Integer, default=1)            # for multiple selection

    # Display
    display_order = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    options = relationship("ItemOption", back_populates="group", cascade="all, delete-orphan")
    item_assignments = relationship("ItemOptionAssignment", back_populates="option_group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ItemOptionGroup {self.name}>"


class ItemOption(Base):
    """
    Individual option choice
    Examples: '少なめ +¥0', '大盛り +¥100', 'レア', 'ミディアム'
    """
    __tablename__ = "item_options"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36), ForeignKey('item_option_groups.id'), nullable=False)

    # Identity
    name = Column(String(100), nullable=False)             # '大盛り'
    name_en = Column(String(100))                          # 'Large'

    # Pricing
    price_adjustment = Column(Numeric(10, 0), default=0)   # +¥100 or -¥50

    # Display
    is_default = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)

    # Status
    is_available = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    group = relationship("ItemOptionGroup", back_populates="options")

    def __repr__(self):
        adj = f"+¥{self.price_adjustment}" if self.price_adjustment > 0 else f"¥{self.price_adjustment}"
        return f"<ItemOption {self.name} {adj}>"


class ItemOptionAssignment(Base):
    """
    Links items to their available option groups
    Example: ビビンバ → [ご飯の量, トッピング]
    """
    __tablename__ = "item_option_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String(36), ForeignKey('items.id'), nullable=False)
    option_group_id = Column(String(36), ForeignKey('item_option_groups.id'), nullable=False)

    # Display order within item's options
    display_order = Column(Integer, default=0)

    # Relationships
    item = relationship("Item", back_populates="option_assignments")
    option_group = relationship("ItemOptionGroup", back_populates="item_assignments")

    def __repr__(self):
        return f"<ItemOptionAssignment item={self.item_id} group={self.option_group_id}>"
