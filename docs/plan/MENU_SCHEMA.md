# Menu Schema Enhancement Plan

## Current State
Chỉ có bảng `menu_items` đơn giản, chưa hỗ trợ:
- Item options (ít cơm, nhiều cơm, nhiều rau)
- Combo deals (bò wagyu A5 + salad giảm 30%)
- Loyalty rewards (8 ly bia lớn tặng 1)
- Order thresholds (đơn ≥ 30,000¥ tặng lưỡi bò)

## Proposed Schema

### 1. Categories Table
```sql
CREATE TABLE item_categories (
    id VARCHAR(36) PRIMARY KEY,
    branch_code VARCHAR(50) NOT NULL,
    code VARCHAR(50) NOT NULL,           -- 'meat', 'drinks', 'salad'
    name VARCHAR(100) NOT NULL,          -- '肉類', '飲み物', 'サラダ'
    name_en VARCHAR(100),                -- 'Meat', 'Drinks', 'Salad'
    parent_id VARCHAR(36),               -- For subcategories
    display_order INT DEFAULT 0,
    icon VARCHAR(50),                    -- emoji or icon name
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    FOREIGN KEY (parent_id) REFERENCES item_categories(id)
);
```

### 2. Items Table (Enhanced)
```sql
CREATE TABLE items (
    id VARCHAR(36) PRIMARY KEY,
    branch_code VARCHAR(50) NOT NULL,
    category_id VARCHAR(36) NOT NULL,

    -- Identity
    sku VARCHAR(50) UNIQUE,              -- 'MEAT-WAGYU-A5-001'
    name VARCHAR(100) NOT NULL,          -- '和牛A5サーロイン'
    name_en VARCHAR(100),
    description TEXT,

    -- Pricing
    base_price NUMERIC(10,0) NOT NULL,   -- ¥3,500
    tax_rate NUMERIC(4,2) DEFAULT 10.0,

    -- Kitchen
    prep_time_minutes INT DEFAULT 5,
    kitchen_printer VARCHAR(50),         -- 'grill', 'drink', 'cold'
    kitchen_note TEXT,

    -- Display
    display_order INT DEFAULT 0,
    image_url VARCHAR(500),

    -- Flags
    is_available BOOLEAN DEFAULT true,
    is_popular BOOLEAN DEFAULT false,
    is_spicy BOOLEAN DEFAULT false,
    is_vegetarian BOOLEAN DEFAULT false,
    allergens VARCHAR(200),              -- 'egg,milk,wheat'

    -- Option config
    has_options BOOLEAN DEFAULT false,
    options_required BOOLEAN DEFAULT false,  -- Must select at least 1 option

    -- Stock management (future)
    track_stock BOOLEAN DEFAULT false,
    stock_quantity INT,
    low_stock_alert INT,

    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES item_categories(id)
);
```

### 3. Item Options (Customization)
```sql
-- Option Groups: "ご飯の量", "焼き加減", "トッピング"
CREATE TABLE item_option_groups (
    id VARCHAR(36) PRIMARY KEY,
    branch_code VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,          -- 'ご飯の量'
    name_en VARCHAR(100),                -- 'Rice Amount'
    selection_type VARCHAR(20) NOT NULL, -- 'single', 'multiple'
    min_selections INT DEFAULT 0,        -- 0 = optional
    max_selections INT DEFAULT 1,
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT true
);

-- Option Choices: "少なめ -¥0", "普通 +¥0", "大盛り +¥100"
CREATE TABLE item_options (
    id VARCHAR(36) PRIMARY KEY,
    group_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,          -- '大盛り'
    name_en VARCHAR(100),                -- 'Large'
    price_adjustment NUMERIC(10,0) DEFAULT 0,  -- +¥100
    is_default BOOLEAN DEFAULT false,
    display_order INT DEFAULT 0,
    is_available BOOLEAN DEFAULT true,

    FOREIGN KEY (group_id) REFERENCES item_option_groups(id)
);

-- Link items to their available option groups
CREATE TABLE item_option_assignments (
    id VARCHAR(36) PRIMARY KEY,
    item_id VARCHAR(36) NOT NULL,
    option_group_id VARCHAR(36) NOT NULL,
    display_order INT DEFAULT 0,

    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (option_group_id) REFERENCES item_option_groups(id),
    UNIQUE(item_id, option_group_id)
);
```

**Example Data:**
```
Option Group: "ご飯の量" (Rice Amount) - single selection
├── 少なめ (Less)      +¥0
├── 普通 (Normal)      +¥0   [default]
└── 大盛り (Large)     +¥100

Option Group: "焼き加減" (Doneness) - single selection
├── レア (Rare)
├── ミディアム (Medium) [default]
└── ウェルダン (Well-done)

Option Group: "トッピング" (Toppings) - multiple selection, max 3
├── 卵黄 (Egg yolk)    +¥100
├── ネギ (Green onion) +¥50
└── にんにく (Garlic)   +¥50
```

### 4. Combo Deals
```sql
CREATE TABLE combos (
    id VARCHAR(36) PRIMARY KEY,
    branch_code VARCHAR(50) NOT NULL,

    -- Identity
    code VARCHAR(50) NOT NULL,           -- 'WAGYU-SALAD-30'
    name VARCHAR(200) NOT NULL,          -- '和牛A5 + サラダセット'
    name_en VARCHAR(200),
    description TEXT,

    -- Discount
    discount_type VARCHAR(20) NOT NULL,  -- 'percentage', 'fixed', 'new_price'
    discount_value NUMERIC(10,2) NOT NULL, -- 30 (%), ¥500, or ¥2800

    -- Validity
    start_date DATE,
    end_date DATE,
    valid_hours_start TIME,              -- 17:00 (dinner only)
    valid_hours_end TIME,                -- 22:00
    valid_days VARCHAR(20),              -- 'mon,tue,wed,thu,fri' or null for all

    -- Limits
    max_uses_total INT,                  -- null = unlimited
    max_uses_per_order INT DEFAULT 1,
    min_order_amount NUMERIC(10,0),      -- Minimum order to apply

    -- Display
    display_order INT DEFAULT 0,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Items required to trigger the combo
CREATE TABLE combo_items (
    id VARCHAR(36) PRIMARY KEY,
    combo_id VARCHAR(36) NOT NULL,
    item_id VARCHAR(36) NOT NULL,
    quantity INT DEFAULT 1,              -- Need this many

    FOREIGN KEY (combo_id) REFERENCES combos(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);
```

**Example:**
```
Combo: "和牛A5 + サラダセット" (Wagyu A5 + Salad Set)
├── Discount: 30% off
├── Required items:
│   ├── 和牛A5サーロイン × 1
│   └── Any salad × 1
└── Valid: All week, dinner time only (17:00-22:00)
```

### 5. Promotions & Thresholds
```sql
CREATE TABLE promotions (
    id VARCHAR(36) PRIMARY KEY,
    branch_code VARCHAR(50) NOT NULL,

    -- Identity
    code VARCHAR(50) NOT NULL,           -- 'ORDER-30K-FREE-TONGUE'
    name VARCHAR(200) NOT NULL,          -- '30,000円以上で牛タン無料'
    description TEXT,

    -- Trigger conditions
    trigger_type VARCHAR(30) NOT NULL,   -- 'order_amount', 'item_quantity', 'item_total'
    trigger_item_id VARCHAR(36),         -- For item-based triggers
    trigger_value NUMERIC(10,0) NOT NULL, -- ¥30,000 or quantity 8

    -- Reward
    reward_type VARCHAR(30) NOT NULL,    -- 'free_item', 'discount_item', 'discount_order'
    reward_item_id VARCHAR(36),          -- Item to give free
    reward_value NUMERIC(10,2),          -- Discount % or amount
    reward_quantity INT DEFAULT 1,       -- Give 1 free item

    -- Validity
    start_date DATE,
    end_date DATE,
    valid_hours_start TIME,
    valid_hours_end TIME,

    -- Limits
    max_uses_per_order INT DEFAULT 1,
    stackable BOOLEAN DEFAULT false,     -- Can combine with other promos?

    is_active BOOLEAN DEFAULT true,
    display_order INT DEFAULT 0,

    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    FOREIGN KEY (trigger_item_id) REFERENCES items(id),
    FOREIGN KEY (reward_item_id) REFERENCES items(id)
);
```

**Examples:**
```
Promotion 1: "30,000円以上で牛タン無料"
├── Trigger: order_amount >= ¥30,000
└── Reward: free_item = 牛タン(6枚) × 1

Promotion 2: "生ビール8杯で1杯無料"
├── Trigger: item_quantity(生ビール) >= 8
└── Reward: free_item = 生ビール × 1
```

### 6. Gift Cards / Loyalty Points (Future)
```sql
CREATE TABLE loyalty_programs (
    id VARCHAR(36) PRIMARY KEY,
    branch_code VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,

    -- Points earning
    points_per_yen INT DEFAULT 1,        -- 1 point per ¥100
    points_multiplier NUMERIC(4,2) DEFAULT 1.0,

    -- Points redemption
    yen_per_point NUMERIC(4,2),          -- ¥1 per point
    min_points_redeem INT,

    is_active BOOLEAN DEFAULT true
);

CREATE TABLE customer_loyalty (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    program_id VARCHAR(36) NOT NULL,

    points_balance INT DEFAULT 0,
    lifetime_points INT DEFAULT 0,
    tier VARCHAR(20) DEFAULT 'bronze',   -- 'bronze', 'silver', 'gold', 'platinum'

    FOREIGN KEY (program_id) REFERENCES loyalty_programs(id)
);

CREATE TABLE gift_cards (
    id VARCHAR(36) PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,    -- 'GIFT-XXXX-XXXX'

    initial_value NUMERIC(10,0) NOT NULL,
    current_balance NUMERIC(10,0) NOT NULL,

    issued_to_customer_id VARCHAR(36),
    issued_at TIMESTAMP,
    expires_at TIMESTAMP,

    is_active BOOLEAN DEFAULT true
);
```

## Migration Priority

### Phase 1: Core (Immediate)
1. ✅ `item_categories` - Organize menu structure
2. ✅ `items` (enhanced) - Replace simple menu_items
3. ✅ `item_option_groups` - Option customization
4. ✅ `item_options` - Option choices
5. ✅ `item_option_assignments` - Link items to options

### Phase 2: Deals (Next Sprint)
6. `combos` - Set meals & combo discounts
7. `combo_items` - Combo composition
8. `promotions` - Threshold rewards

### Phase 3: Loyalty (Future)
9. `loyalty_programs` - Points system
10. `customer_loyalty` - Customer points
11. `gift_cards` - Prepaid cards

## Sample Data for Hirama Branch

### Categories
| code | name | name_en | parent |
|------|------|---------|--------|
| meat | 肉類 | Meat | - |
| meat-beef | 牛肉 | Beef | meat |
| meat-pork | 豚肉 | Pork | meat |
| meat-chicken | 鶏肉 | Chicken | meat |
| meat-offal | ホルモン | Offal | meat |
| drinks | 飲み物 | Drinks | - |
| drinks-beer | ビール | Beer | drinks |
| drinks-sour | サワー | Sour | drinks |
| salad | サラダ | Salad | - |
| rice | ご飯・麺 | Rice & Noodles | - |
| dessert | デザート | Dessert | - |

### Option Groups
| name | name_en | type | items |
|------|---------|------|-------|
| ご飯の量 | Rice Amount | single | ビビンバ, クッパ |
| 焼き加減 | Doneness | single | All beef items |
| トッピング | Toppings | multiple | ビビンバ |
| 飲み方 | Drinking Style | single | 焼酎 |

### Options
| group | name | name_en | price_adj |
|-------|------|---------|-----------|
| ご飯の量 | 少なめ | Less | ¥0 |
| ご飯の量 | 普通 | Normal | ¥0 |
| ご飯の量 | 大盛り | Large | +¥100 |
| 焼き加減 | レア | Rare | ¥0 |
| 焼き加減 | ミディアム | Medium | ¥0 |
| 焼き加減 | ウェルダン | Well-done | ¥0 |
| トッピング | 卵黄 | Egg Yolk | +¥100 |
| トッピング | ネギ増し | Extra Onion | +¥50 |
| 飲み方 | ロック | On the Rocks | ¥0 |
| 飲み方 | 水割り | Mizuwari | ¥0 |
| 飲み方 | お湯割り | Oyuwari | ¥0 |

## API Endpoints

```
GET  /api/menu/categories?branch_code=hirama
GET  /api/menu/items?branch_code=hirama&category=meat
GET  /api/menu/items/{item_id}/options
GET  /api/menu/combos?branch_code=hirama
GET  /api/menu/promotions?branch_code=hirama

POST /api/orders/calculate  # Calculate with options, combos, promotions
```

## Frontend Changes

### Table Order App
```javascript
// When item has options
if (item.has_options) {
    showOptionsModal(item);
}

// Options modal shows:
// - Required option groups (must select)
// - Optional groups (can skip)
// - Price updates in real-time
```

### Cart Calculation
```javascript
// Server-side calculation includes:
// 1. Base item prices
// 2. Option adjustments
// 3. Combo discounts (auto-detected)
// 4. Promotion rewards (auto-applied)
// 5. Tax calculation
```
