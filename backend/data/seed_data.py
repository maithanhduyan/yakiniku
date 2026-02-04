"""
Seed database with staff, customers, and preferences data.
Run: cd backend && python -m data.seed_data
"""
import asyncio
import csv
import os
import random
from datetime import datetime
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine, Base
from app.models.staff import Staff, StaffRole
from app.models.customer import GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference
from app.models.menu import MenuItem


DATA_DIR = Path(__file__).parent


async def seed_staff(session: AsyncSession):
    """Seed staff members from CSV."""
    csv_path = DATA_DIR / "staff.csv"
    if not csv_path.exists():
        print("❌ staff.csv not found")
        return

    count = 0
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            staff = Staff(
                id=row["id"],
                employee_id=row["employee_id"],
                branch_code=row["branch_code"],
                name=row["name"],
                name_kana=row["name_kana"],
                phone=row["phone"],
                email=row["email"],
                role=StaffRole(row["role"]),
                pin_code=row["pin_code"],
                is_active=row["is_active"].lower() == "true",
                hire_date=datetime.fromisoformat(row["hire_date"]),
            )
            session.add(staff)
            count += 1

    await session.commit()
    print(f"✅ Seeded {count} staff members (2 admins)")


async def seed_customers(session: AsyncSession):
    """Seed global customers from CSV."""
    csv_path = DATA_DIR / "customers.csv"
    if not csv_path.exists():
        print("❌ customers.csv not found")
        return

    count = 0
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customer = GlobalCustomer(
                id=row["id"],
                phone=row["phone"],
                name=row["name"],
                email=row.get("email"),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            session.add(customer)
            count += 1

    await session.commit()
    print(f"✅ Seeded {count} global customers")


async def seed_branch_customers(session: AsyncSession):
    """Seed branch customers with sentiment from CSV."""
    csv_path = DATA_DIR / "branch_customers.csv"
    if not csv_path.exists():
        print("❌ branch_customers.csv not found")
        return

    count = 0
    sentiment_counts = {
        "very_positive": 0,
        "positive": 0,
        "neutral": 0,
        "negative": 0,
        "very_negative": 0,
    }

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            branch_customer = BranchCustomer(
                id=f"bc-{idx:03d}",
                global_customer_id=row["global_customer_id"],
                branch_code=row["branch_code"],
                visit_count=int(row["visit_count"]),
                last_visit=datetime.fromisoformat(row["last_visit"]) if row.get("last_visit") else None,
                is_vip=row["is_vip"].lower() == "true",
                notes=row.get("notes", ""),
            )
            session.add(branch_customer)
            count += 1

            # Count sentiments from notes
            sentiment = row.get("sentiment", "neutral")
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1

    await session.commit()
    print(f"✅ Seeded {count} branch customers")
    print(f"   Sentiment distribution:")
    for sentiment, c in sentiment_counts.items():
        emoji = {
            "very_positive": "😍",
            "positive": "😊",
            "neutral": "😐",
            "negative": "😕",
            "very_negative": "😠",
        }.get(sentiment, "")
        print(f"   - {sentiment}: {c} {emoji}")


async def seed_preferences(session: AsyncSession):
    """Seed customer preferences from CSV."""
    csv_path = DATA_DIR / "customer_preferences.csv"
    if not csv_path.exists():
        print("❌ customer_preferences.csv not found")
        return

    count = 0
    categories = {}

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            preference = CustomerPreference(
                id=f"pref-{idx:03d}",
                branch_customer_id=row["branch_customer_id"],
                preference=row["preference"],
                category=row.get("category", "other"),
                note=row.get("note", ""),
                confidence=float(row.get("confidence", 0.8)),
                source=row.get("source", "staff"),
            )
            session.add(preference)
            count += 1

            # Count categories
            cat = row.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1

    await session.commit()
    print(f"✅ Seeded {count} customer preferences")
    print(f"   Categories: {categories}")


async def seed_menu_items(session: AsyncSession):
    """Seed menu items from CSV."""
    csv_path = DATA_DIR / "menu_items.csv"
    if not csv_path.exists():
        print("❌ menu_items.csv not found")
        return

    count = 0
    categories = {}

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Build image URL from filename
            image_filename = row.get("image_filename", "")
            image_url = f"/images/menu/{image_filename}" if image_filename else None

            menu_item = MenuItem(
                id=row["id"],
                branch_code=row["branch_code"],
                name=row["name"],
                name_en=row.get("name_en", ""),
                description=row.get("description", ""),
                category=row["category"],
                subcategory=row.get("subcategory", ""),
                price=int(row["price"]),
                display_order=int(row.get("display_order", 0)),
                is_available=row.get("is_available", "true").lower() == "true",
                is_popular=row.get("is_popular", "false").lower() == "true",
                is_spicy=row.get("is_spicy", "false").lower() == "true",
                is_vegetarian=row.get("is_vegetarian", "false").lower() == "true",
                allergens=row.get("allergens", ""),
                prep_time_minutes=int(row.get("prep_time_minutes", 5)),
                kitchen_note=row.get("kitchen_note", ""),
                image_url=image_url,
            )
            session.add(menu_item)
            count += 1

            # Count categories
            cat = row["category"]
            categories[cat] = categories.get(cat, 0) + 1

    await session.commit()
    print(f"✅ Seeded {count} menu items")
    print(f"   Categories: {categories}")


async def seed_all(drop_existing=True):
    """Run all seed functions."""
    print("\n🌱 Seeding Yakiniku Jinan database...\n")

    # Import all models to register them with Base
    from app.models.staff import Staff
    from app.models.customer import GlobalCustomer, BranchCustomer
    from app.models.preference import CustomerPreference
    from app.models.booking import Booking
    from app.models.table import Table
    from app.models.branch import Branch
    from app.models.chat import ChatMessage
    from app.models.menu import MenuItem
    from app.models.order import Order, OrderItem

    # Drop and recreate tables
    async with engine.begin() as conn:
        if drop_existing:
            await conn.run_sync(Base.metadata.drop_all)
            print("🗑️  Dropped existing tables")
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")

    async with AsyncSessionLocal() as session:
        await seed_staff(session)
        await seed_customers(session)
        await seed_branch_customers(session)
        await seed_preferences(session)
        await seed_menu_items(session)

    print("\n🎉 Database seeding complete!\n")
    print("Summary:")
    print("  - 10 Staff members (2 admins, 1 manager, 1 cashier, 3 waiters, 2 kitchen, 1 receptionist)")
    print("  - 100 Global customers with Japanese names")
    print("  - 100 Branch customers with visit history & sentiment")
    print("  - Customer preferences for CRM insights")
    print("  - 40 Menu items with images")


if __name__ == "__main__":
    asyncio.run(seed_all())
