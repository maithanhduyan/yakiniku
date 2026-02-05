"""
Shared Models - Re-export from legacy models
"""
# Re-export from legacy models
from app.models.branch import Branch
from app.models.menu import MenuItem
from app.models.table import Table

__all__ = ["Branch", "MenuItem", "Table"]
