"""
User Model - Operators who run the restaurant apps.

Role hierarchy:
  chef_manager  → Regional director, manages multiple branches via Dashboard
  manager       → Branch manager, full access to all apps within their branch
  staff         → Frontline employee, limited to operational apps (checkin, table-order, kitchen)

Each user links to a staff record and has explicit app-level permissions.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from enum import Enum
import uuid
import hashlib

from app.database import Base


class UserRole(str, Enum):
    """Hierarchical operator roles"""
    CHEF_MANAGER = "chef_manager"   # 統括マネージャー — multi-branch dashboard
    MANAGER = "manager"             # 店長 — single-branch full access
    STAFF = "staff"                 # スタッフ — operational apps only


class User(Base):
    """
    Application operator — someone who logs in to run the system.
    Separated from Staff (HR record) to keep auth concerns isolated.
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Link to staff record (optional — chef_manager may not belong to a single branch)
    staff_id = Column(String(36), ForeignKey("staff.id", ondelete="SET NULL"), nullable=True)
    branch_code = Column(String(50), nullable=True, index=True)  # NULL for chef_manager (multi-branch)

    # Credentials
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)  # SHA-256 hex digest
    display_name = Column(String(100), nullable=False)

    # Role
    role = Column(String(20), nullable=False, default=UserRole.STAFF.value, index=True)

    # App permissions — which frontends this user can access
    can_dashboard = Column(Boolean, default=False)    # Dashboard admin app
    can_checkin = Column(Boolean, default=False)       # Check-in kiosk
    can_table_order = Column(Boolean, default=False)   # Table ordering iPad
    can_kitchen = Column(Boolean, default=False)       # Kitchen display (KDS)
    can_pos = Column(Boolean, default=False)           # Point of sale

    # Multi-branch access (chef_manager only)
    # Comma-separated branch codes, e.g. "hirama,shinjuku,yaesu"
    # NULL = single branch (use branch_code), "*" = all branches
    managed_branches = Column(String(500), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Notes
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role}) [{self.branch_code or 'multi'}]>"

    @staticmethod
    def hash_password(plain: str) -> str:
        """Simple SHA-256 hash for demo purposes. Use bcrypt in production."""
        return hashlib.sha256(plain.encode()).hexdigest()
