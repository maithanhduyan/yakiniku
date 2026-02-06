"""
Menu Router - Menu items API for table ordering
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.menu import MenuItem, MenuCategory
from app.schemas.menu import MenuItemResponse, MenuCategoryResponse, MenuResponse

router = APIRouter()

# Category labels and icons for UI
CATEGORY_INFO = {
    "meat": {"label": "肉類", "icon": "🥩"},
    "drinks": {"label": "飲物", "icon": "🍺"},
    "salad": {"label": "サラダ", "icon": "🥗"},
    "rice": {"label": "ご飯・麺", "icon": "🍚"},
    "side": {"label": "サイドメニュー", "icon": "🍟"},
    "dessert": {"label": "デザート", "icon": "🍨"},
    "set": {"label": "セットメニュー", "icon": "🍱"},
}


@router.get("", response_model=List[MenuItemResponse])
async def get_menu_items(
    branch_code: str = "hirama",
    category: str = None,
    available_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items for a branch"""
    query = select(MenuItem).where(MenuItem.branch_code == branch_code)

    if category:
        query = query.where(MenuItem.category == category)

    if available_only:
        query = query.where(MenuItem.is_available == True)

    query = query.order_by(MenuItem.category, MenuItem.display_order, MenuItem.name)

    result = await db.execute(query)
    items = result.scalars().all()

    return items


@router.get("/categories", response_model=MenuResponse)
async def get_menu_by_category(
    branch_code: str = "hirama",
    db: AsyncSession = Depends(get_db)
):
    """Get menu items grouped by category"""
    query = select(MenuItem).where(
        MenuItem.branch_code == branch_code,
        MenuItem.is_available == True
    ).order_by(MenuItem.category, MenuItem.display_order)

    result = await db.execute(query)
    items = result.scalars().all()

    # Group by category
    categories_dict = {}
    for item in items:
        cat = item.category
        if cat not in categories_dict:
            info = CATEGORY_INFO.get(cat, {"label": cat, "icon": "📦"})
            categories_dict[cat] = {
                "category": cat,
                "category_label": info["label"],
                "icon": info["icon"],
                "items": []
            }
        categories_dict[cat]["items"].append(item)

    # Maintain order
    category_order = ["meat", "drinks", "salad", "rice", "side", "dessert", "set"]
    categories = []
    for cat in category_order:
        if cat in categories_dict:
            categories.append(MenuCategoryResponse(**categories_dict[cat]))

    return MenuResponse(
        branch_code=branch_code,
        categories=categories,
        updated_at=datetime.now()
    )


@router.get("/popular", response_model=List[MenuItemResponse])
async def get_popular_items(
    branch_code: str = "hirama",
    limit: int = 6,
    db: AsyncSession = Depends(get_db)
):
    """Get popular/recommended menu items"""
    query = select(MenuItem).where(
        MenuItem.branch_code == branch_code,
        MenuItem.is_available == True,
        MenuItem.is_popular == True
    ).order_by(MenuItem.display_order).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    return items


@router.get("/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get single menu item details"""
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return item
