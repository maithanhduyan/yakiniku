"""
SQLAlchemy Models
"""
from app.models.branch import Branch
from app.models.customer import Customer, GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference
from app.models.booking import Booking
from app.models.chat import ChatMessage, ChatInsight
from app.models.table import Table, TableAssignment, TableAvailability

__all__ = [
    "Branch",
    "Customer",
    "GlobalCustomer",
    "BranchCustomer",
    "CustomerPreference",
    "Booking",
    "ChatMessage",
    "ChatInsight",
    "Table",
    "TableAssignment",
    "TableAvailability",
]
