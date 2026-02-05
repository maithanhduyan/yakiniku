"""
Menu Model - Menu items and categories
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Numeric
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class MenuCategory(str, enum.Enum):
    MEAT = "meat"           # è‚‰é¡ž
    DRINKS = "drinks"       # é£²ç‰©
    SALAD = "salad"         # ã‚µãƒ©ãƒ€
    RICE = "rice"           # ã”é£¯ãƒ»éºº
    SIDE = "side"           # ã‚µã‚¤ãƒ‰ãƒ¡ãƒ‹ãƒ¥ãƒ¼
    DESSERT = "dessert"     # ãƒ‡ã‚¶ãƒ¼ãƒˆ
    SET = "set"             # ã‚»ãƒƒãƒˆãƒ¡ãƒ‹ãƒ¥ãƒ¼


class MenuItem(Base):
    """Menu item configuration"""
    __tablename__ = "menu_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    branch_code = Column(String(50), nullable=False, index=True)

    # Item identity
    name = Column(String(100), nullable=False)          # ä¸Šãƒãƒ©ãƒŸ
    name_en = Column(String(100))                       # Premium Harami
    description = Column(Text)                          # èª¬æ˜Ž

    # Category & Display
    category = Column(String(30), nullable=False, index=True)  # meat, drinks, etc.
    subcategory = Column(String(50))                    # beef, pork, chicken
    display_order = Column(Integer, default=0)          # Sort order in menu

    # Pricing
    price = Column(Numeric(10, 0), nullable=False)      # Â¥1,800
    tax_rate = Column(Numeric(4, 2), default=10.0)      # 10%

    # Image
    image_url = Column(String(500))                     # Image path

    # Kitchen info
    prep_time_minutes = Column(Integer, default=5)      # Estimated prep time
    kitchen_note = Column(String(200))                  # Instructions for kitchen

    # Flags
    is_available = Column(Boolean, default=True)        # Currently available
    is_popular = Column(Boolean, default=False)         # Show as recommended
    is_spicy = Column(Boolean, default=False)           # è¾›ã„
    is_vegetarian = Column(Boolean, default=False)      # ãƒ™ã‚¸ã‚¿ãƒªã‚¢ãƒ³
    allergens = Column(String(200))                     # egg, milk, wheat, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<MenuItem {self.name} Â¥{self.price}>"

