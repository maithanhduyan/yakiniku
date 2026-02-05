"""
Dashboard Router - Staff management interface
HTMX-powered for real-time updates
"""
from fastapi import APIRouter, Depends, Request, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.booking import Booking
from app.models.customer import GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference

router = APIRouter()

# Templates - relative to backend folder
templates = Jinja2Templates(directory="../dashboard/templates")


# ============================================
# MAIN DASHBOARD
# ============================================
@router.get("/", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
):
    """Main dashboard with today's overview"""
    today = date.today()

    # Get today's bookings
    result = await db.execute(
        select(Booking)
        .where(
            Booking.branch_code == branch_code,
            Booking.date == today
        )
        .order_by(Booking.time)
    )
    today_bookings = result.scalars().all()

    # Get upcoming bookings (next 7 days)
    result = await db.execute(
        select(Booking)
        .where(
            Booking.branch_code == branch_code,
            Booking.date > today,
            Booking.date <= today + timedelta(days=7)
        )
        .order_by(Booking.date, Booking.time)
    )
    upcoming_bookings = result.scalars().all()

    # Stats
    total_guests_today = sum(b.guests for b in today_bookings)
    confirmed_count = sum(1 for b in today_bookings if b.status == "confirmed")
    pending_count = sum(1 for b in today_bookings if b.status == "pending")

    return templates.TemplateResponse("dashboard/home.html", {
        "request": request,
        "active": "home",
        "today": today,
        "today_bookings": today_bookings,
        "upcoming_bookings": upcoming_bookings,
        "stats": {
            "total_bookings": len(today_bookings),
            "total_guests": total_guests_today,
            "confirmed": confirmed_count,
            "pending": pending_count,
        },
        "branch_code": branch_code,
    })


# ============================================
# BOOKINGS MANAGEMENT
# ============================================
@router.get("/bookings", response_class=HTMLResponse)
async def bookings_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    booking_date: Optional[str] = None,
    status: Optional[str] = None,
):
    """Bookings list with filters"""
    query = select(Booking).where(Booking.branch_code == branch_code)

    # Date filter
    filter_date = date.today()
    if booking_date:
        try:
            filter_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    query = query.where(Booking.date == filter_date)

    if status:
        query = query.where(Booking.status == status)

    query = query.order_by(Booking.time)

    result = await db.execute(query)
    bookings = result.scalars().all()

    return templates.TemplateResponse("dashboard/bookings.html", {
        "request": request,
        "active": "bookings",
        "bookings": bookings,
        "filter_date": filter_date,
        "filter_status": status,
        "branch_code": branch_code,
    })


@router.get("/bookings/{booking_id}", response_class=HTMLResponse)
async def booking_detail(
    request: Request,
    booking_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Booking detail modal content"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        return HTMLResponse("<p>äºˆç´„ãŒè¦‹ã¤ã‹ã‚Šã¾ã›ã‚“</p>", status_code=404)

    # Get customer info if exists
    customer = None
    if booking.guest_phone:
        result = await db.execute(
            select(GlobalCustomer).where(GlobalCustomer.phone == booking.guest_phone)
        )
        customer = result.scalar_one_or_none()

    return templates.TemplateResponse("dashboard/partials/booking_detail.html", {
        "request": request,
        "booking": booking,
        "customer": customer,
    })


@router.put("/bookings/{booking_id}/status", response_class=HTMLResponse)
async def update_booking_status(
    request: Request,
    booking_id: str,
    status: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Update booking status (HTMX)"""
    from app.services.notification_service import notify_booking_confirmed, notify_booking_cancelled

    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        return HTMLResponse("<p>ã‚¨ãƒ©ãƒ¼</p>", status_code=404)

    old_status = booking.status
    booking.status = status
    await db.commit()
    await db.refresh(booking)

    # Send notification for status change
    if status == "confirmed" and old_status != "confirmed":
        await notify_booking_confirmed(
            branch_code=booking.branch_code,
            guest_name=booking.guest_name or "ã‚²ã‚¹ãƒˆ",
            booking_date=booking.date.isoformat(),
            booking_time=booking.time,
            booking_id=booking.id,
        )
    elif status == "cancelled" and old_status != "cancelled":
        await notify_booking_cancelled(
            branch_code=booking.branch_code,
            guest_name=booking.guest_name or "ã‚²ã‚¹ãƒˆ",
            booking_date=booking.date.isoformat(),
            booking_time=booking.time,
            booking_id=booking.id,
        )

    return templates.TemplateResponse("dashboard/partials/booking_row.html", {
        "request": request,
        "booking": booking,
    })


@router.put("/bookings/{booking_id}/note", response_class=HTMLResponse)
async def update_booking_note(
    request: Request,
    booking_id: str,
    staff_note: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Update staff note on booking"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if booking:
        booking.staff_note = staff_note
        await db.commit()

    return HTMLResponse(f'<span class="text-green-400">âœ“ ä¿å­˜ã—ã¾ã—ãŸ</span>')


# ============================================
# CUSTOMER INSIGHTS
# ============================================
@router.get("/customers", response_class=HTMLResponse)
async def customers_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    search: Optional[str] = None,
    id: Optional[str] = Query(default=None),
):
    """Customer list with search. If id is provided, show customer detail."""
    # If id is provided, redirect to customer detail
    if id:
        return await customer_detail(request, id, db, branch_code)
    query = (
        select(BranchCustomer)
        .options(
            selectinload(BranchCustomer.global_customer),
            selectinload(BranchCustomer.preferences)
        )
        .where(BranchCustomer.branch_code == branch_code)
    )

    if search:
        # Search by phone or name via global_customer
        query = query.join(GlobalCustomer).where(
            (GlobalCustomer.phone.ilike(f"%{search}%")) |
            (GlobalCustomer.name.ilike(f"%{search}%"))
        )

    query = query.order_by(BranchCustomer.visit_count.desc())

    result = await db.execute(query)
    customers = result.scalars().all()

    return templates.TemplateResponse("dashboard/customers.html", {
        "request": request,
        "active": "customers",
        "customers": customers,
        "search": search,
        "branch_code": branch_code,
    })


@router.get("/customers/{customer_id}", response_class=HTMLResponse)
async def customer_detail(
    request: Request,
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
):
    """Customer detail with history"""
    # Get branch customer
    result = await db.execute(
        select(BranchCustomer)
        .options(
            selectinload(BranchCustomer.global_customer),
            selectinload(BranchCustomer.preferences)
        )
        .where(BranchCustomer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        return HTMLResponse("<p>é¡§å®¢ãŒè¦‹ã¤ã‹ã‚Šã¾ã›ã‚“</p>", status_code=404)

    # Get booking history
    result = await db.execute(
        select(Booking)
        .where(Booking.guest_phone == customer.global_customer.phone)
        .order_by(Booking.date.desc())
        .limit(10)
    )
    bookings = result.scalars().all()

    return templates.TemplateResponse("dashboard/partials/customer_detail.html", {
        "request": request,
        "customer": customer,
        "bookings": bookings,
    })


@router.post("/customers/{customer_id}/preference", response_class=HTMLResponse)
async def add_customer_preference(
    request: Request,
    customer_id: str,
    preference: str = Form(...),
    category: str = Form(default="meat"),
    note: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
):
    """Add preference to customer"""
    new_pref = CustomerPreference(
        branch_customer_id=customer_id,
        preference=preference,
        category=category,
        note=note,
        source="dashboard",
        confidence=1.0,
    )
    db.add(new_pref)
    await db.commit()

    return templates.TemplateResponse("dashboard/partials/preference_tag.html", {
        "request": request,
        "pref": new_pref,
    })


@router.put("/customers/{customer_id}/vip", response_class=HTMLResponse)
async def toggle_vip_status(
    request: Request,
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Toggle VIP status"""
    result = await db.execute(
        select(BranchCustomer).where(BranchCustomer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if customer:
        customer.is_vip = not customer.is_vip
        await db.commit()

        status = "VIP ã«è¨­å®šã—ã¾ã—ãŸ â­" if customer.is_vip else "VIP ã‚’è§£é™¤ã—ã¾ã—ãŸ"
        return HTMLResponse(f'<span class="text-primary">{status}</span>')

    return HTMLResponse("<span>ã‚¨ãƒ©ãƒ¼</span>", status_code=404)


# ============================================
# QUICK SEARCH (HTMX)
# ============================================
@router.get("/search", response_class=HTMLResponse)
async def quick_search(
    request: Request,
    q: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
):
    """Quick search for customers by phone/name"""
    if len(q) < 2:
        return HTMLResponse("")

    result = await db.execute(
        select(GlobalCustomer)
        .where(
            (GlobalCustomer.phone.ilike(f"%{q}%")) |
            (GlobalCustomer.name.ilike(f"%{q}%"))
        )
        .limit(5)
    )
    customers = result.scalars().all()

    return templates.TemplateResponse("dashboard/partials/search_results.html", {
        "request": request,
        "customers": customers,
        "query": q,
    })


# ============================================
# TABLE MANAGEMENT (Dashboard Views)
# ============================================

@router.get("/tables", response_class=HTMLResponse)
async def tables_management(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
):
    """Table management with AI insights"""
    from app.models.table import Table
    from app.services.table_optimization import TableOptimizationService

    if target_date is None:
        target_date = date.today()

    # Get tables
    result = await db.execute(
        select(Table)
        .where(Table.branch_code == branch_code)
        .order_by(Table.zone, Table.table_number)
    )
    tables = result.scalars().all()

    # Convert to response format
    tables_data = [
        {
            "id": t.id,
            "table_number": t.table_number,
            "name": t.name,
            "max_capacity": t.max_capacity,
            "table_type": t.table_type,
            "zone": t.zone,
            "status": t.status,
            "is_active": t.is_active,
            "features": {
                "has_window": t.has_window,
                "has_baby_chair": t.has_baby_chair,
            }
        }
        for t in tables
    ]

    # Get AI insights
    insights = []
    slot_summaries = []
    gantt_data = {"tables": [], "time_slots": [], "unassigned_bookings": []}
    if tables:
        try:
            optimizer = TableOptimizationService(db, branch_code)
            insights_raw = await optimizer.generate_insights(target_date)
            insights = [
                {
                    "type": i.type,
                    "title": i.title,
                    "message": i.message,
                    "priority": i.priority,
                    "action": i.action,
                }
                for i in insights_raw
            ]

            summaries_raw = await optimizer.get_time_slot_summary(target_date)
            slot_summaries = [
                {
                    "time_slot": s.time_slot,
                    "total_tables": s.total_tables,
                    "available_tables": s.available_tables,
                    "utilization_rate": s.utilization_rate,
                }
                for s in summaries_raw
            ]

            # Get Gantt chart data
            gantt_data = await optimizer.get_gantt_data(target_date)
        except Exception as e:
            print(f"Error generating insights: {e}")
            import traceback
            traceback.print_exc()

    # Stats
    total_capacity = sum(t.max_capacity for t in tables)
    tables_4_seat = sum(1 for t in tables if t.max_capacity == 4)
    tables_6_seat = sum(1 for t in tables if t.max_capacity >= 6)

    return templates.TemplateResponse("dashboard/tables.html", {
        "request": request,
        "active": "tables",
        "tables": tables_data,
        "insights": insights,
        "slot_summaries": slot_summaries,
        "gantt_data": gantt_data,
        "target_date": target_date,
        "branch_code": branch_code,
        "total_tables": len(tables),
        "total_capacity": total_capacity,
        "tables_4_seat": tables_4_seat,
        "tables_6_seat": tables_6_seat,
    })


@router.get("/tables/gantt", response_class=HTMLResponse)
async def get_gantt_partial(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
):
    """Get Gantt chart as HTMX partial for real-time updates"""
    from app.models.table import Table
    from app.services.table_optimization import TableOptimizationService

    if target_date is None:
        target_date = date.today()

    # Get tables
    result = await db.execute(
        select(Table)
        .where(Table.branch_code == branch_code)
        .order_by(Table.zone, Table.table_number)
    )
    tables = result.scalars().all()

    # Get Gantt data
    gantt_data = {"tables": [], "time_slots": [], "unassigned_bookings": []}
    if tables:
        try:
            optimizer = TableOptimizationService(db, branch_code)
            gantt_data = await optimizer.get_gantt_data(target_date)
        except Exception as e:
            print(f"Error getting gantt data: {e}")

    return templates.TemplateResponse("dashboard/partials/gantt.html", {
        "request": request,
        "gantt_data": gantt_data,
        "target_date": target_date,
        "branch_code": branch_code,
    })


@router.get("/tables/insights", response_class=HTMLResponse)
async def get_table_insights_partial(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    target_date: date = Query(default=None),
):
    """Get AI insights as HTMX partial"""
    from app.services.table_optimization import TableOptimizationService

    if target_date is None:
        target_date = date.today()

    optimizer = TableOptimizationService(db, branch_code)
    insights_raw = await optimizer.generate_insights(target_date)
    insights = [
        {
            "type": i.type,
            "title": i.title,
            "message": i.message,
            "priority": i.priority,
            "action": i.action,
        }
        for i in insights_raw
    ]

    return templates.TemplateResponse("dashboard/partials/insights.html", {
        "request": request,
        "insights": insights,
    })


@router.post("/tables/seed", response_class=HTMLResponse)
async def seed_tables_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
):
    """Seed sample tables via dashboard"""
    from app.models.table import Table

    # Check if already seeded
    existing = await db.execute(
        select(Table).where(Table.branch_code == branch_code).limit(1)
    )
    if existing.scalar_one_or_none():
        return HTMLResponse('<div class="text-yellow-400 p-4">ãƒ†ãƒ¼ãƒ–ãƒ«ã¯æ—¢ã«è¨­å®šã•ã‚Œã¦ã„ã¾ã™ã€‚ãƒšãƒ¼ã‚¸ã‚’æ›´æ–°ã—ã¦ãã ã•ã„ã€‚</div>')

    tables_config = [
        {"table_number": "A1", "name": "çª“éš›å¸­A", "max_capacity": 4, "zone": "A", "has_window": True},
        {"table_number": "A2", "name": "çª“éš›å¸­B", "max_capacity": 4, "zone": "A", "has_window": True},
        {"table_number": "B1", "name": "ä¸­å¤®å¸­A", "max_capacity": 4, "zone": "B"},
        {"table_number": "B2", "name": "ä¸­å¤®å¸­B", "max_capacity": 4, "zone": "B"},
        {"table_number": "C1", "name": "ã‚°ãƒ«ãƒ¼ãƒ—å¸­A", "max_capacity": 6, "zone": "C"},
        {"table_number": "C2", "name": "ã‚°ãƒ«ãƒ¼ãƒ—å¸­B", "max_capacity": 6, "zone": "C"},
        {"table_number": "C3", "name": "ã‚°ãƒ«ãƒ¼ãƒ—å¸­C", "max_capacity": 6, "zone": "C"},
        {"table_number": "VIP1", "name": "å€‹å®¤", "max_capacity": 8, "zone": "VIP", "table_type": "private", "priority": 10},
    ]

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

    await db.commit()

    return HTMLResponse('<div class="text-green-400 p-4">âœ… 8ãƒ†ãƒ¼ãƒ–ãƒ«ã‚’ç”Ÿæˆã—ã¾ã—ãŸã€‚ãƒšãƒ¼ã‚¸ã‚’æ›´æ–°ã—ã¦ãã ã•ã„ã€‚</div>')


@router.post("/tables/create", response_class=HTMLResponse)
async def create_table_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    branch_code: str = Query(default="hirama"),
    table_number: str = Form(...),
    name: str = Form(default=None),
    max_capacity: int = Form(default=4),
    table_type: str = Form(default="regular"),
    zone: str = Form(default=None),
    has_window: bool = Form(default=False),
    has_baby_chair: bool = Form(default=False),
):
    """Create new table via dashboard form"""
    from app.models.table import Table

    # Check for duplicate
    existing = await db.execute(
        select(Table).where(
            and_(
                Table.branch_code == branch_code,
                Table.table_number == table_number
            )
        )
    )
    if existing.scalar_one_or_none():
        return HTMLResponse('<div class="text-red-400 p-4">âŒ ã“ã®ãƒ†ãƒ¼ãƒ–ãƒ«ç•ªå·ã¯æ—¢ã«å­˜åœ¨ã—ã¾ã™</div>')

    table = Table(
        branch_code=branch_code,
        table_number=table_number,
        name=name,
        min_capacity=1,
        max_capacity=max_capacity,
        table_type=table_type,
        floor=1,
        zone=zone,
        has_window=has_window,
        has_baby_chair=has_baby_chair,
    )
    db.add(table)
    await db.commit()

    return HTMLResponse(f'<div class="text-green-400 p-4">âœ… {table_number} ã‚’è¿½åŠ ã—ã¾ã—ãŸã€‚ãƒšãƒ¼ã‚¸ã‚’æ›´æ–°ã—ã¦ãã ã•ã„ã€‚</div>')

