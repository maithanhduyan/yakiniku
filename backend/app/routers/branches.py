"""
Branches Router - Branch management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchResponse

router = APIRouter()


@router.get("/", response_model=List[BranchResponse])
async def list_branches(
    db: AsyncSession = Depends(get_db),
):
    """List all active branches"""
    result = await db.execute(
        select(Branch).where(Branch.is_active == True).order_by(Branch.code)
    )
    branches = result.scalars().all()

    return [
        BranchResponse(
            id=b.id,
            code=b.code,
            name=b.name,
            subdomain=b.subdomain,
            phone=b.phone,
            address=b.address,
            theme_primary_color=b.theme_primary_color or "#d4af37",
            theme_bg_color=b.theme_bg_color or "#1a1a1a",
            opening_time=str(b.opening_time) if b.opening_time else "17:00",
            closing_time=str(b.closing_time) if b.closing_time else "23:00",
            closed_days=b.closed_days or [2],
            max_capacity=b.max_capacity or 30,
            features=b.features or {},
            is_active=b.is_active,
        )
        for b in branches
    ]


@router.get("/{branch_code}", response_model=BranchResponse)
async def get_branch(
    branch_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Get branch by code"""
    result = await db.execute(select(Branch).where(Branch.code == branch_code))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    return BranchResponse(
        id=branch.id,
        code=branch.code,
        name=branch.name,
        subdomain=branch.subdomain,
        phone=branch.phone,
        address=branch.address,
        theme_primary_color=branch.theme_primary_color or "#d4af37",
        theme_bg_color=branch.theme_bg_color or "#1a1a1a",
        opening_time=str(branch.opening_time) if branch.opening_time else "17:00",
        closing_time=str(branch.closing_time) if branch.closing_time else "23:00",
        closed_days=branch.closed_days or [2],
        max_capacity=branch.max_capacity or 30,
        features=branch.features or {},
        is_active=branch.is_active,
    )


@router.post("/", response_model=BranchResponse, status_code=201)
async def create_branch(
    branch: BranchCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new branch"""
    # Check if code already exists
    existing = await db.execute(select(Branch).where(Branch.code == branch.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Branch code already exists")

    db_branch = Branch(
        code=branch.code,
        name=branch.name,
        subdomain=branch.subdomain or branch.code,
        phone=branch.phone,
        address=branch.address,
        theme_primary_color=branch.theme_primary_color,
        theme_bg_color=branch.theme_bg_color,
        closed_days=branch.closed_days,
        max_capacity=branch.max_capacity,
    )

    db.add(db_branch)
    await db.commit()
    await db.refresh(db_branch)

    return BranchResponse(
        id=db_branch.id,
        code=db_branch.code,
        name=db_branch.name,
        subdomain=db_branch.subdomain,
        phone=db_branch.phone,
        address=db_branch.address,
        theme_primary_color=db_branch.theme_primary_color or "#d4af37",
        theme_bg_color=db_branch.theme_bg_color or "#1a1a1a",
        opening_time=str(db_branch.opening_time) if db_branch.opening_time else "17:00",
        closing_time=str(db_branch.closing_time) if db_branch.closing_time else "23:00",
        closed_days=db_branch.closed_days or [2],
        max_capacity=db_branch.max_capacity or 30,
        features=db_branch.features or {},
        is_active=db_branch.is_active,
    )


@router.post("/seed")
async def seed_default_branch(
    db: AsyncSession = Depends(get_db),
):
    """Seed default Hirama branch"""
    existing = await db.execute(select(Branch).where(Branch.code == "hirama"))
    if existing.scalar_one_or_none():
        return {"message": "Default branch already exists"}

    hirama = Branch(
        code="hirama",
        name="Yakiniku 平間本店",
        subdomain="hirama",
        phone="044-789-8413",
        address="〒211-0013 神奈川県川崎市中原区上平間XXXX",
        theme_primary_color="#d4af37",
        theme_bg_color="#1a1a1a",
        closed_days=[2],
        max_capacity=30,
        features={
            "chat": True,
            "ai_booking": True,
            "customer_insights": True,
        },
    )

    db.add(hirama)
    await db.commit()

    return {"message": "Default branch created", "code": "hirama"}
