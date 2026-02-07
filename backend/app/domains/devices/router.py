"""
Device Management Router
Team: dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import Optional
import secrets
import json

from app.database import get_db
from app.domains.devices.models import Device, DeviceStatus
from app.domains.devices.schemas import (
    DeviceCreate, DeviceUpdate, DeviceResponse,
    DeviceAuthRequest, DeviceAuthResponse
)

router = APIRouter()


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

    return {
        "devices": [_device_to_dict(d) for d in devices],
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

    return _device_to_dict(device)


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

    return _device_to_dict(device)


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

    return _device_to_dict(device)


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

    await db.commit()
    await db.refresh(device)

    return _device_to_dict(device)


# ── Device auth (called by devices when scanning QR) ──
@router.post("/auth")
async def authenticate_device(
    data: DeviceAuthRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Device sends token from QR code to authenticate.
    Returns device config if authorized.
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

    # Activate on first auth
    now = datetime.utcnow()
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
        message="認証成功",
    )


# ── Helper ──
def _device_to_dict(device: Device) -> dict:
    """Convert Device model to dict for JSON response"""
    return {
        "id": device.id,
        "branch_code": device.branch_code,
        "name": device.name,
        "device_type": device.device_type,
        "token": device.token,
        "config": device.config,
        "table_id": device.table_id,
        "table_number": device.table_number,
        "status": device.status,
        "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
        "activated_at": device.activated_at.isoformat() if device.activated_at else None,
        "created_at": device.created_at.isoformat() if device.created_at else None,
        "updated_at": device.updated_at.isoformat() if device.updated_at else None,
        "created_by": device.created_by,
        "notes": device.notes,
    }
