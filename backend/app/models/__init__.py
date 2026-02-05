"""
SQLAlchemy Models
"""
from app.models.branch import Branch
from app.models.customer import Customer, GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference
from app.models.booking import Booking
from app.models.chat import ChatMessage, ChatInsight
from app.models.table import Table, TableAssignment, TableAvailability
from app.models.menu import MenuItem, MenuCategory
from app.models.order import Order, OrderItem, TableSession, OrderStatus
from app.models.staff import Staff, StaffRole

# New enhanced menu models
from app.models.category import ItemCategory
from app.models.item import Item, ItemOptionGroup, ItemOption, ItemOptionAssignment
from app.models.combo import Combo, ComboItem
from app.models.promotion import Promotion, PromotionUsage

__all__ = [
    # Branch & Customer
    "Branch",
    "Customer",
    "GlobalCustomer",
    "BranchCustomer",
    "CustomerPreference",

    # Booking & Chat
    "Booking",
    "ChatMessage",
    "ChatInsight",

    # Tables
    "Table",
    "TableAssignment",
    "TableAvailability",

    # Menu (legacy)
    "MenuItem",
    "MenuCategory",

    # Menu (new - enhanced)
    "ItemCategory",
    "Item",
    "ItemOptionGroup",
    "ItemOption",
    "ItemOptionAssignment",

    # Combos & Promotions
    "Combo",
    "ComboItem",
    "Promotion",
    "PromotionUsage",

    # Orders
    "Order",
    "OrderItem",
    "TableSession",
    "OrderStatus",

    # Staff
    "Staff",
    "StaffRole",
]
