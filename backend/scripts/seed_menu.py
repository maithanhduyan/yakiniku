"""
Seed script for menu items and tables
Run: python -m scripts.seed_menu
"""
import asyncio
from decimal import Decimal
from app.database import AsyncSessionLocal, init_db
from app.models.menu import MenuItem
from app.models.table import Table


MENU_ITEMS = [
    # 肉類 (Meat)
    {"name": "和牛上ハラミ", "name_en": "Premium Wagyu Harami", "category": "meat", "price": 1800, "description": "口の中でほどける柔らかさと濃厚な味わい", "is_popular": True, "display_order": 1, "image_url": "https://images.unsplash.com/photo-1558030089-02acba3c214e?w=400"},
    {"name": "厚切り上タン塩", "name_en": "Thick-cut Beef Tongue", "category": "meat", "price": 2200, "description": "贅沢な厚切り。歯ごたえと肉汁が溢れます", "is_popular": True, "display_order": 2, "image_url": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400"},
    {"name": "カルビ", "name_en": "Kalbi", "category": "meat", "price": 1500, "description": "定番の人気メニュー", "display_order": 3, "image_url": "https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400"},
    {"name": "ロース", "name_en": "Sirloin", "category": "meat", "price": 1600, "description": "赤身の旨味が楽しめる", "display_order": 4, "image_url": "https://images.unsplash.com/photo-1558030089-02acba3c214e?w=400"},
    {"name": "ホルモン盛り合わせ", "name_en": "Assorted Offal", "category": "meat", "price": 1400, "description": "新鮮なホルモンをたっぷり", "display_order": 5, "image_url": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400"},
    {"name": "特選盛り合わせ", "name_en": "Premium Selection", "category": "meat", "price": 4500, "description": "本日のおすすめ希少部位を贅沢に", "is_popular": True, "display_order": 6, "image_url": "https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400"},

    # 飲物 (Drinks)
    {"name": "生ビール", "name_en": "Draft Beer", "category": "drinks", "price": 600, "description": "キンキンに冷えた生ビール", "display_order": 1, "image_url": "https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400"},
    {"name": "ハイボール", "name_en": "Highball", "category": "drinks", "price": 500, "description": "すっきり爽やか", "display_order": 2, "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400"},
    {"name": "レモンサワー", "name_en": "Lemon Sour", "category": "drinks", "price": 500, "description": "自家製レモンサワー", "display_order": 3, "image_url": "https://images.unsplash.com/photo-1560508180-03f285f67c1a?w=400"},
    {"name": "ウーロン茶", "name_en": "Oolong Tea", "category": "drinks", "price": 300, "description": "ソフトドリンク", "display_order": 4, "image_url": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400"},
    {"name": "コーラ", "name_en": "Cola", "category": "drinks", "price": 300, "description": "コカ・コーラ", "display_order": 5},

    # サラダ (Salad)
    {"name": "チョレギサラダ", "name_en": "Choregi Salad", "category": "salad", "price": 600, "description": "韓国風ピリ辛サラダ", "display_order": 1, "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400"},
    {"name": "シーザーサラダ", "name_en": "Caesar Salad", "category": "salad", "price": 700, "description": "パルメザンチーズたっぷり", "display_order": 2, "image_url": "https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400"},

    # ご飯・麺 (Rice & Noodles)
    {"name": "ライス", "name_en": "Rice", "category": "rice", "price": 200, "description": "国産コシヒカリ", "display_order": 1, "image_url": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400"},
    {"name": "ビビンバ", "name_en": "Bibimbap", "category": "rice", "price": 1200, "description": "石焼ビビンバ", "is_popular": True, "display_order": 2, "image_url": "https://images.unsplash.com/photo-1553163147-622ab57be1c7?w=400"},
    {"name": "冷麺", "name_en": "Cold Noodles", "category": "rice", "price": 900, "description": "韓国冷麺", "display_order": 3, "image_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400"},
    {"name": "クッパ", "name_en": "Gukbap", "category": "rice", "price": 800, "description": "具だくさんスープご飯", "display_order": 4},

    # サイドメニュー (Side)
    {"name": "キムチ", "name_en": "Kimchi", "category": "side", "price": 400, "description": "自家製キムチ", "display_order": 1},
    {"name": "ナムル盛り合わせ", "name_en": "Assorted Namul", "category": "side", "price": 500, "description": "3種のナムル", "display_order": 2},
    {"name": "チヂミ", "name_en": "Pajeon", "category": "side", "price": 800, "description": "海鮮チヂミ", "display_order": 3},

    # デザート (Dessert)
    {"name": "バニラアイス", "name_en": "Vanilla Ice Cream", "category": "dessert", "price": 400, "description": "濃厚バニラ", "display_order": 1, "image_url": "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400"},
    {"name": "杏仁豆腐", "name_en": "Almond Tofu", "category": "dessert", "price": 450, "description": "手作り杏仁豆腐", "display_order": 2, "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400"},
    {"name": "黒ごまアイス", "name_en": "Black Sesame Ice Cream", "category": "dessert", "price": 450, "description": "香ばしい黒ごま", "display_order": 3},
]


TABLES = [
    {"table_number": "A1", "name": "カウンター1", "min_capacity": 1, "max_capacity": 2, "table_type": "counter", "zone": "A"},
    {"table_number": "A2", "name": "カウンター2", "min_capacity": 1, "max_capacity": 2, "table_type": "counter", "zone": "A"},
    {"table_number": "B1", "name": "テーブル1", "min_capacity": 2, "max_capacity": 4, "table_type": "regular", "zone": "B"},
    {"table_number": "B2", "name": "テーブル2", "min_capacity": 2, "max_capacity": 4, "table_type": "regular", "zone": "B"},
    {"table_number": "B3", "name": "テーブル3", "min_capacity": 2, "max_capacity": 4, "table_type": "regular", "zone": "B", "has_window": True},
    {"table_number": "B4", "name": "テーブル4", "min_capacity": 2, "max_capacity": 4, "table_type": "regular", "zone": "B", "has_window": True},
    {"table_number": "C1", "name": "大テーブル1", "min_capacity": 4, "max_capacity": 6, "table_type": "regular", "zone": "C"},
    {"table_number": "C2", "name": "大テーブル2", "min_capacity": 4, "max_capacity": 6, "table_type": "regular", "zone": "C"},
    {"table_number": "VIP1", "name": "個室A", "min_capacity": 4, "max_capacity": 8, "table_type": "private", "zone": "VIP", "priority": 10},
    {"table_number": "VIP2", "name": "個室B", "min_capacity": 4, "max_capacity": 8, "table_type": "private", "zone": "VIP", "priority": 10},
]


async def seed_menu():
    await init_db()

    async with AsyncSessionLocal() as session:
        # Seed menu items
        print("🍖 Seeding menu items...")
        for item_data in MENU_ITEMS:
            item = MenuItem(
                branch_code="jinan",
                **item_data
            )
            session.add(item)

        # Seed tables
        print("🪑 Seeding tables...")
        for table_data in TABLES:
            table = Table(
                branch_code="jinan",
                **table_data
            )
            session.add(table)

        await session.commit()
        print(f"✅ Seeded {len(MENU_ITEMS)} menu items and {len(TABLES)} tables")


if __name__ == "__main__":
    asyncio.run(seed_menu())
