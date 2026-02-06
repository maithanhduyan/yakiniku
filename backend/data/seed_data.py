"""
Comprehensive Seed Data — Seeds ALL tables from CSV files.

Usage:
    cd backend
    python cli.py db seed           # Seed (skip if data exists)
    python cli.py db seed --drop    # Drop + recreate + seed
    python -m data.seed_data        # Direct run (legacy)

Tables seeded (in dependency order):
  1. branches         — 5 branches (hirama, shinjuku, yaesu, shinagawa, yokohama)
  2. global_customers  — 100 customers
  3. branch_customers  — 50 branch-customer relationships
  4. customer_preferences — 57 preferences
  5. staff             — 34 staff across all branches
  6. tables            — 21 tables across branches
  7. bookings          — 25 bookings
  8. menu_items        — 40 legacy menu items (hirama)
  9. item_categories   — 16 categories (6 top-level + 10 sub)
 10. items             — 63 enhanced items with options/kitchen routing
 11. item_option_groups — 7 option groups
 12. item_options      — 28 option choices
 13. item_option_assignments — 29 item↔option links
 14. combos            — 9 combo deals
 15. combo_items       — 33 combo item requirements
 16. promotions        — 8 promotions
"""
import asyncio
import csv
from datetime import datetime, date, time
from decimal import Decimal
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sa_func

# Add parent directory to path for standalone execution
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Database
from app.database import AsyncSessionLocal, engine, Base

# Models
from app.models.branch import Branch
from app.models.staff import Staff, StaffRole
from app.models.customer import GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference
from app.models.table import Table
from app.models.booking import Booking
from app.models.menu import MenuItem
from app.models.category import ItemCategory
from app.models.item import Item, ItemOptionGroup, ItemOption, ItemOptionAssignment
from app.models.combo import Combo, ComboItem
from app.models.promotion import Promotion

DATA_DIR = Path(__file__).parent


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _bool(value: str) -> bool:
    """Parse boolean from CSV string."""
    return value.strip().lower() in ("true", "1", "yes")


def _int(value: str, default: int = 0) -> int:
    """Parse int from CSV string with default."""
    value = value.strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _float(value: str, default: float = 0.0) -> float:
    """Parse float from CSV string with default."""
    value = value.strip()
    return float(value) if value else default


def _decimal(value: str, default=0) -> Decimal:
    """Parse Decimal from CSV string."""
    value = value.strip()
    return Decimal(value) if value else Decimal(default)


def _str(value: str) -> str | None:
    """Return None for empty strings."""
    value = value.strip()
    return value if value else None


def _datetime(value: str) -> datetime | None:
    """Parse datetime from CSV string."""
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _date(value: str) -> date | None:
    """Parse date from CSV string."""
    value = value.strip()
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _time(value: str) -> time | None:
    """Parse time from CSV string."""
    value = value.strip()
    if not value:
        return None
    parts = value.split(":")
    h, m = int(parts[0]), int(parts[1])
    s = int(parts[2]) if len(parts) > 2 else 0
    # Handle times >= 24:00 (late-night closing)
    if h >= 24:
        h = h - 24
    return time(h, m, s)


def _read_csv(filename: str) -> list[dict]:
    """Read CSV file and return list of dicts."""
    csv_path = DATA_DIR / filename
    if not csv_path.exists():
        print(f"  ⚠️  {filename} not found, skipping")
        return []
    with open(csv_path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


async def _count(session: AsyncSession, model) -> int:
    """Count rows in a table."""
    result = await session.execute(select(sa_func.count()).select_from(model))
    return result.scalar() or 0


# ──────────────────────────────────────────────
# Seeders
# ──────────────────────────────────────────────

async def seed_branches(session: AsyncSession) -> int:
    """Seed branches from branches.csv."""
    rows = _read_csv("branches.csv")
    count = 0
    for row in rows:
        branch = Branch(
            id=f"branch-{row['code']}",
            code=row["code"],
            name=row["name"],
            phone=_str(row.get("phone", "")),
            address=_str(row.get("address", "")),
            opening_time=_time(row.get("opening_time", "")),
            closing_time=_time(row.get("closing_time", "")),
            is_active=_bool(row.get("is_active", "true")),
        )
        session.add(branch)
        count += 1
    await session.commit()
    print(f"  ✅ branches: {count} rows")
    return count


async def seed_customers(session: AsyncSession) -> int:
    """Seed global customers from customers.csv."""
    rows = _read_csv("customers.csv")
    count = 0
    for row in rows:
        customer = GlobalCustomer(
            id=row["id"],
            phone=row["phone"],
            name=row["name"],
            email=_str(row.get("email", "")),
            created_at=_datetime(row.get("created_at", "")),
        )
        session.add(customer)
        count += 1
    await session.commit()
    print(f"  ✅ global_customers: {count} rows")
    return count


async def seed_branch_customers(session: AsyncSession) -> int:
    """Seed branch customers from branch_customers.csv."""
    rows = _read_csv("branch_customers.csv")
    count = 0
    for idx, row in enumerate(rows, 1):
        bc = BranchCustomer(
            id=f"bc-{idx:03d}",
            global_customer_id=row["global_customer_id"],
            branch_code=row["branch_code"],
            visit_count=_int(row.get("visit_count", "0")),
            last_visit=_datetime(row.get("last_visit", "")),
            is_vip=_bool(row.get("is_vip", "false")),
            notes=_str(row.get("notes", "")),
        )
        session.add(bc)
        count += 1
    await session.commit()
    print(f"  ✅ branch_customers: {count} rows")
    return count


async def seed_preferences(session: AsyncSession) -> int:
    """Seed customer preferences from customer_preferences.csv."""
    rows = _read_csv("customer_preferences.csv")
    count = 0
    for idx, row in enumerate(rows, 1):
        # branch_customer_id in CSV is the global_customer_id
        # Map: cust-001 → bc-xxx via DB lookup
        global_cust_id = row["branch_customer_id"]
        result = await session.execute(
            select(BranchCustomer.id).where(
                BranchCustomer.global_customer_id == global_cust_id
            ).limit(1)
        )
        bc_id = result.scalar()
        if not bc_id:
            continue

        pref = CustomerPreference(
            id=f"pref-{idx:03d}",
            branch_customer_id=bc_id,
            preference=row["preference"],
            category=_str(row.get("category", "other")),
            note=_str(row.get("note", "")),
            confidence=_float(row.get("confidence", "0.8")),
            source=row.get("source", "manual"),
        )
        session.add(pref)
        count += 1
    await session.commit()
    print(f"  ✅ customer_preferences: {count} rows")
    return count


async def seed_staff(session: AsyncSession) -> int:
    """Seed staff from staff.csv."""
    rows = _read_csv("staff.csv")
    count = 0
    for row in rows:
        staff = Staff(
            id=row["id"],
            employee_id=row["employee_id"],
            branch_code=row["branch_code"],
            name=row["name"],
            name_kana=_str(row.get("name_kana", "")),
            phone=_str(row.get("phone", "")),
            email=_str(row.get("email", "")),
            role=row.get("role", "waiter"),
            pin_code=_str(row.get("pin_code", "")),
            is_active=_bool(row.get("is_active", "true")),
            hire_date=_datetime(row.get("hire_date", "")),
        )
        session.add(staff)
        count += 1
    await session.commit()
    print(f"  ✅ staff: {count} rows")
    return count


async def seed_tables(session: AsyncSession) -> int:
    """Seed tables from tables.csv."""
    rows = _read_csv("tables.csv")
    count = 0
    for row in rows:
        table = Table(
            id=row["id"],
            branch_code=row["branch_code"],
            table_number=row["table_number"],
            name=_str(row.get("name", "")),
            max_capacity=_int(row["max_capacity"]),
            table_type=row.get("table_type", "regular"),
            zone=_str(row.get("zone", "")),
            has_window=_bool(row.get("has_window", "false")),
            is_active=_bool(row.get("is_active", "true")),
            notes=_str(row.get("notes", "")),
        )
        session.add(table)
        count += 1
    await session.commit()
    print(f"  ✅ tables: {count} rows")
    return count


async def seed_bookings(session: AsyncSession) -> int:
    """Seed bookings from bookings.csv."""
    rows = _read_csv("bookings.csv")
    count = 0
    for row in rows:
        global_cust_id = _str(row.get("global_customer_id", ""))
        bc_id = None
        if global_cust_id:
            result = await session.execute(
                select(BranchCustomer.id).where(
                    BranchCustomer.global_customer_id == global_cust_id
                ).limit(1)
            )
            bc_id = result.scalar()

        # Model: String(5) expects "HH:MM", CSV may have "HH:MM:SS"
        time_val = row["time"].strip()
        if len(time_val) > 5:
            time_val = time_val[:5]

        booking = Booking(
            id=row["id"],
            branch_code=row["branch_code"],
            branch_customer_id=bc_id,
            date=_date(row["date"]),
            time=time_val,
            guests=_int(row["guests"]),
            guest_name=_str(row.get("guest_name", "")),
            guest_phone=_str(row.get("phone", "")),
            guest_email=_str(row.get("email", "")),
            status=row.get("status", "pending"),
            note=_str(row.get("note", "")),
            source=row.get("source", "web"),
        )
        session.add(booking)
        count += 1
    await session.commit()
    print(f"  ✅ bookings: {count} rows")
    return count


async def seed_menu_items(session: AsyncSession) -> int:
    """Seed legacy menu items from menu_items.csv."""
    rows = _read_csv("menu_items.csv")
    count = 0
    for row in rows:
        image_filename = row.get("image_filename", "")
        image_url = f"/images/menu/{image_filename}" if image_filename else None

        item = MenuItem(
            id=row["id"],
            branch_code=row["branch_code"],
            name=row["name"],
            name_en=_str(row.get("name_en", "")),
            description=_str(row.get("description", "")),
            category=row["category"],
            subcategory=_str(row.get("subcategory", "")),
            price=_int(row["price"]),
            display_order=_int(row.get("display_order", "0")),
            is_available=_bool(row.get("is_available", "true")),
            is_popular=_bool(row.get("is_popular", "false")),
            is_spicy=_bool(row.get("is_spicy", "false")),
            is_vegetarian=_bool(row.get("is_vegetarian", "false")),
            allergens=_str(row.get("allergens", "")),
            prep_time_minutes=_int(row.get("prep_time_minutes", "5")),
            kitchen_note=_str(row.get("kitchen_note", "")),
            image_url=image_url,
        )
        session.add(item)
        count += 1
    await session.commit()
    print(f"  ✅ menu_items: {count} rows")
    return count


async def seed_categories(session: AsyncSession) -> int:
    """Seed item categories from item_categories.csv (parent-first order)."""
    rows = _read_csv("item_categories.csv")

    # Split into parent (no parent_id) and children
    parents = [r for r in rows if not r.get("parent_id", "").strip()]
    children = [r for r in rows if r.get("parent_id", "").strip()]

    count = 0
    for row in parents:
        cat = ItemCategory(
            id=row["id"],
            branch_code=row["branch_code"],
            code=row["code"],
            name=row["name"],
            name_en=_str(row.get("name_en", "")),
            parent_id=None,
            display_order=_int(row.get("display_order", "0")),
            icon=_str(row.get("icon", "")),
            is_active=_bool(row.get("is_active", "true")),
        )
        session.add(cat)
        count += 1
    await session.commit()

    for row in children:
        cat = ItemCategory(
            id=row["id"],
            branch_code=row["branch_code"],
            code=row["code"],
            name=row["name"],
            name_en=_str(row.get("name_en", "")),
            parent_id=row["parent_id"],
            display_order=_int(row.get("display_order", "0")),
            icon=_str(row.get("icon", "")),
            is_active=_bool(row.get("is_active", "true")),
        )
        session.add(cat)
        count += 1
    await session.commit()
    print(f"  ✅ item_categories: {count} rows")
    return count


async def seed_items(session: AsyncSession) -> int:
    """Seed enhanced items from items.csv."""
    rows = _read_csv("items.csv")
    count = 0
    for row in rows:
        item = Item(
            id=row["id"],
            branch_code=row["branch_code"],
            category_id=_str(row.get("category_id", "")),
            sku=_str(row.get("sku", "")),
            name=row["name"],
            name_en=_str(row.get("name_en", "")),
            description=_str(row.get("description", "")),
            base_price=_decimal(row["base_price"]),
            prep_time_minutes=_int(row.get("prep_time_minutes", "5")),
            kitchen_printer=_str(row.get("kitchen_printer", "")),
            display_order=_int(row.get("display_order", "0")),
            is_available=_bool(row.get("is_available", "true")),
            is_popular=_bool(row.get("is_popular", "false")),
            is_spicy=_bool(row.get("is_spicy", "false")),
            is_vegetarian=_bool(row.get("is_vegetarian", "false")),
            allergens=_str(row.get("allergens", "")),
            has_options=_bool(row.get("has_options", "false")),
            options_required=_bool(row.get("options_required", "false")),
        )
        session.add(item)
        count += 1
    await session.commit()
    print(f"  ✅ items: {count} rows")
    return count


async def seed_option_groups(session: AsyncSession) -> int:
    """Seed item option groups from item_option_groups.csv."""
    rows = _read_csv("item_option_groups.csv")
    count = 0
    for row in rows:
        group = ItemOptionGroup(
            id=row["id"],
            branch_code=row["branch_code"],
            name=row["name"],
            name_en=_str(row.get("name_en", "")),
            description=_str(row.get("description", "")),
            selection_type=row.get("selection_type", "single"),
            min_selections=_int(row.get("min_selections", "0")),
            max_selections=_int(row.get("max_selections", "1")),
            display_order=_int(row.get("display_order", "0")),
            is_active=_bool(row.get("is_active", "true")),
        )
        session.add(group)
        count += 1
    await session.commit()
    print(f"  ✅ item_option_groups: {count} rows")
    return count


async def seed_options(session: AsyncSession) -> int:
    """Seed item options from item_options.csv."""
    rows = _read_csv("item_options.csv")
    count = 0
    for row in rows:
        option = ItemOption(
            id=row["id"],
            group_id=row["group_id"],
            name=row["name"],
            name_en=_str(row.get("name_en", "")),
            price_adjustment=_decimal(row.get("price_adjustment", "0")),
            is_default=_bool(row.get("is_default", "false")),
            display_order=_int(row.get("display_order", "0")),
            is_available=_bool(row.get("is_available", "true")),
        )
        session.add(option)
        count += 1
    await session.commit()
    print(f"  ✅ item_options: {count} rows")
    return count


async def seed_option_assignments(session: AsyncSession) -> int:
    """Seed item-option assignments from item_option_assignments.csv."""
    rows = _read_csv("item_option_assignments.csv")
    count = 0
    for row in rows:
        assignment = ItemOptionAssignment(
            id=row["id"],
            item_id=row["item_id"],
            option_group_id=row["option_group_id"],
            display_order=_int(row.get("display_order", "0")),
        )
        session.add(assignment)
        count += 1
    await session.commit()
    print(f"  ✅ item_option_assignments: {count} rows")
    return count


async def seed_combos(session: AsyncSession) -> int:
    """Seed combos from combos.csv."""
    rows = _read_csv("combos.csv")
    count = 0
    for row in rows:
        combo = Combo(
            id=row["id"],
            branch_code=row["branch_code"],
            code=row["code"],
            name=row["name"],
            name_en=_str(row.get("name_en", "")),
            description=_str(row.get("description", "")),
            discount_type=row["discount_type"],
            discount_value=_decimal(row["discount_value"]),
            valid_hours_start=_time(row.get("valid_hours_start", "")),
            valid_hours_end=_time(row.get("valid_hours_end", "")),
            valid_days=_str(row.get("valid_days", "")),
            max_uses_per_order=_int(row.get("max_uses_per_order", "1")),
            display_order=_int(row.get("display_order", "0")),
            is_active=_bool(row.get("is_active", "true")),
            is_featured=_bool(row.get("is_featured", "false")),
        )
        session.add(combo)
        count += 1
    await session.commit()
    print(f"  ✅ combos: {count} rows")
    return count


async def seed_combo_items(session: AsyncSession) -> int:
    """Seed combo items from combo_items.csv."""
    rows = _read_csv("combo_items.csv")
    count = 0
    for row in rows:
        ci = ComboItem(
            id=row["id"],
            combo_id=row["combo_id"],
            item_id=_str(row.get("item_id", "")),
            category_id=_str(row.get("category_id", "")),
            quantity=_int(row.get("quantity", "1")),
        )
        session.add(ci)
        count += 1
    await session.commit()
    print(f"  ✅ combo_items: {count} rows")
    return count


async def seed_promotions(session: AsyncSession) -> int:
    """Seed promotions from promotions.csv."""
    rows = _read_csv("promotions.csv")
    count = 0
    for row in rows:
        promo = Promotion(
            id=row["id"],
            branch_code=row["branch_code"],
            code=row["code"],
            name=row["name"],
            name_en=_str(row.get("name_en", "")),
            description=_str(row.get("description", "")),
            trigger_type=row["trigger_type"],
            trigger_item_id=_str(row.get("trigger_item_id", "")),
            trigger_category_id=_str(row.get("trigger_category_id", "")),
            trigger_value=_decimal(row.get("trigger_value", "0")),
            reward_type=row["reward_type"],
            reward_item_id=_str(row.get("reward_item_id", "")),
            reward_value=_decimal(row.get("reward_value", "0")) if _str(row.get("reward_value", "")) else None,
            reward_quantity=_int(row.get("reward_quantity", "1")),
            valid_hours_start=_time(row.get("valid_hours_start", "")),
            valid_hours_end=_time(row.get("valid_hours_end", "")),
            valid_days=_str(row.get("valid_days", "")),
            max_uses_per_order=_int(row.get("max_uses_per_order", "1")),
            max_uses_per_customer=_int(row.get("max_uses_per_customer", "0")) or None,
            max_uses_total=_int(row.get("max_uses_total", "0")) or None,
            stackable=_bool(row.get("stackable", "false")),
            priority=_int(row.get("priority", "0")),
            display_order=_int(row.get("display_order", "0")),
            show_on_menu=_bool(row.get("show_on_menu", "true")),
            is_active=_bool(row.get("is_active", "true")),
        )
        session.add(promo)
        count += 1
    await session.commit()
    print(f"  ✅ promotions: {count} rows")
    return count


# ──────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────

async def seed_all(drop_existing: bool = True):
    """Run all seed functions in dependency order."""
    print("\n🌱 Seeding Yakiniku database...\n")

    # Import all models to register with Base
    from app.models import (
        Branch, GlobalCustomer, BranchCustomer, CustomerPreference,
        Booking, ChatMessage, ChatInsight,
        Table, TableAssignment, TableAvailability,
        MenuItem, Item, ItemCategory, ItemOptionGroup, ItemOption, ItemOptionAssignment,
        Combo, ComboItem, Promotion, PromotionUsage,
        Order, OrderItem, TableSession, Staff,
    )
    from app.domains.tableorder.events import OrderEvent
    from app.domains.checkin.models import WaitingList, CheckInLog

    if drop_existing:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print("  🗑️  Dropped existing tables")
            await conn.run_sync(Base.metadata.create_all)
            print("  📦 Created tables\n")

    totals = {}

    async with AsyncSessionLocal() as session:
        # 1. Core entities (no FK dependencies)
        totals["branches"] = await seed_branches(session)
        totals["customers"] = await seed_customers(session)

        # 2. Entities depending on core
        totals["branch_customers"] = await seed_branch_customers(session)
        totals["staff"] = await seed_staff(session)
        totals["tables"] = await seed_tables(session)

        # 3. Entities depending on customers/tables
        totals["preferences"] = await seed_preferences(session)
        totals["bookings"] = await seed_bookings(session)

        # 4. Menu system
        totals["menu_items"] = await seed_menu_items(session)
        totals["categories"] = await seed_categories(session)
        totals["items"] = await seed_items(session)
        totals["option_groups"] = await seed_option_groups(session)
        totals["options"] = await seed_options(session)
        totals["option_assignments"] = await seed_option_assignments(session)

        # 5. Combos & Promotions
        totals["combos"] = await seed_combos(session)
        totals["combo_items"] = await seed_combo_items(session)
        totals["promotions"] = await seed_promotions(session)

    total_rows = sum(totals.values())
    print(f"\n🎉 Seeding complete! {total_rows} rows across {len(totals)} tables\n")

    # Summary table
    print("  ┌──────────────────────────┬───────┐")
    print("  │ Table                    │ Rows  │")
    print("  ├──────────────────────────┼───────┤")
    for table_name, count in totals.items():
        print(f"  │ {table_name:<24} │ {count:>5} │")
    print("  └──────────────────────────┴───────┘")
    print()


if __name__ == "__main__":
    asyncio.run(seed_all())
