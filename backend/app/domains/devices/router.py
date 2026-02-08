"""
Device Management Router
Team: dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import json

from app.database import get_db
from app.domains.devices.models import Device, DeviceStatus
from app.models.branch import Branch
from app.domains.devices.schemas import (
    DeviceCreate, DeviceUpdate, DeviceResponse,
    DeviceAuthRequest, DeviceAuthResponse,
    SessionValidateRequest, SessionValidateResponse,
)

router = APIRouter()

# Session duration: 1 year
SESSION_DURATION_DAYS = 365


def generate_token() -> str:
    """Generate a secure 32-byte hex token for device auth"""
    return secrets.token_hex(32)


# ── List devices ──
@router.get("/")
async def list_devices(
    branch_code: str = "hirama",
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all devices for a branch"""
    query = select(Device).where(Device.branch_code == branch_code)

    if device_type:
        query = query.where(Device.device_type == device_type)
    if status:
        query = query.where(Device.status == status)

    query = query.order_by(Device.device_type, Device.name)
    result = await db.execute(query)
    devices = result.scalars().all()

    # Resolve branch name
    branch_name = await _resolve_branch_name(db, branch_code)

    return {
        "devices": [_device_to_dict(d, branch_name=branch_name) for d in devices],
        "total": len(devices),
    }


# ── Get single device ──
@router.get("/{device_id}")
async def get_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get device details by ID"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    branch_name = await _resolve_branch_name(db, device.branch_code)
    return _device_to_dict(device, branch_name=branch_name)


# ── Create device ──
@router.post("/")
async def create_device(
    data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new device and generate auth token"""
    token = generate_token()

    device = Device(
        branch_code=data.branch_code,
        name=data.name,
        device_type=data.device_type.value,
        token=token,
        table_id=data.table_id,
        table_number=data.table_number,
        config=json.dumps(data.config or {}),
        status=DeviceStatus.PENDING.value,
        notes=data.notes,
    )

    db.add(device)
    await db.commit()
    await db.refresh(device)

    branch_name = await _resolve_branch_name(db, device.branch_code)
    return _device_to_dict(device, branch_name=branch_name)


# ── Update device ──
@router.patch("/{device_id}")
async def update_device(
    device_id: str,
    data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update device settings"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if data.name is not None:
        device.name = data.name
    if data.status is not None:
        device.status = data.status.value
    if data.table_id is not None:
        device.table_id = data.table_id
    if data.table_number is not None:
        device.table_number = data.table_number
    if data.config is not None:
        device.config = json.dumps(data.config)
    if data.notes is not None:
        device.notes = data.notes

    await db.commit()
    await db.refresh(device)

    branch_name = await _resolve_branch_name(db, device.branch_code)
    return _device_to_dict(device, branch_name=branch_name)


# ── Delete device ──
@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove a device"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    await db.delete(device)
    await db.commit()

    return {"ok": True, "message": f"Device '{device.name}' deleted"}


# ── Regenerate token ──
@router.post("/{device_id}/regenerate-token")
async def regenerate_token(
    device_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Regenerate auth token (invalidates old QR code)"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.token = generate_token()
    device.status = DeviceStatus.PENDING.value
    device.activated_at = None
    # Clear session binding — device must re-auth with new QR
    device.session_token = None
    device.session_expires_at = None
    device.device_fingerprint = None

    await db.commit()
    await db.refresh(device)

    branch_name = await _resolve_branch_name(db, device.branch_code)
    return _device_to_dict(device, branch_name=branch_name)


# ── Device auth (called by devices when scanning QR) ──
@router.post("/auth")
async def authenticate_device(
    data: DeviceAuthRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Device sends token + fingerprint from QR code to authenticate.
    Binds fingerprint on first auth. Rejects if different fingerprint tries same token.
    Returns session_token (valid 1 year) for subsequent requests.
    """
    result = await db.execute(
        select(Device).where(Device.token == data.token)
    )
    device = result.scalar_one_or_none()

    if not device:
        return DeviceAuthResponse(
            authorized=False,
            message="無効なトークンです。管理者にお問い合わせください。",
        )

    if device.status == DeviceStatus.INACTIVE.value:
        return DeviceAuthResponse(
            authorized=False,
            message="この端末は無効化されています。",
        )

    # ── Fingerprint binding: 1 QR = 1 device only ──
    if device.device_fingerprint and device.device_fingerprint != data.device_fingerprint:
        return DeviceAuthResponse(
            authorized=False,
            message="このQRコードは別の端末で使用されています。管理者にお問い合わせください。",
        )

    now = datetime.now(timezone.utc)

    # Bind fingerprint on first auth
    if not device.device_fingerprint:
        device.device_fingerprint = data.device_fingerprint

    # Generate session token (or reuse if still valid)
    if not device.session_token or not device.session_expires_at or device.session_expires_at < now:
        device.session_token = secrets.token_hex(32)
        device.session_expires_at = now + timedelta(days=SESSION_DURATION_DAYS)

    # Activate on first auth
    if device.status == DeviceStatus.PENDING.value:
        device.status = DeviceStatus.ACTIVE.value
        device.activated_at = now

    device.last_seen_at = now
    await db.commit()

    # Parse config
    try:
        config = json.loads(device.config) if device.config else {}
    except (json.JSONDecodeError, TypeError):
        config = {}

    return DeviceAuthResponse(
        authorized=True,
        device_id=device.id,
        device_type=device.device_type,
        branch_code=device.branch_code,
        table_id=device.table_id,
        table_number=device.table_number,
        config=config,
        session_token=device.session_token,
        session_expires_at=device.session_expires_at,
        message="認証成功",
    )


# ── Session validation (called on app boot to check saved session) ──
@router.post("/session/validate")
async def validate_session(
    data: SessionValidateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Device sends saved session_token + fingerprint to validate.
    Used on app startup to skip QR re-scan.
    """
    result = await db.execute(
        select(Device).where(Device.session_token == data.session_token)
    )
    device = result.scalar_one_or_none()

    if not device:
        return SessionValidateResponse(valid=False, message="セッションが見つかりません")

    if device.status == DeviceStatus.INACTIVE.value:
        return SessionValidateResponse(valid=False, message="この端末は無効化されています")

    if device.device_fingerprint != data.device_fingerprint:
        return SessionValidateResponse(valid=False, message="別の端末からのアクセスです")

    now = datetime.now(timezone.utc)
    if device.session_expires_at and device.session_expires_at < now:
        return SessionValidateResponse(valid=False, message="セッションの有効期限が切れています")

    # Update last seen
    device.last_seen_at = now
    await db.commit()

    # Parse config
    try:
        config = json.loads(device.config) if device.config else {}
    except (json.JSONDecodeError, TypeError):
        config = {}

    return SessionValidateResponse(
        valid=True,
        device_id=device.id,
        device_type=device.device_type,
        branch_code=device.branch_code,
        table_id=device.table_id,
        table_number=device.table_number,
        config=config,
        expires_at=device.session_expires_at,
        message="セッション有効",
    )


# ── Logout device (called from dashboard) ──
@router.post("/{device_id}/logout")
async def logout_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Dashboard admin logs out a device — clears session + fingerprint.
    Device must re-scan QR to auth again.
    """
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.session_token = None
    device.session_expires_at = None
    device.device_fingerprint = None
    device.status = DeviceStatus.PENDING.value

    await db.commit()
    await db.refresh(device)

    branch_name = await _resolve_branch_name(db, device.branch_code)
    return {"ok": True, "message": f"Device '{device.name}' logged out", "device": _device_to_dict(device, branch_name=branch_name)}


# ── Helpers ──
async def _resolve_branch_name(db: AsyncSession, branch_code: str) -> Optional[str]:
    """Look up branch name from code"""
    result = await db.execute(
        select(Branch.name).where(Branch.code == branch_code)
    )
    return result.scalar_one_or_none()


def _device_to_dict(device: Device, *, branch_name: Optional[str] = None) -> dict:
    """Convert Device model to dict for JSON response"""
    return {
        "id": device.id,
        "branch_code": device.branch_code,
        "branch_name": branch_name or device.branch_code,
        "name": device.name,
        "device_type": device.device_type,
        "token": device.token,
        "config": device.config,
        "table_id": device.table_id,
        "table_number": device.table_number,
        "status": device.status,
        "device_fingerprint": device.device_fingerprint,
        "has_session": bool(device.session_token),
        "session_expires_at": device.session_expires_at.isoformat() if device.session_expires_at else None,
        "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
        "activated_at": device.activated_at.isoformat() if device.activated_at else None,
        "created_at": device.created_at.isoformat() if device.created_at else None,
        "updated_at": device.updated_at.isoformat() if device.updated_at else None,
        "created_by": device.created_by,
        "notes": device.notes,
    }
