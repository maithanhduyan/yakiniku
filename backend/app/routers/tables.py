"""
Tables Router - Table management and AI optimization API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.table import Table, TableAssignment, TableStatus, TableType
from app.models.booking import Booking
from app.services.table_optimization import TableOptimizationService


router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class TableCreate(BaseModel):
    table_number: str
    name: Optional[str] = None
    min_capacity: int = 1
    max_capacity: int
    table_type: str = "regular"
    floor: int = 1
    zone: Optional[str] = None
    has_window: bool = False
    is_smoking: bool = False
    is_wheelchair_accessible: bool = True
    has_baby_chair: bool = False
    priority: int = 0
    notes: Optional[str] = None


class TableUpdate(BaseModel):
    name: Optional[str] = None
    min_capacity: Optional[int] = None
    max_capacity: Optional[int] = None
    table_type: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    notes: Optional[str] = None


class TableResponse(BaseModel):
    id: str
    table_number: str
    name: Optional[str]
    min_capacity: int
    max_capacity: int
    table_type: str
    floor: int
    zone: Optional[str]
    status: str
    is_active: bool
    features: dict

    class Config:
        from_attributes = True


class SlotSummaryResponse(BaseModel):
    time_slot: str
    total_tables: int
    available_tables: int
    occupied_tables: int
    total_capacity: int
    used_capacity: int
    available_capacity: int
    utilization_rate: float


class InsightResponse(BaseModel):
    type: str
    title: str
    message: str
    priority: int
    action: Optional[str]
    data: Optional[dict]


# ============================================
# TABLE CRUD
# ============================================

@router.get("/", response_model=List[TableResponse])
async def list_tables(
    branch_code: str = Query(default="hirama"),
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    """List all tables for a branch"""
    query = select(Table).where(Table.branch_code == branch_code)

    if not include_inactive:
        query = query.where(Table.is_active == True)

    query = query.order_by(Table.floor, Table.zone, Table.table_number)

    result = await db.execute(query)
    tables = result.scalars().all()

    return [
        TableResponse(
            id=t.id,
            table_number=t.table_number,
            name=t.name,
            min_capacity=t.min_capacity,
            max_capacity=t.max_capacity,
            table_type=t.table_type,
            floor=t.floor,
            zone=t.zone,
            status=t.status,
            is_active=t.is_active,
            features={
                "has_window": t.has_window,
                "is_smoking": t.is_smoking,
                "is_wheelchair_accessible": t.is_wheelchair_accessible,
                "has_baby_chair": t.has_baby_chair,
            }
        )
        for t in tables
    ]


@router.post("/", response_model=TableResponse, status_code=201)
async def create_table(
    table: TableCreate,
    branch_code: str = Query(default="hirama"),
    db: AsyncSession = Depends(get_db),
):
    """Create a new table"""
    # Check for duplicate table number
    existing = await db.execute(
        select(Table).where(
            and_(
                Table.branch_code == branch_code,
                Table.table_number == table.table_number
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Table number already exists")

    db_table = Table(
        branch_code=branch_code,
        table_number=table.table_number,
        name=table.name,
        min_capacity=table.min_capacity,
        max_capacity=table.max_capacity,
        table_type=table.table_type,
        floor=table.floor,
        zone=table.zone,
        has_window=table.has_window,
        is_smoking=table.is_smoking,
        is_wheelchair_accessible=table.is_wheelchair_accessible,
        has_baby_chair=table.has_baby_chair,
        priority=table.priority,
        notes=table.notes,
    )

    db.add(db_table)
    await db.commit()
    await db.refresh(db_table)

    return TableResponse(
        id=db_table.id,
        table_number=db_table.table_number,
        name=db_table.name,
        min_capacity=db_table.min_capacity,
        max_capacity=db_table.max_capacity,
        table_type=db_table.table_type,
        floor=db_table.floor,
        zone=db_table.zone,
        status=db_table.status,
        is_active=db_table.is_active,
        features={
            "has_window": db_table.has_window,
            "is_smoking": db_table.is_smoking,
            "is_wheelchair_accessible": db_table.is_wheelchair_accessible,
            "has_baby_chair": db_table.has_baby_chair,
        }
    )


@router.patch("/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: str,
    update: TableUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a table"""
    result = await db.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    if update.name is not None:
        table.name = update.name
    if update.min_capacity is not None:
        table.min_capacity = update.min_capacity
    if update.max_capacity is not None:
        table.max_capacity = update.max_capacity
    if update.table_type is not None:
        table.table_type = update.table_type
    if update.status is not None:
        table.status = update.status
    if update.is_active is not None:
        table.is_active = update.is_active
    if update.priority is not None:
        table.priority = update.priority
    if update.notes is not None:
        table.notes = update.notes

    await db.commit()
    await db.refresh(table)

    return TableResponse(
        id=table.id,
        table_number=table.table_number,
        name=table.name,
        min_capacity=table.min_capacity,
        max_capacity=table.max_capacity,
        table_type=table.table_type,
        floor=table.floor,
        zone=table.zone,
        status=table.status,
        is_active=table.is_active,
        features={
            "has_window": table.has_window,
            "is_smoking": table.is_smoking,
            "is_wheelchair_accessible": table.is_wheelchair_accessible,
            "has_baby_chair": table.has_baby_chair,
        }
    )


@router.delete("/{table_id}", status_code=204)
async def delete_table(
    table_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a table (soft delete - sets is_active=False)"""
    result = await db.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table.is_active = False
    await db.commit()


# ============================================
# AI OPTIMIZATION ENDPOINTS
# ============================================

@router.get("/optimization/summary", response_model=List[SlotSummaryResponse])
async def get_slot_summary(
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Get utilization summary for all time slots"""
    if target_date is None:
        target_date = date.today()

    optimizer = TableOptimizationService(db, branch_code)
    summaries = await optimizer.get_time_slot_summary(target_date)

    return [
        SlotSummaryResponse(
            time_slot=s.time_slot,
            total_tables=s.total_tables,
            available_tables=s.available_tables,
            occupied_tables=s.occupied_tables,
            total_capacity=s.total_capacity,
            used_capacity=s.used_capacity,
            available_capacity=s.available_capacity,
            utilization_rate=s.utilization_rate,
        )
        for s in summaries
    ]


@router.get("/optimization/insights", response_model=List[InsightResponse])
async def get_ai_insights(
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated insights and suggestions"""
    if target_date is None:
        target_date = date.today()

    optimizer = TableOptimizationService(db, branch_code)
    insights = await optimizer.generate_insights(target_date)

    return [
        InsightResponse(
            type=i.type,
            title=i.title,
            message=i.message,
            priority=i.priority,
            action=i.action,
            data=i.data,
        )
        for i in insights
    ]


@router.get("/optimization/check")
async def check_table_availability(
    branch_code: str = Query(default="hirama"),
    booking_date: date = Query(...),
    time_slot: str = Query(...),
    guests: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Check if tables are available and get suggestions"""
    optimizer = TableOptimizationService(db, branch_code)
    result = await optimizer.check_availability(guests, booking_date, time_slot)

    return {
        "available": result["available"],
        "message": result["message"],
        "suggestions": [
            {
                "table_number": t.table_number,
                "capacity": t.capacity,
                "score": t.score,
                "reason": t.reason,
                "waste": t.waste,
            }
            for t in result["tables"]
        ],
        "alternatives": [
            {
                "time": a["time"],
                "diff_minutes": a["diff_minutes"],
            }
            for a in result.get("alternatives", [])
        ]
    }


@router.post("/optimization/assign/{booking_id}")
async def assign_table_to_booking(
    booking_id: str,
    table_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Assign a table to a booking (manual or auto)"""
    # Get booking
    booking_result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = booking_result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    optimizer = TableOptimizationService(db, booking.branch_code)

    if table_id:
        # Manual assignment
        assignment = await optimizer.reassign_table(booking_id, table_id, "Manual assignment")
    else:
        # Auto assignment
        assignment = await optimizer.auto_assign_table(
            booking_id,
            booking.guests,
            booking.date,
            booking.time
        )

    if not assignment:
        raise HTTPException(status_code=400, detail="No suitable table found")

    # Get table info
    table_result = await db.execute(
        select(Table).where(Table.id == assignment.table_id)
    )
    table = table_result.scalar_one_or_none()

    return {
        "success": True,
        "assignment_id": assignment.id,
        "table": {
            "id": table.id,
            "table_number": table.table_number,
            "capacity": table.max_capacity,
        } if table else None,
        "notes": assignment.notes,
    }


# ============================================
# SEED DATA FOR TESTING
# ============================================

@router.post("/seed", status_code=201)
async def seed_tables(
    branch_code: str = Query(default="hirama"),
    db: AsyncSession = Depends(get_db),
):
    """
    Seed sample tables for testing.
    Creates 8 tables: 4x 4-seat, 3x 6-seat, 1x 8-seat VIP
    """
    # Check if already seeded
    existing = await db.execute(
        select(Table).where(Table.branch_code == branch_code).limit(1)
    )
    if existing.scalar_one_or_none():
        return {"message": "Tables already exist", "seeded": False}

    tables_config = [
        # 4-seat regular tables
        {"table_number": "A1", "name": "çª“éš›å¸­A", "max_capacity": 4, "zone": "A", "has_window": True},
        {"table_number": "A2", "name": "çª“éš›å¸­B", "max_capacity": 4, "zone": "A", "has_window": True},
        {"table_number": "B1", "name": "ä¸­å¤®å¸­A", "max_capacity": 4, "zone": "B"},
        {"table_number": "B2", "name": "ä¸­å¤®å¸­B", "max_capacity": 4, "zone": "B"},
        # 6-seat tables
        {"table_number": "C1", "name": "ã‚°ãƒ«ãƒ¼ãƒ—å¸­A", "max_capacity": 6, "zone": "C"},
        {"table_number": "C2", "name": "ã‚°ãƒ«ãƒ¼ãƒ—å¸­B", "max_capacity": 6, "zone": "C"},
        {"table_number": "C3", "name": "ã‚°ãƒ«ãƒ¼ãƒ—å¸­C", "max_capacity": 6, "zone": "C"},
        # VIP room
        {"table_number": "VIP1", "name": "å€‹å®¤", "max_capacity": 8, "zone": "VIP",
         "table_type": "private", "priority": 10},
    ]

    created = []
    for config in tables_config:
        table = Table(
            branch_code=branch_code,
            table_number=config["table_number"],
            name=config.get("name"),
            min_capacity=1,
            max_capacity=config["max_capacity"],
            table_type=config.get("table_type", "regular"),
            floor=1,
            zone=config.get("zone"),
            has_window=config.get("has_window", False),
            priority=config.get("priority", 0),
        )
        db.add(table)
        created.append(config["table_number"])

    await db.commit()

    return {
        "message": f"Created {len(created)} tables",
        "seeded": True,
        "tables": created,
    }

