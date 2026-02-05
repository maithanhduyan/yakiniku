"""
Seed data for enhanced menu system
- Categories, Items, Options, Combos, Promotions
"""
import asyncio
from app.database import async_session_factory
from app.models import (
    ItemCategory, Item, ItemOptionGroup, ItemOption, ItemOptionAssignment,
    Combo, ComboItem, Promotion
)


# ============================================
# CATEGORIES
# ============================================
CATEGORIES = [
    # Top-level categories
    {"id": "cat-meat", "code": "meat", "name": "肉類", "name_en": "Meat", "icon": "🥩", "order": 1},
    {"id": "cat-drinks", "code": "drinks", "name": "飲み物", "name_en": "Drinks", "icon": "🍺", "order": 2},
    {"id": "cat-salad", "code": "salad", "name": "サラダ", "name_en": "Salad", "icon": "🥗", "order": 3},
    {"id": "cat-rice", "code": "rice", "name": "ご飯・麺", "name_en": "Rice & Noodles", "icon": "🍚", "order": 4},
    {"id": "cat-side", "code": "side", "name": "サイドメニュー", "name_en": "Side Menu", "icon": "🍢", "order": 5},
    {"id": "cat-dessert", "code": "dessert", "name": "デザート", "name_en": "Dessert", "icon": "🍨", "order": 6},

    # Sub-categories - Meat
    {"id": "cat-beef", "code": "beef", "name": "牛肉", "name_en": "Beef", "parent": "cat-meat", "order": 1},
    {"id": "cat-wagyu", "code": "wagyu", "name": "和牛", "name_en": "Wagyu", "parent": "cat-meat", "order": 2},
    {"id": "cat-pork", "code": "pork", "name": "豚肉", "name_en": "Pork", "parent": "cat-meat", "order": 3},
    {"id": "cat-chicken", "code": "chicken", "name": "鶏肉", "name_en": "Chicken", "parent": "cat-meat", "order": 4},
    {"id": "cat-offal", "code": "offal", "name": "ホルモン", "name_en": "Offal", "parent": "cat-meat", "order": 5},

    # Sub-categories - Drinks
    {"id": "cat-beer", "code": "beer", "name": "ビール", "name_en": "Beer", "parent": "cat-drinks", "order": 1},
    {"id": "cat-sour", "code": "sour", "name": "サワー", "name_en": "Sour", "parent": "cat-drinks", "order": 2},
    {"id": "cat-shochu", "code": "shochu", "name": "焼酎", "name_en": "Shochu", "parent": "cat-drinks", "order": 3},
    {"id": "cat-sake", "code": "sake", "name": "日本酒", "name_en": "Sake", "parent": "cat-drinks", "order": 4},
    {"id": "cat-soft", "code": "soft", "name": "ソフトドリンク", "name_en": "Soft Drinks", "parent": "cat-drinks", "order": 5},
]

# ============================================
# ITEMS (Menu Items)
# ============================================
ITEMS = [
    # === WAGYU / Premium Beef ===
    {"id": "item-001", "sku": "WAGYU-A5-SIRLOIN", "cat": "cat-wagyu",
     "name": "和牛A5サーロイン", "name_en": "Wagyu A5 Sirloin",
     "desc": "最高級A5ランクの和牛サーロイン。口の中でとろける極上の味わい",
     "price": 4500, "prep": 6, "printer": "grill",
     "popular": True, "has_options": True, "order": 1},

    {"id": "item-002", "sku": "WAGYU-A5-KALBI", "cat": "cat-wagyu",
     "name": "和牛A5カルビ", "name_en": "Wagyu A5 Kalbi",
     "desc": "霜降りが美しい最高級カルビ。濃厚な旨味が特徴",
     "price": 3800, "prep": 5, "printer": "grill",
     "popular": True, "has_options": True, "order": 2},

    {"id": "item-003", "sku": "WAGYU-HARAMI", "cat": "cat-wagyu",
     "name": "和牛上ハラミ", "name_en": "Premium Wagyu Harami",
     "desc": "口の中でほどける柔らかさと濃厚な味わい。当店自慢の一品",
     "price": 2800, "prep": 5, "printer": "grill",
     "popular": True, "has_options": True, "order": 3},

    # === Regular Beef ===
    {"id": "item-010", "sku": "BEEF-KALBI", "cat": "cat-beef",
     "name": "カルビ", "name_en": "Kalbi",
     "desc": "定番の人気メニュー。ジューシーな味わい",
     "price": 1500, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 1},

    {"id": "item-011", "sku": "BEEF-ROSU", "cat": "cat-beef",
     "name": "ロース", "name_en": "Sirloin",
     "desc": "あっさりとした赤身の美味しさ",
     "price": 1400, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 2},

    {"id": "item-012", "sku": "BEEF-TAN", "cat": "cat-beef",
     "name": "厚切り上タン塩", "name_en": "Thick Sliced Beef Tongue",
     "desc": "贅沢な厚切り。歯ごたえと肉汁が溢れます",
     "price": 2200, "prep": 6, "printer": "grill",
     "popular": True, "has_options": True, "order": 3},

    {"id": "item-013", "sku": "BEEF-TAN-THIN", "cat": "cat-beef",
     "name": "牛タン（6枚）", "name_en": "Beef Tongue 6pcs",
     "desc": "薄切り牛タン6枚盛り",
     "price": 1200, "prep": 5, "printer": "grill",
     "popular": False, "has_options": False, "order": 4},

    # === Pork ===
    {"id": "item-020", "sku": "PORK-KALBI", "cat": "cat-pork",
     "name": "豚カルビ", "name_en": "Pork Kalbi",
     "desc": "甘みのある豚バラ肉",
     "price": 900, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 1},

    {"id": "item-021", "sku": "PORK-TORO", "cat": "cat-pork",
     "name": "豚トロ", "name_en": "Pork Jowl",
     "desc": "脂の甘みが絶品。とろける食感",
     "price": 1100, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 2},

    # === Chicken ===
    {"id": "item-030", "sku": "CHICKEN-MOMO", "cat": "cat-chicken",
     "name": "鶏もも", "name_en": "Chicken Thigh",
     "desc": "柔らかくジューシーな鶏もも肉",
     "price": 800, "prep": 5, "printer": "grill",
     "popular": False, "has_options": True, "order": 1},

    # === Offal ===
    {"id": "item-040", "sku": "OFFAL-MIX", "cat": "cat-offal",
     "name": "ホルモン盛り合わせ", "name_en": "Offal Assortment",
     "desc": "新鮮なホルモンをたっぷり。ミノ・ハチノス・シマチョウ",
     "price": 1400, "prep": 7, "printer": "grill",
     "popular": False, "has_options": False, "order": 1},

    # === BEER ===
    {"id": "item-100", "sku": "BEER-DRAFT-M", "cat": "cat-beer",
     "name": "生ビール（中）", "name_en": "Draft Beer (Medium)",
     "desc": "キンキンに冷えた生ビール",
     "price": 600, "prep": 1, "printer": "drink",
     "popular": True, "has_options": False, "order": 1},

    {"id": "item-101", "sku": "BEER-DRAFT-L", "cat": "cat-beer",
     "name": "生ビール（大）", "name_en": "Draft Beer (Large)",
     "desc": "大ジョッキの生ビール",
     "price": 800, "prep": 1, "printer": "drink",
     "popular": True, "has_options": False, "order": 2},

    {"id": "item-102", "sku": "BEER-BOTTLE", "cat": "cat-beer",
     "name": "瓶ビール", "name_en": "Bottled Beer",
     "desc": "アサヒスーパードライ",
     "price": 650, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 3},

    # === SOUR ===
    {"id": "item-110", "sku": "SOUR-LEMON", "cat": "cat-sour",
     "name": "レモンサワー", "name_en": "Lemon Sour",
     "desc": "自家製レモンサワー。さっぱり飲みやすい",
     "price": 500, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 1},

    {"id": "item-111", "sku": "SOUR-UME", "cat": "cat-sour",
     "name": "梅酒サワー", "name_en": "Plum Wine Sour",
     "desc": "甘酸っぱい梅酒ソーダ割り",
     "price": 550, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 2},

    {"id": "item-112", "sku": "HIGHBALL", "cat": "cat-sour",
     "name": "ハイボール", "name_en": "Highball",
     "desc": "すっきり爽やかなウイスキーソーダ",
     "price": 500, "prep": 1, "printer": "drink",
     "popular": True, "has_options": False, "order": 3},

    # === SHOCHU ===
    {"id": "item-120", "sku": "SHOCHU-IMO", "cat": "cat-shochu",
     "name": "焼酎（芋）", "name_en": "Sweet Potato Shochu",
     "desc": "本格芋焼酎",
     "price": 500, "prep": 1, "printer": "drink",
     "popular": False, "has_options": True, "order": 1},  # has options: ロック/水割り/お湯割り

    {"id": "item-121", "sku": "SHOCHU-MUGI", "cat": "cat-shochu",
     "name": "焼酎（麦）", "name_en": "Barley Shochu",
     "desc": "本格麦焼酎",
     "price": 500, "prep": 1, "printer": "drink",
     "popular": False, "has_options": True, "order": 2},

    # === SOFT DRINKS ===
    {"id": "item-130", "sku": "SOFT-OOLONG", "cat": "cat-soft",
     "name": "ウーロン茶", "name_en": "Oolong Tea",
     "desc": "ソフトドリンク",
     "price": 300, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 1},

    {"id": "item-131", "sku": "SOFT-COLA", "cat": "cat-soft",
     "name": "コーラ", "name_en": "Cola",
     "desc": "コカ・コーラ",
     "price": 300, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 2},

    {"id": "item-132", "sku": "SOFT-ORANGE", "cat": "cat-soft",
     "name": "オレンジジュース", "name_en": "Orange Juice",
     "desc": "100%果汁オレンジジュース",
     "price": 350, "prep": 1, "printer": "drink",
     "popular": False, "has_options": False, "order": 3},

    # === SALADS ===
    {"id": "item-200", "sku": "SALAD-CHOREGI", "cat": "cat-salad",
     "name": "チョレギサラダ", "name_en": "Korean Salad",
     "desc": "韓国風ピリ辛サラダ。ごま油が香る",
     "price": 600, "prep": 3, "printer": "cold",
     "popular": False, "spicy": True, "vegetarian": True, "order": 1},

    {"id": "item-201", "sku": "SALAD-CAESAR", "cat": "cat-salad",
     "name": "シーザーサラダ", "name_en": "Caesar Salad",
     "desc": "パルメザンチーズたっぷり",
     "price": 700, "prep": 3, "printer": "cold",
     "popular": False, "vegetarian": True, "allergens": "milk", "order": 2},

    {"id": "item-202", "sku": "SALAD-NAMUL", "cat": "cat-salad",
     "name": "ナムル盛り合わせ", "name_en": "Namul Assortment",
     "desc": "3種のナムル（もやし・ほうれん草・大根）",
     "price": 500, "prep": 3, "printer": "cold",
     "popular": False, "vegetarian": True, "order": 3},

    {"id": "item-203", "sku": "SALAD-KIMCHI", "cat": "cat-salad",
     "name": "キムチ盛り合わせ", "name_en": "Kimchi Assortment",
     "desc": "白菜・カクテキ・オイキムチ",
     "price": 550, "prep": 2, "printer": "cold",
     "popular": False, "spicy": True, "vegetarian": True, "order": 4},

    # === RICE & NOODLES ===
    {"id": "item-300", "sku": "RICE-PLAIN", "cat": "cat-rice",
     "name": "ライス", "name_en": "Rice",
     "desc": "国産コシヒカリ使用",
     "price": 200, "prep": 2, "printer": "rice",
     "popular": False, "vegetarian": True, "has_options": True, "order": 1},  # size options

    {"id": "item-301", "sku": "RICE-BIBIMBAP", "cat": "cat-rice",
     "name": "石焼ビビンバ", "name_en": "Stone Pot Bibimbap",
     "desc": "熱々の石鍋で提供。おこげが美味しい",
     "price": 1200, "prep": 8, "printer": "grill",
     "popular": True, "spicy": True, "allergens": "egg", "has_options": True, "order": 2},

    {"id": "item-302", "sku": "RICE-REIMEN", "cat": "cat-rice",
     "name": "冷麺", "name_en": "Cold Noodles",
     "desc": "韓国冷麺。さっぱりとした味わい",
     "price": 900, "prep": 5, "printer": "cold",
     "popular": False, "allergens": "wheat", "order": 3},

    {"id": "item-303", "sku": "RICE-KUPPA", "cat": "cat-rice",
     "name": "カルビクッパ", "name_en": "Kalbi Rice Soup",
     "desc": "カルビ入りの韓国風スープご飯",
     "price": 950, "prep": 6, "printer": "grill",
     "popular": False, "spicy": True, "has_options": True, "order": 4},

    # === DESSERTS ===
    {"id": "item-400", "sku": "DESSERT-ICE", "cat": "cat-dessert",
     "name": "バニラアイス", "name_en": "Vanilla Ice Cream",
     "desc": "濃厚バニラアイス",
     "price": 300, "prep": 2, "printer": "cold",
     "popular": False, "vegetarian": True, "allergens": "milk", "order": 1},

    {"id": "item-401", "sku": "DESSERT-SHERBET", "cat": "cat-dessert",
     "name": "柚子シャーベット", "name_en": "Yuzu Sherbet",
     "desc": "さっぱり柚子シャーベット",
     "price": 350, "prep": 2, "printer": "cold",
     "popular": False, "vegetarian": True, "order": 2},
]

# ============================================
# OPTION GROUPS & OPTIONS
# ============================================
OPTION_GROUPS = [
    # Rice amount
    {"id": "og-rice-amount", "name": "ご飯の量", "name_en": "Rice Amount",
     "type": "single", "min": 0, "max": 1, "order": 1},

    # Doneness (for meat)
    {"id": "og-doneness", "name": "焼き加減", "name_en": "Doneness",
     "type": "single", "min": 0, "max": 1, "order": 2},

    # Toppings
    {"id": "og-toppings", "name": "トッピング", "name_en": "Toppings",
     "type": "multiple", "min": 0, "max": 3, "order": 3},

    # Shochu style
    {"id": "og-shochu-style", "name": "飲み方", "name_en": "Drinking Style",
     "type": "single", "min": 1, "max": 1, "order": 1},  # required

    # Spicy level
    {"id": "og-spicy", "name": "辛さ", "name_en": "Spicy Level",
     "type": "single", "min": 0, "max": 1, "order": 4},
]

OPTIONS = [
    # Rice amount options
    {"id": "opt-rice-small", "group": "og-rice-amount", "name": "少なめ", "name_en": "Less", "price": 0, "order": 1},
    {"id": "opt-rice-normal", "group": "og-rice-amount", "name": "普通", "name_en": "Normal", "price": 0, "default": True, "order": 2},
    {"id": "opt-rice-large", "group": "og-rice-amount", "name": "大盛り", "name_en": "Large", "price": 100, "order": 3},
    {"id": "opt-rice-extra", "group": "og-rice-amount", "name": "特盛り", "name_en": "Extra Large", "price": 200, "order": 4},

    # Doneness options
    {"id": "opt-rare", "group": "og-doneness", "name": "レア", "name_en": "Rare", "price": 0, "order": 1},
    {"id": "opt-medium-rare", "group": "og-doneness", "name": "ミディアムレア", "name_en": "Medium Rare", "price": 0, "order": 2},
    {"id": "opt-medium", "group": "og-doneness", "name": "ミディアム", "name_en": "Medium", "price": 0, "default": True, "order": 3},
    {"id": "opt-well", "group": "og-doneness", "name": "ウェルダン", "name_en": "Well Done", "price": 0, "order": 4},

    # Toppings
    {"id": "opt-egg", "group": "og-toppings", "name": "卵黄", "name_en": "Egg Yolk", "price": 100, "order": 1},
    {"id": "opt-negi", "group": "og-toppings", "name": "ネギ増し", "name_en": "Extra Green Onion", "price": 50, "order": 2},
    {"id": "opt-garlic", "group": "og-toppings", "name": "にんにく", "name_en": "Garlic", "price": 50, "order": 3},
    {"id": "opt-cheese", "group": "og-toppings", "name": "チーズ", "name_en": "Cheese", "price": 150, "order": 4},

    # Shochu style
    {"id": "opt-rock", "group": "og-shochu-style", "name": "ロック", "name_en": "On the Rocks", "price": 0, "default": True, "order": 1},
    {"id": "opt-mizuwari", "group": "og-shochu-style", "name": "水割り", "name_en": "Mizuwari", "price": 0, "order": 2},
    {"id": "opt-oyuwari", "group": "og-shochu-style", "name": "お湯割り", "name_en": "Oyuwari", "price": 0, "order": 3},
    {"id": "opt-straight", "group": "og-shochu-style", "name": "ストレート", "name_en": "Straight", "price": 0, "order": 4},

    # Spicy level
    {"id": "opt-mild", "group": "og-spicy", "name": "控えめ", "name_en": "Mild", "price": 0, "order": 1},
    {"id": "opt-normal-spicy", "group": "og-spicy", "name": "普通", "name_en": "Normal", "price": 0, "default": True, "order": 2},
    {"id": "opt-hot", "group": "og-spicy", "name": "辛め", "name_en": "Hot", "price": 0, "order": 3},
    {"id": "opt-extra-hot", "group": "og-spicy", "name": "激辛", "name_en": "Extra Hot", "price": 100, "order": 4},
]

# Item -> Option Group assignments
ITEM_OPTIONS = [
    # Wagyu items get doneness options
    {"item": "item-001", "group": "og-doneness"},  # A5 Sirloin
    {"item": "item-002", "group": "og-doneness"},  # A5 Kalbi
    {"item": "item-003", "group": "og-doneness"},  # Harami
    {"item": "item-010", "group": "og-doneness"},  # Kalbi
    {"item": "item-011", "group": "og-doneness"},  # Rosu
    {"item": "item-012", "group": "og-doneness"},  # Tan
    {"item": "item-020", "group": "og-doneness"},  # Pork Kalbi
    {"item": "item-021", "group": "og-doneness"},  # Pork Toro
    {"item": "item-030", "group": "og-doneness"},  # Chicken

    # Rice items get rice amount options
    {"item": "item-300", "group": "og-rice-amount"},  # Rice
    {"item": "item-301", "group": "og-rice-amount"},  # Bibimbap
    {"item": "item-303", "group": "og-rice-amount"},  # Kuppa

    # Bibimbap gets toppings
    {"item": "item-301", "group": "og-toppings"},

    # Spicy items get spicy level
    {"item": "item-301", "group": "og-spicy"},  # Bibimbap
    {"item": "item-303", "group": "og-spicy"},  # Kuppa

    # Shochu gets drinking style
    {"item": "item-120", "group": "og-shochu-style"},  # Imo
    {"item": "item-121", "group": "og-shochu-style"},  # Mugi
]

# ============================================
# COMBOS
# ============================================
COMBOS = [
    {
        "id": "combo-001",
        "code": "WAGYU-SALAD-30",
        "name": "和牛A5 + サラダセット",
        "name_en": "Wagyu A5 + Salad Set",
        "desc": "和牛A5（サーロインまたはカルビ）とサラダを一緒にご注文で30%OFF！",
        "discount_type": "percentage",
        "discount_value": 30,
        "featured": True,
        "items": [
            {"item_id": "item-001", "qty": 1},  # A5 Sirloin
            {"category_id": "cat-salad", "qty": 1},  # Any salad
        ]
    },
    {
        "id": "combo-002",
        "code": "YAKINIKU-SET-A",
        "name": "焼肉セットA（2名様）",
        "name_en": "Yakiniku Set A (2 persons)",
        "desc": "カルビ・ロース・ハラミ・サラダ・ライス×2のお得なセット",
        "discount_type": "new_price",
        "discount_value": 4500,  # Instead of individual total
        "featured": True,
        "items": [
            {"item_id": "item-010", "qty": 1},  # Kalbi
            {"item_id": "item-011", "qty": 1},  # Rosu
            {"item_id": "item-003", "qty": 1},  # Harami
            {"category_id": "cat-salad", "qty": 1},  # Any salad
            {"item_id": "item-300", "qty": 2},  # Rice x2
        ]
    },
    {
        "id": "combo-003",
        "code": "BEER-SNACK",
        "name": "ビール＋おつまみセット",
        "name_en": "Beer + Snack Set",
        "desc": "生ビール（中）2杯とキムチ盛り合わせで¥500 OFF",
        "discount_type": "fixed",
        "discount_value": 500,
        "items": [
            {"item_id": "item-100", "qty": 2},  # Draft beer x2
            {"item_id": "item-203", "qty": 1},  # Kimchi
        ]
    },
]

# ============================================
# PROMOTIONS
# ============================================
PROMOTIONS = [
    {
        "id": "promo-001",
        "code": "ORDER-30K-FREE-TONGUE",
        "name": "30,000円以上で牛タン無料",
        "name_en": "Free beef tongue for orders over ¥30,000",
        "desc": "お会計30,000円以上で牛タン（6枚）を1皿プレゼント！",
        "trigger_type": "order_amount",
        "trigger_value": 30000,
        "reward_type": "free_item",
        "reward_item_id": "item-013",  # Beef tongue 6pcs
        "reward_quantity": 1,
        "show_on_menu": True,
    },
    {
        "id": "promo-002",
        "code": "BEER-8-FREE-1",
        "name": "生ビール8杯で1杯無料",
        "name_en": "Buy 8 draft beers, get 1 free",
        "desc": "生ビール（大）を8杯ご注文で、1杯無料！",
        "trigger_type": "item_quantity",
        "trigger_item_id": "item-101",  # Draft beer large
        "trigger_value": 8,
        "reward_type": "free_item",
        "reward_item_id": "item-101",  # Same beer
        "reward_quantity": 1,
        "show_on_menu": True,
    },
    {
        "id": "promo-003",
        "code": "LUNCH-20OFF",
        "name": "ランチタイム20%OFF",
        "name_en": "Lunch 20% discount",
        "desc": "平日11:00-15:00のお食事が20%OFF（ドリンク除く）",
        "trigger_type": "order_amount",
        "trigger_value": 0,  # No minimum
        "reward_type": "discount_order",
        "reward_value": 20,  # 20%
        "valid_hours_start": "11:00",
        "valid_hours_end": "15:00",
        "valid_days": "mon,tue,wed,thu,fri",
        "show_on_menu": True,
    },
]


async def seed_enhanced_menu(branch_code: str = "hirama"):
    """Seed all enhanced menu data for a branch"""
    async with async_session_factory() as session:
        print(f"\n🍖 Seeding enhanced menu for branch: {branch_code}")

        # 1. Categories
        print("  📁 Creating categories...")
        for cat in CATEGORIES:
            category = ItemCategory(
                id=cat["id"],
                branch_code=branch_code,
                code=cat["code"],
                name=cat["name"],
                name_en=cat.get("name_en"),
                parent_id=cat.get("parent"),
                icon=cat.get("icon"),
                display_order=cat.get("order", 0),
                is_active=True
            )
            session.add(category)
        await session.commit()
        print(f"    ✅ Created {len(CATEGORIES)} categories")

        # 2. Items
        print("  🥩 Creating items...")
        for item in ITEMS:
            new_item = Item(
                id=item["id"],
                branch_code=branch_code,
                category_id=item["cat"],
                sku=item.get("sku"),
                name=item["name"],
                name_en=item.get("name_en"),
                description=item.get("desc"),
                base_price=item["price"],
                prep_time_minutes=item.get("prep", 5),
                kitchen_printer=item.get("printer"),
                display_order=item.get("order", 0),
                is_available=True,
                is_popular=item.get("popular", False),
                is_spicy=item.get("spicy", False),
                is_vegetarian=item.get("vegetarian", False),
                allergens=item.get("allergens"),
                has_options=item.get("has_options", False),
            )
            session.add(new_item)
        await session.commit()
        print(f"    ✅ Created {len(ITEMS)} items")

        # 3. Option Groups
        print("  ⚙️ Creating option groups...")
        for og in OPTION_GROUPS:
            group = ItemOptionGroup(
                id=og["id"],
                branch_code=branch_code,
                name=og["name"],
                name_en=og.get("name_en"),
                selection_type=og["type"],
                min_selections=og.get("min", 0),
                max_selections=og.get("max", 1),
                display_order=og.get("order", 0),
                is_active=True
            )
            session.add(group)
        await session.commit()
        print(f"    ✅ Created {len(OPTION_GROUPS)} option groups")

        # 4. Options
        print("  📋 Creating options...")
        for opt in OPTIONS:
            option = ItemOption(
                id=opt["id"],
                group_id=opt["group"],
                name=opt["name"],
                name_en=opt.get("name_en"),
                price_adjustment=opt.get("price", 0),
                is_default=opt.get("default", False),
                display_order=opt.get("order", 0),
                is_available=True
            )
            session.add(option)
        await session.commit()
        print(f"    ✅ Created {len(OPTIONS)} options")

        # 5. Item-Option Assignments
        print("  🔗 Linking items to options...")
        for i, assignment in enumerate(ITEM_OPTIONS):
            link = ItemOptionAssignment(
                id=f"ioa-{i+1:03d}",
                item_id=assignment["item"],
                option_group_id=assignment["group"],
                display_order=i
            )
            session.add(link)
        await session.commit()
        print(f"    ✅ Created {len(ITEM_OPTIONS)} item-option links")

        # 6. Combos
        print("  🎁 Creating combos...")
        for combo_data in COMBOS:
            combo = Combo(
                id=combo_data["id"],
                branch_code=branch_code,
                code=combo_data["code"],
                name=combo_data["name"],
                name_en=combo_data.get("name_en"),
                description=combo_data.get("desc"),
                discount_type=combo_data["discount_type"],
                discount_value=combo_data["discount_value"],
                is_active=True,
                is_featured=combo_data.get("featured", False)
            )
            session.add(combo)

            # Combo items
            for j, ci in enumerate(combo_data.get("items", [])):
                combo_item = ComboItem(
                    id=f"{combo_data['id']}-item-{j+1}",
                    combo_id=combo_data["id"],
                    item_id=ci.get("item_id"),
                    category_id=ci.get("category_id"),
                    quantity=ci.get("qty", 1)
                )
                session.add(combo_item)
        await session.commit()
        print(f"    ✅ Created {len(COMBOS)} combos")

        # 7. Promotions
        print("  🎉 Creating promotions...")
        for promo_data in PROMOTIONS:
            promo = Promotion(
                id=promo_data["id"],
                branch_code=branch_code,
                code=promo_data["code"],
                name=promo_data["name"],
                name_en=promo_data.get("name_en"),
                description=promo_data.get("desc"),
                trigger_type=promo_data["trigger_type"],
                trigger_item_id=promo_data.get("trigger_item_id"),
                trigger_value=promo_data["trigger_value"],
                reward_type=promo_data["reward_type"],
                reward_item_id=promo_data.get("reward_item_id"),
                reward_value=promo_data.get("reward_value"),
                reward_quantity=promo_data.get("reward_quantity", 1),
                show_on_menu=promo_data.get("show_on_menu", False),
                is_active=True
            )
            session.add(promo)
        await session.commit()
        print(f"    ✅ Created {len(PROMOTIONS)} promotions")

        print(f"\n✅ Enhanced menu seeding complete for {branch_code}!")
        print(f"   - {len(CATEGORIES)} categories")
        print(f"   - {len(ITEMS)} items")
        print(f"   - {len(OPTION_GROUPS)} option groups")
        print(f"   - {len(OPTIONS)} options")
        print(f"   - {len(ITEM_OPTIONS)} item-option links")
        print(f"   - {len(COMBOS)} combos")
        print(f"   - {len(PROMOTIONS)} promotions")


if __name__ == "__main__":
    asyncio.run(seed_enhanced_menu())
