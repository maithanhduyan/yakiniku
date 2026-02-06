"""
Customers Router - Customer lookup and preferences
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.customer import GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference
from app.schemas.customer import CustomerCreate, CustomerResponse, PreferenceCreate, PreferenceResponse

router = APIRouter()


@router.post("/identify", response_model=CustomerResponse)
async def identify_customer(
    customer: CustomerCreate,
    branch_code: str = Query(default="hirama"),
    db: AsyncSession = Depends(get_db),
):
    """
    Identify or create customer by phone.
    Returns customer with preferences for the branch.
    """
    # Find or create global customer
    result = await db.execute(
        select(GlobalCustomer).where(GlobalCustomer.phone == customer.phone)
    )
    global_customer = result.scalar_one_or_none()

    if not global_customer:
        # Create new global customer
        global_customer = GlobalCustomer(
            phone=customer.phone,
            name=customer.name,
            email=customer.email,
        )
        db.add(global_customer)
        await db.commit()
        await db.refresh(global_customer)

    # Find or create branch customer relationship
    result = await db.execute(
        select(BranchCustomer)
        .options(selectinload(BranchCustomer.preferences))
        .where(
            BranchCustomer.global_customer_id == global_customer.id,
            BranchCustomer.branch_code == branch_code,
        )
    )
    branch_customer = result.scalar_one_or_none()

    if not branch_customer:
        branch_customer = BranchCustomer(
            global_customer_id=global_customer.id,
            branch_code=branch_code,
        )
        db.add(branch_customer)
        await db.commit()
        await db.refresh(branch_customer)
        # Reload with preferences
        result = await db.execute(
            select(BranchCustomer)
            .options(selectinload(BranchCustomer.preferences))
            .where(BranchCustomer.id == branch_customer.id)
        )
        branch_customer = result.scalar_one()

    return CustomerResponse(
        id=branch_customer.id,
        phone=global_customer.phone,
        name=global_customer.name,
        email=global_customer.email,
        visit_count=branch_customer.visit_count or 0,
        is_vip=branch_customer.is_vip or False,
        preferences=[
            PreferenceResponse(
                id=p.id,
                preference=p.preference,
                category=p.category,
                note=p.note,
                confidence=p.confidence or 1.0,
                source=p.source or "manual",
            )
            for p in (branch_customer.preferences or [])
        ],
    )


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    branch_code: str = Query(default="hirama"),
    vip_only: bool = Query(default=False),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List customers for a branch"""
    query = (
        select(BranchCustomer, GlobalCustomer)
        .join(GlobalCustomer, BranchCustomer.global_customer_id == GlobalCustomer.id)
        .options(selectinload(BranchCustomer.preferences))
        .where(BranchCustomer.branch_code == branch_code)
    )

    if vip_only:
        query = query.where(BranchCustomer.is_vip == True)

    if search:
        query = query.where(
            GlobalCustomer.name.ilike(f"%{search}%")
            | GlobalCustomer.phone.ilike(f"%{search}%")
        )

    query = query.order_by(BranchCustomer.visit_count.desc())

    result = await db.execute(query)
    rows = result.all()

    return [
        CustomerResponse(
            id=bc.id,
            phone=gc.phone,
            name=gc.name,
            email=gc.email,
            visit_count=bc.visit_count or 0,
            is_vip=bc.is_vip or False,
            preferences=[
                PreferenceResponse(
                    id=p.id,
                    preference=p.preference,
                    category=p.category,
                    note=p.note,
                    confidence=p.confidence or 1.0,
                    source=p.source or "manual",
                )
                for p in (bc.preferences or [])
            ],
        )
        for bc, gc in rows
    ]


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get customer by ID"""
    result = await db.execute(
        select(BranchCustomer, GlobalCustomer)
        .join(GlobalCustomer, BranchCustomer.global_customer_id == GlobalCustomer.id)
        .options(selectinload(BranchCustomer.preferences))
        .where(BranchCustomer.id == customer_id)
    )
    row = result.one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")

    bc, gc = row
    return CustomerResponse(
        id=bc.id,
        phone=gc.phone,
        name=gc.name,
        email=gc.email,
        visit_count=bc.visit_count or 0,
        is_vip=bc.is_vip or False,
        preferences=[
            PreferenceResponse(
                id=p.id,
                preference=p.preference,
                category=p.category,
                note=p.note,
                confidence=p.confidence or 1.0,
                source=p.source or "manual",
            )
            for p in (bc.preferences or [])
        ],
    )


@router.post("/{customer_id}/preferences", response_model=PreferenceResponse, status_code=201)
async def add_preference(
    customer_id: str,
    preference: PreferenceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a preference to customer"""
    # Check customer exists
    result = await db.execute(
        select(BranchCustomer).where(BranchCustomer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create preference
    db_preference = CustomerPreference(
        branch_customer_id=customer_id,
        preference=preference.preference,
        category=preference.category,
        note=preference.note,
        confidence=preference.confidence,
        source=preference.source,
    )

    db.add(db_preference)
    await db.commit()
    await db.refresh(db_preference)

    return PreferenceResponse(
        id=db_preference.id,
        preference=db_preference.preference,
        category=db_preference.category,
        note=db_preference.note,
        confidence=db_preference.confidence or 1.0,
        source=db_preference.source or "manual",
    )


@router.patch("/{customer_id}/vip")
async def toggle_vip(
    customer_id: str,
    is_vip: bool = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Toggle VIP status"""
    result = await db.execute(
        select(BranchCustomer).where(BranchCustomer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.is_vip = is_vip
    await db.commit()

    return {"id": customer_id, "is_vip": is_vip}

