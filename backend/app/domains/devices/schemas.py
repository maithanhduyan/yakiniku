"""
Device Management Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class DeviceTypeEnum(str, Enum):
    table_order = "table-order"
    kitchen = "kitchen"
    pos = "pos"
    checkin = "checkin"


class DeviceStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"


# ── Create ──
class DeviceCreate(BaseModel):
    branch_code: str = "hirama"
    name: str = Field(..., min_length=1, max_length=100)
    device_type: DeviceTypeEnum
    table_id: Optional[str] = None
    table_number: Optional[str] = None
    config: Optional[dict] = None
    notes: Optional[str] = None


# ── Update ──
class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[DeviceStatusEnum] = None
    table_id: Optional[str] = None
    table_number: Optional[str] = None
    config: Optional[dict] = None
    notes: Optional[str] = None


# ── Response ──
class DeviceResponse(BaseModel):
    id: str
    branch_code: str
    name: str
    device_type: str
    token: str
    config: Optional[str] = None
    table_id: Optional[str] = None
    table_number: Optional[str] = None
    status: str
    device_fingerprint: Optional[str] = None
    session_token: Optional[str] = None
    session_expires_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ── QR Payload (what the device reads) ──
class DeviceQRPayload(BaseModel):
    """Payload encoded into QR code for device auth"""
    token: str
    branch_code: str
    device_type: str
    table_number: Optional[str] = None
    api_url: str


# ── Auth request (device sends token + fingerprint) ──
class DeviceAuthRequest(BaseModel):
    token: str
    device_fingerprint: str = Field(..., min_length=8, max_length=64,
                                     description="SHA-256 hash of browser/device info for binding")


class DeviceAuthResponse(BaseModel):
    authorized: bool
    device_id: Optional[str] = None
    device_type: Optional[str] = None
    branch_code: Optional[str] = None
    table_id: Optional[str] = None
    table_number: Optional[str] = None
    config: Optional[dict] = None
    session_token: Optional[str] = None
    session_expires_at: Optional[datetime] = None
    message: str = ""


# ── Session validation (device sends session_token) ──
class SessionValidateRequest(BaseModel):
    session_token: str
    device_fingerprint: str


class SessionValidateResponse(BaseModel):
    valid: bool
    device_id: Optional[str] = None
    device_type: Optional[str] = None
    branch_code: Optional[str] = None
    table_id: Optional[str] = None
    table_number: Optional[str] = None
    config: Optional[dict] = None
    expires_at: Optional[datetime] = None
    message: str = ""
