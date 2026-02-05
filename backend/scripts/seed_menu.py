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
    # è‚‰é¡ž (Meat)
    {"name": "å’Œç‰›ä¸Šãƒãƒ©ãƒŸ", "name_en": "Premium Wagyu Harami", "category": "meat", "price": 1800, "description": "å£ã®ä¸­ã§ã»ã©ã‘ã‚‹æŸ”ã‚‰ã‹ã•ã¨æ¿ƒåŽšãªå‘³ã‚ã„", "is_popular": True, "display_order": 1, "image_url": "https://images.unsplash.com/photo-1558030089-02acba3c214e?w=400"},
    {"name": "åŽšåˆ‡ã‚Šä¸Šã‚¿ãƒ³å¡©", "name_en": "Thick-cut Beef Tongue", "category": "meat", "price": 2200, "description": "è´…æ²¢ãªåŽšåˆ‡ã‚Šã€‚æ­¯ã”ãŸãˆã¨è‚‰æ±ãŒæº¢ã‚Œã¾ã™", "is_popular": True, "display_order": 2, "image_url": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400"},
    {"name": "ã‚«ãƒ«ãƒ“", "name_en": "Kalbi", "category": "meat", "price": 1500, "description": "å®šç•ªã®äººæ°—ãƒ¡ãƒ‹ãƒ¥ãƒ¼", "display_order": 3, "image_url": "https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400"},
    {"name": "ãƒ­ãƒ¼ã‚¹", "name_en": "Sirloin", "category": "meat", "price": 1600, "description": "èµ¤èº«ã®æ—¨å‘³ãŒæ¥½ã—ã‚ã‚‹", "display_order": 4, "image_url": "https://images.unsplash.com/photo-1558030089-02acba3c214e?w=400"},
    {"name": "ãƒ›ãƒ«ãƒ¢ãƒ³ç››ã‚Šåˆã‚ã›", "name_en": "Assorted Offal", "category": "meat", "price": 1400, "description": "æ–°é®®ãªãƒ›ãƒ«ãƒ¢ãƒ³ã‚’ãŸã£ã·ã‚Š", "display_order": 5, "image_url": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400"},
    {"name": "ç‰¹é¸ç››ã‚Šåˆã‚ã›", "name_en": "Premium Selection", "category": "meat", "price": 4500, "description": "æœ¬æ—¥ã®ãŠã™ã™ã‚å¸Œå°‘éƒ¨ä½ã‚’è´…æ²¢ã«", "is_popular": True, "display_order": 6, "image_url": "https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400"},

    # é£²ç‰© (Drinks)
    {"name": "ç”Ÿãƒ“ãƒ¼ãƒ«", "name_en": "Draft Beer", "category": "drinks", "price": 600, "description": "ã‚­ãƒ³ã‚­ãƒ³ã«å†·ãˆãŸç”Ÿãƒ“ãƒ¼ãƒ«", "display_order": 1, "image_url": "https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400"},
    {"name": "ãƒã‚¤ãƒœãƒ¼ãƒ«", "name_en": "Highball", "category": "drinks", "price": 500, "description": "ã™ã£ãã‚Šçˆ½ã‚„ã‹", "display_order": 2, "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400"},
    {"name": "ãƒ¬ãƒ¢ãƒ³ã‚µãƒ¯ãƒ¼", "name_en": "Lemon Sour", "category": "drinks", "price": 500, "description": "è‡ªå®¶è£½ãƒ¬ãƒ¢ãƒ³ã‚µãƒ¯ãƒ¼", "display_order": 3, "image_url": "https://images.unsplash.com/photo-1560508180-03f285f67c1a?w=400"},
    {"name": "ã‚¦ãƒ¼ãƒ­ãƒ³èŒ¶", "name_en": "Oolong Tea", "category": "drinks", "price": 300, "description": "ã‚½ãƒ•ãƒˆãƒ‰ãƒªãƒ³ã‚¯", "display_order": 4, "image_url": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400"},
    {"name": "ã‚³ãƒ¼ãƒ©", "name_en": "Cola", "category": "drinks", "price": 300, "description": "ã‚³ã‚«ãƒ»ã‚³ãƒ¼ãƒ©", "display_order": 5},

    # ã‚µãƒ©ãƒ€ (Salad)
    {"name": "ãƒãƒ§ãƒ¬ã‚®ã‚µãƒ©ãƒ€", "name_en": "Choregi Salad", "category": "salad", "price": 600, "description": "éŸ“å›½é¢¨ãƒ”ãƒªè¾›ã‚µãƒ©ãƒ€", "display_order": 1, "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400"},
    {"name": "ã‚·ãƒ¼ã‚¶ãƒ¼ã‚µãƒ©ãƒ€", "name_en": "Caesar Salad", "category": "salad", "price": 700, "description": "ãƒ‘ãƒ«ãƒ¡ã‚¶ãƒ³ãƒãƒ¼ã‚ºãŸã£ã·ã‚Š", "display_order": 2, "image_url": "https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400"},

    # ã”é£¯ãƒ»éºº (Rice & Noodles)
    {"name": "ãƒ©ã‚¤ã‚¹", "name_en": "Rice", "category": "rice", "price": 200, "description": "å›½ç”£ã‚³ã‚·ãƒ’ã‚«ãƒª", "display_order": 1, "image_url": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400"},
    {"name": "ãƒ“ãƒ“ãƒ³ãƒ", "name_en": "Bibimbap", "category": "rice", "price": 1200, "description": "çŸ³ç„¼ãƒ“ãƒ“ãƒ³ãƒ", "is_popular": True, "display_order": 2, "image_url": "https://images.unsplash.com/photo-1553163147-622ab57be1c7?w=400"},
    {"name": "å†·éºº", "name_en": "Cold Noodles", "category": "rice", "price": 900, "description": "éŸ“å›½å†·éºº", "display_order": 3, "image_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400"},
    {"name": "ã‚¯ãƒƒãƒ‘", "name_en": "Gukbap", "category": "rice", "price": 800, "description": "å…·ã ãã•ã‚“ã‚¹ãƒ¼ãƒ—ã”é£¯", "display_order": 4},

    # ã‚µã‚¤ãƒ‰ãƒ¡ãƒ‹ãƒ¥ãƒ¼ (Side)
    {"name": "ã‚­ãƒ ãƒ", "name_en": "Kimchi", "category": "side", "price": 400, "description": "è‡ªå®¶è£½ã‚­ãƒ ãƒ", "display_order": 1},
    {"name": "ãƒŠãƒ ãƒ«ç››ã‚Šåˆã‚ã›", "name_en": "Assorted Namul", "category": "side", "price": 500, "description": "3ç¨®ã®ãƒŠãƒ ãƒ«", "display_order": 2},
    {"name": "ãƒãƒ‚ãƒŸ", "name_en": "Pajeon", "category": "side", "price": 800, "description": "æµ·é®®ãƒãƒ‚ãƒŸ", "display_order": 3},

    # ãƒ‡ã‚¶ãƒ¼ãƒˆ (Dessert)
    {"name": "ãƒãƒ‹ãƒ©ã‚¢ã‚¤ã‚¹", "name_en": "Vanilla Ice Cream", "category": "dessert", "price": 400, "description": "æ¿ƒåŽšãƒãƒ‹ãƒ©", "display_order": 1, "image_url": "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400"},
    {"name": "æä»è±†è…", "name_en": "Almond Tofu", "category": "dessert", "price": 450, "description": "æ‰‹ä½œã‚Šæä»è±†è…", "display_order": 2, "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400"},
    {"name": "é»’ã”ã¾ã‚¢ã‚¤ã‚¹", "name_en": "Black Sesame Ice Cream", "category": "dessert", "price": 450, "description": "é¦™ã°ã—ã„é»’ã”ã¾", "display_order": 3},
]


TABLES = [
    {"table_number": "A1", "name": "ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼1", "min_capacity": 1, "max_capacity": 2, "table_type": "counter", "zone": "A"},
    {"table_number": "A2", "name": "ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼2", "min_capacity": 1, "max_capacity": 2, "table_type": "counter", "zone": "A"},
    {"table_number": "B1", "name": "ãƒ†ãƒ¼ãƒ–ãƒ«1", "min_capacity": 2, "max_capacity": 4, "table_type": "regular", "zone": "B"},
    {"table_number": "B2", "name": "ãƒ†ãƒ¼ãƒ–ãƒ«2", "min_capacity": 2, "max_capacity": 4, "table_type": "regular", "zone": "B"},
    {"table_number": "B3", "name": "ãƒ†ãƒ¼ãƒ–ãƒ«3", "min_capacity": 2, "max_capacity": 4, "table_type": "regular", "zone": "B", "has_window": True},
    {"table_number": "B4", "name": "ãƒ†ãƒ¼ãƒ–ãƒ«4", "min_capacity": 2, "max_capacity": 4, "table_type": "regular", "zone": "B", "has_window": True},
    {"table_number": "C1", "name": "å¤§ãƒ†ãƒ¼ãƒ–ãƒ«1", "min_capacity": 4, "max_capacity": 6, "table_type": "regular", "zone": "C"},
    {"table_number": "C2", "name": "å¤§ãƒ†ãƒ¼ãƒ–ãƒ«2", "min_capacity": 4, "max_capacity": 6, "table_type": "regular", "zone": "C"},
    {"table_number": "VIP1", "name": "å€‹å®¤A", "min_capacity": 4, "max_capacity": 8, "table_type": "private", "zone": "VIP", "priority": 10},
    {"table_number": "VIP2", "name": "å€‹å®¤B", "min_capacity": 4, "max_capacity": 8, "table_type": "private", "zone": "VIP", "priority": 10},
]


async def seed_menu():
    await init_db()

    async with AsyncSessionLocal() as session:
        # Seed menu items
        print("ðŸ– Seeding menu items...")
        for item_data in MENU_ITEMS:
            item = MenuItem(
                branch_code="hirama",
                **item_data
            )
            session.add(item)

        # Seed tables
        print("ðŸª‘ Seeding tables...")
        for table_data in TABLES:
            table = Table(
                branch_code="hirama",
                **table_data
            )
            session.add(table)

        await session.commit()
        print(f"âœ… Seeded {len(MENU_ITEMS)} menu items and {len(TABLES)} tables")


if __name__ == "__main__":
    asyncio.run(seed_menu())

