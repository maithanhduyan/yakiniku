# 📊 Database Schema — Yakiniku.io

> Auto-maintained. Last update: 2026-02-07
>
> **29 models** across **27 tables** · **10 enum types**
> Dual DB: SQLite (dev) / PostgreSQL (prod, asyncpg)
> IDs: UUID v4 `String(36)` · No auto-increment

---

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Core — Branch & Staff](#1-core--branch--staff)
3. [Users — App Operators](#2-users--app-operators)
4. [Customers](#3-customers)
5. [Tables & Seating](#4-tables--seating)
6. [Bookings](#5-bookings)
7. [Menu — Legacy](#6-menu--legacy)
8. [Menu — Enhanced](#7-menu--enhanced)
9. [Options System](#8-options-system)
10. [Combos & Promotions](#9-combos--promotions)
11. [Orders](#10-orders)
12. [Event Sourcing](#11-event-sourcing)
13. [Devices](#12-devices)
14. [Check-in & Waiting](#13-check-in--waiting)
15. [Chat & Insights](#14-chat--insights)
16. [ER Diagram](#er-diagram)
17. [Seed Data Summary](#seed-data-summary)

---

## Schema Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CORE LAYER                               │
│  branches ──┬── staff ── users (operators)                      │
│             ├── tables ── devices                               │
│             └── global_customers ── branch_customers            │
├─────────────────────────────────────────────────────────────────┤
│                       MENU LAYER                                │
│  item_categories ── items ──┬── item_option_assignments         │
│  menu_items (legacy)        │     └── item_option_groups        │
│  combos ── combo_items      │          └── item_options          │
│  promotions ── promotion_usages                                 │
├─────────────────────────────────────────────────────────────────┤
│                      OPERATIONS LAYER                           │
│  bookings ── table_assignments                                  │
│  table_sessions                                                 │
│  orders ── order_items                                          │
│  order_events (event sourcing)                                  │
│  devices (auth + session)                                       │
│  waiting_list ── checkin_logs                                   │
│  chat_messages ── chat_insights                                 │
├─────────────────────────────────────────────────────────────────┤
│                      PREFERENCE LAYER                           │
│  customer_preferences                                           │
│  table_availability                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Core — Branch & Staff

### `branches`

Restaurant locations. Multi-tenant root entity.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| code | String(50) | UNIQUE, NOT NULL, INDEX | `hirama`, `shinjuku` |
| name | String(255) | NOT NULL | Display name |
| subdomain | String(100) | | URL subdomain |
| phone | String(20) | | |
| address | String(500) | | |
| theme_primary_color | String(7) | default `#d4af37` | Brand color |
| theme_bg_color | String(7) | default `#1a1a1a` | Background |
| logo_url | String(500) | | |
| opening_time | Time | | `17:00` |
| closing_time | Time | | `24:00` |
| last_order_time | Time | | `22:30` |
| closed_days | JSON | default `[2]` | 0=Sun, 2=Tue |
| max_capacity | Integer | default 30 | |
| features | JSON | | `{chat, ai_booking, ...}` |
| is_active | Boolean | default true | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

### `staff`

HR records for restaurant employees.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | `staff-001` |
| branch_code | String(50) | NOT NULL, INDEX | FK-like (no constraint) |
| employee_id | String(20) | UNIQUE, NOT NULL | `S001` |
| name | String(255) | NOT NULL | Full name (kanji) |
| name_kana | String(255) | | Furigana |
| phone | String(20) | | |
| email | String(255) | | |
| role | String(20) | default `waiter` | StaffRole enum |
| pin_code | String(6) | | Quick login PIN |
| is_active | Boolean | default true | |
| hire_date | DateTime(tz) | | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

**Enum `StaffRole`**: `admin` · `manager` · `cashier` · `waiter` · `kitchen` · `receptionist`

---

## 2. Users — App Operators

### `users`

People who **operate** the apps. Separated from `staff` (HR) to isolate auth concerns.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | `user-001` |
| staff_id | String(36) | FK → staff.id, nullable | Link to HR record |
| branch_code | String(50) | INDEX, nullable | NULL = multi-branch |
| username | String(50) | UNIQUE, NOT NULL, INDEX | Login credential |
| password_hash | String(128) | NOT NULL | SHA-256 hex digest |
| display_name | String(100) | NOT NULL | UI display |
| role | String(20) | NOT NULL, INDEX, default `staff` | UserRole enum |
| can_dashboard | Boolean | default false | 📊 Dashboard access |
| can_checkin | Boolean | default false | 📋 Check-in access |
| can_table_order | Boolean | default false | 🍽️ Table-order access |
| can_kitchen | Boolean | default false | 👨‍🍳 Kitchen KDS access |
| can_pos | Boolean | default false | 💰 POS access |
| managed_branches | String(500) | nullable | Multi-branch CSV or `*` |
| is_active | Boolean | default true | |
| last_login_at | DateTime(tz) | | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |
| notes | Text | nullable | |

**Enum `UserRole`**: `chef_manager` · `manager` · `staff`

### Role Hierarchy & App Permissions

```
┌──────────────────────────────────────────────────────────────────┐
│  Role             │ Dashboard │ Checkin │ Table │ Kitchen │ POS  │
├───────────────────┼───────────┼────────┼───────┼─────────┼──────┤
│  chef_manager     │    ✅     │   ✅   │  ✅   │   ✅    │  ✅  │
│  (統括マネージャー)│  multi-   │        │       │         │      │
│                   │  branch   │        │       │         │      │
├───────────────────┼───────────┼────────┼───────┼─────────┼──────┤
│  manager          │    ✅     │   ✅   │  ✅   │   ✅    │  ✅  │
│  (店長)           │  single   │        │       │         │      │
│                   │  branch   │        │       │         │      │
├───────────────────┼───────────┼────────┼───────┼─────────┼──────┤
│  staff            │    ❌     │   ✅   │  ✅   │   ✅    │  ❌  │
│  (スタッフ)       │           │  some  │ some  │  some   │      │
│                   │           │ staff  │ staff │  staff  │      │
└───────────────────┴───────────┴────────┴───────┴─────────┴──────┘

Note: staff permissions are per-user (can_* flags), not role-wide.
Kitchen-only staff get can_kitchen=true, all others false.
```

### Multi-Branch Access (chef_manager)

| managed_branches | Meaning |
|------------------|---------|
| `*` | All branches (CEO/owner) |
| `hirama,shinjuku,yaesu` | Specific branches (regional manager) |
| NULL | Single branch (use `branch_code`) |

### User ↔ Staff Relationship

```
User (app operator)          Staff (HR record)
┌──────────────┐             ┌──────────────┐
│ user-004     │────────────→│ staff-001    │
│ yamada       │  staff_id   │ 山田 太郎    │
│ role=manager │             │ role=admin   │
│ branch=hirama│             │ branch=hirama│
└──────────────┘             └──────────────┘

chef_manager may have staff_id=NULL (not tied to one branch)
```

---

## 3. Customers

### `global_customers`

Cross-branch customer identity.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| phone | String(20) | UNIQUE, NOT NULL, INDEX | Primary identifier |
| name | String(255) | | |
| email | String(255) | | |
| created_at | DateTime(tz) | server_default now() | |

### `branch_customers`

Per-branch customer relationship (visit history, VIP status).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| global_customer_id | String(36) | FK → global_customers.id, NOT NULL | |
| branch_code | String(50) | NOT NULL, INDEX | |
| visit_count | Integer | default 0 | |
| last_visit | DateTime(tz) | | |
| is_vip | Boolean | default false | |
| notes | String(1000) | | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

### `customer_preferences`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_customer_id | String(36) | FK → branch_customers.id, NOT NULL | |
| preference | String(255) | NOT NULL | |
| category | String(50) | | |
| note | String(500) | | |
| confidence | Float | default 1.0 | |
| source | String(50) | default `manual` | |
| created_at | DateTime(tz) | server_default now() | |

---

## 4. Tables & Seating

### `tables`

Physical tables in each branch.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | `table-hirama-01` |
| branch_code | String(50) | NOT NULL, INDEX | |
| table_number | String(10) | NOT NULL | `A1`, `B2` |
| name | String(100) | | Display label |
| min_capacity | Integer | default 1 | |
| max_capacity | Integer | NOT NULL | |
| table_type | String(20) | default `regular` | TableType enum |
| floor | Integer | default 1 | |
| zone | String(50) | | `floor`, `counter`, `private` |
| has_window | Boolean | default false | |
| is_smoking | Boolean | default false | |
| is_wheelchair_accessible | Boolean | default true | |
| has_baby_chair | Boolean | default false | |
| status | String(20) | default `available` | TableStatus enum |
| is_active | Boolean | default true | |
| priority | Integer | default 0 | |
| notes | String(500) | | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

**Enum `TableType`**: `regular` · `counter` · `booth` · `private` · `terrace`
**Enum `TableStatus`**: `available` · `occupied` · `reserved` · `cleaning`

### `table_assignments`

Links bookings to physical tables.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| booking_id | String(36) | FK → bookings.id, NOT NULL, INDEX | |
| table_id | String(36) | FK → tables.id, NOT NULL, INDEX | |
| assigned_at | DateTime(tz) | server_default now() | |
| seated_at | DateTime(tz) | | |
| cleared_at | DateTime(tz) | | |
| notes | String(500) | | |

### `table_availability`

Time-slot based availability calendar.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| table_id | String(36) | FK → tables.id, NOT NULL | |
| date | DateTime | NOT NULL, INDEX | |
| time_slot | String(5) | NOT NULL | `17:00` |
| is_available | Boolean | default true | |
| booking_id | String(36) | FK → bookings.id | |

---

## 5. Bookings

### `bookings`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| branch_customer_id | String(36) | FK → branch_customers.id | |
| date | Date | NOT NULL, INDEX | |
| time | String(5) | NOT NULL | `18:00` |
| guests | Integer | NOT NULL | |
| guest_name | String(255) | | Walk-in name |
| guest_phone | String(20) | | |
| guest_email | String(255) | | |
| status | String(20) | default `pending` | BookingStatus enum |
| note | String(1000) | | Customer note |
| staff_note | String(1000) | | Internal note |
| checked_in_at | DateTime(tz) | | |
| source | String(50) | default `web` | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

**Enum `BookingStatus`**: `pending` · `confirmed` · `checked_in` · `completed` · `cancelled` · `no_show`

---

## 6. Menu — Legacy

### `menu_items`

Original flat menu. Kept for backward compatibility.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| name | String(100) | NOT NULL | Japanese name |
| name_en | String(100) | | English name |
| description | Text | | |
| category | String(30) | NOT NULL, INDEX | MenuCategory enum |
| subcategory | String(50) | | |
| display_order | Integer | default 0 | |
| price | Numeric(10,0) | NOT NULL | Yen (no decimal) |
| tax_rate | Numeric(4,2) | default 10.0 | |
| image_url | String(500) | | |
| prep_time_minutes | Integer | default 5 | |
| kitchen_note | String(200) | | |
| is_available | Boolean | default true | |
| is_popular | Boolean | default false | |
| is_spicy | Boolean | default false | |
| is_vegetarian | Boolean | default false | |
| allergens | String(200) | | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

**Enum `MenuCategory`**: `beef` · `pork` · `chicken` · `seafood` · `sides` · `drinks` · `desserts`

---

## 7. Menu — Enhanced

### `item_categories`

Hierarchical categories (parent → child).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| code | String(50) | NOT NULL | |
| name | String(100) | NOT NULL | Japanese name |
| name_en | String(100) | | English name |
| description | Text | | |
| parent_id | String(36) | FK → self, nullable | Self-referential |
| display_order | Integer | default 0 | |
| icon | String(50) | | Emoji icon |
| image_url | String(500) | | |
| is_active | Boolean | default true | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

### `items`

Enhanced menu items with option support and stock tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| category_id | String(36) | FK → item_categories.id | |
| sku | String(50) | UNIQUE, nullable | |
| name | String(100) | NOT NULL | |
| name_en | String(100) | | |
| description | Text | | |
| base_price | Numeric(10,0) | NOT NULL | |
| tax_rate | Numeric(4,2) | default 10.0 | |
| prep_time_minutes | Integer | default 5 | |
| kitchen_printer | String(50) | | Routing |
| kitchen_note | Text | | |
| display_order | Integer | default 0 | |
| image_url | String(500) | | |
| is_available | Boolean | default true | |
| is_popular | Boolean | default false | |
| is_spicy | Boolean | default false | |
| is_vegetarian | Boolean | default false | |
| allergens | String(200) | | |
| has_options | Boolean | default false | |
| options_required | Boolean | default false | |
| track_stock | Boolean | default false | |
| stock_quantity | Integer | nullable | |
| low_stock_alert | Integer | nullable | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

---

## 8. Options System

### `item_option_groups`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| name | String(100) | NOT NULL | e.g. "焼き加減" |
| name_en | String(100) | | |
| description | Text | | |
| selection_type | String(20) | NOT NULL, default `single` | `single`/`multi` |
| min_selections | Integer | default 0 | |
| max_selections | Integer | default 1 | |
| display_order | Integer | default 0 | |
| is_active | Boolean | default true | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

### `item_options`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| group_id | String(36) | FK → item_option_groups.id, NOT NULL | |
| name | String(100) | NOT NULL | e.g. "レア" |
| name_en | String(100) | | |
| price_adjustment | Numeric(10,0) | default 0 | ¥ delta |
| is_default | Boolean | default false | |
| display_order | Integer | default 0 | |
| is_available | Boolean | default true | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

### `item_option_assignments`

Many-to-many: items ↔ option groups.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| item_id | String(36) | FK → items.id, NOT NULL | |
| option_group_id | String(36) | FK → item_option_groups.id, NOT NULL | |
| display_order | Integer | default 0 | |

---

## 9. Combos & Promotions

### `combos`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| code | String(50) | NOT NULL | |
| name | String(200) | NOT NULL | |
| name_en | String(200) | | |
| description | Text | | |
| discount_type | String(20) | NOT NULL | |
| discount_value | Numeric(10,2) | NOT NULL | |
| start_date | Date | nullable | |
| end_date | Date | nullable | |
| valid_hours_start | Time | nullable | |
| valid_hours_end | Time | nullable | |
| valid_days | String(50) | nullable | |
| max_uses_total | Integer | nullable | |
| max_uses_per_order | Integer | default 1 | |
| current_uses | Integer | default 0 | |
| min_order_amount | Numeric(10,0) | nullable | |
| display_order | Integer | default 0 | |
| image_url | String(500) | | |
| is_active | Boolean | default true | |
| is_featured | Boolean | default false | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

### `combo_items`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| combo_id | String(36) | FK → combos.id, NOT NULL | |
| item_id | String(36) | FK → items.id, nullable | |
| category_id | String(36) | FK → item_categories.id, nullable | |
| quantity | Integer | default 1 | |

### `promotions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| code | String(50) | NOT NULL | |
| name | String(200) | NOT NULL | |
| name_en | String(200) | | |
| description | Text | | |
| trigger_type | String(30) | NOT NULL | |
| trigger_item_id | String(36) | FK → items.id, nullable | |
| trigger_category_id | String(36) | FK → item_categories.id, nullable | |
| trigger_value | Numeric(10,0) | NOT NULL | |
| reward_type | String(30) | NOT NULL | |
| reward_item_id | String(36) | FK → items.id, nullable | |
| reward_value | Numeric(10,2) | nullable | |
| reward_quantity | Integer | default 1 | |
| start_date | Date | nullable | |
| end_date | Date | nullable | |
| valid_hours_start | Time | nullable | |
| valid_hours_end | Time | nullable | |
| valid_days | String(50) | nullable | |
| max_uses_per_order | Integer | default 1 | |
| max_uses_per_customer | Integer | nullable | |
| max_uses_total | Integer | nullable | |
| current_uses | Integer | default 0 | |
| stackable | Boolean | default false | |
| priority | Integer | default 0 | |
| display_order | Integer | default 0 | |
| image_url | String(500) | | |
| show_on_menu | Boolean | default true | |
| is_active | Boolean | default true | |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |

### `promotion_usages`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| promotion_id | String(36) | FK → promotions.id, NOT NULL | |
| order_id | String(36) | NOT NULL (no FK) | |
| customer_id | String(36) | nullable (no FK) | |
| discount_amount | Numeric(10,0) | NOT NULL | |
| applied_at | DateTime(tz) | server_default now() | |

---

## 10. Orders

### `orders`

⚠️ **No FK on `table_id`** — intentional for demo mode (works without seeded data).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| table_id | String(36) | NOT NULL, INDEX | **No FK** |
| session_id | String(36) | NOT NULL, INDEX | |
| order_number | Integer | NOT NULL | Sequential per session |
| status | String(20) | default `pending`, INDEX | OrderStatus enum |
| created_at | DateTime(tz) | server_default now() | |
| confirmed_at | DateTime(tz) | | |
| ready_at | DateTime(tz) | | |
| served_at | DateTime(tz) | | |

**Enum `OrderStatus`**: `pending` · `confirmed` · `preparing` · `ready` · `served` · `cancelled`

### `order_items`

⚠️ **No FK on `menu_item_id`** — denormalized `item_name`, `item_price` sent by frontend.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| order_id | String(36) | FK → orders.id, NOT NULL, INDEX | |
| menu_item_id | String(36) | NOT NULL | **No FK** |
| item_name | String(100) | NOT NULL | Denormalized |
| item_price | Numeric(10,0) | NOT NULL | Denormalized |
| quantity | Integer | default 1, NOT NULL | |
| notes | String(200) | | |
| status | String(20) | default `pending` | |
| created_at | DateTime(tz) | server_default now() | |
| prepared_at | DateTime(tz) | | |

### `table_sessions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| table_id | String(36) | FK → tables.id, NOT NULL, INDEX | |
| booking_id | String(36) | FK → bookings.id, nullable | |
| guest_count | Integer | default 1 | |
| started_at | DateTime(tz) | server_default now() | |
| ended_at | DateTime(tz) | | |
| is_paid | Boolean | default false | |
| total_amount | Numeric(10,0) | default 0 | |
| notes | Text | | |

---

## 11. Event Sourcing

### `order_events`

Append-only event log for table-order domain.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| event_type | String(50) | NOT NULL, INDEX | EventType enum |
| event_source | String(30) | NOT NULL, INDEX | EventSource enum |
| timestamp | DateTime(tz) | server_default now(), INDEX | |
| branch_code | String(50) | NOT NULL, INDEX | |
| table_id | String(36) | INDEX | |
| session_id | String(36) | INDEX | |
| order_id | String(36) | INDEX | |
| order_item_id | String(36) | INDEX | |
| actor_type | String(20) | | `customer`, `staff`, `system` |
| actor_id | String(36) | | |
| data | JSON | default {} | Event payload |
| correlation_id | String(36) | INDEX | Links related events |
| sequence_number | Integer | | Order within correlation |
| error_code | String(50) | | |
| error_message | Text | | |

**Composite Indexes:**
- `ix_order_events_session_time` (session_id, timestamp)
- `ix_order_events_order_time` (order_id, timestamp)
- `ix_order_events_correlation` (correlation_id, sequence_number)
- `ix_order_events_type_time` (event_type, timestamp)

**Enum `EventType`** (29 types):
`session_started` · `session_ended` · `order_placed` · `order_confirmed` · `order_cancelled` · `item_added` · `item_removed` · `item_preparing` · `item_ready` · `item_served` · `item_cancelled` · `payment_requested` · `payment_completed` · `call_staff` · `table_assigned` · `table_cleared` · `guest_checked_in` · `guest_checked_out` · `menu_viewed` · `menu_item_clicked` · `cart_updated` · `feedback_submitted` · `error_occurred` · `gateway_timeout` · `gateway_retry` · `gateway_success` · `gateway_failure` · `system_health_check` · `custom`

**Enum `EventSource`**: `table_order` · `kitchen` · `pos` · `dashboard` · `system` · `api`

---

## 12. Devices

### `devices`

Authorized hardware/browser devices for each app.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| name | String(100) | NOT NULL | `iPad-A1-Hirama` |
| device_type | String(20) | NOT NULL | DeviceType enum |
| token | String(64) | UNIQUE, NOT NULL, INDEX | QR payload (hex) |
| config | Text | default `{}` | JSON config |
| table_id | String(36) | FK → tables.id (SET NULL) | Table-order only |
| table_number | String(10) | nullable | Denormalized |
| status | String(20) | default `pending`, INDEX | DeviceStatus enum |
| device_fingerprint | String(64) | nullable | Browser hash |
| session_token | String(64) | UNIQUE, nullable, INDEX | Active session |
| session_expires_at | DateTime(tz) | | 365 days |
| last_seen_at | DateTime(tz) | | Heartbeat |
| activated_at | DateTime(tz) | | First login |
| created_at | DateTime(tz) | server_default now() | |
| updated_at | DateTime(tz) | onupdate now() | |
| created_by | String(100) | | Staff who registered |
| notes | String(500) | | |

**Enum `DeviceType`**: `table-order` · `kitchen` · `pos` · `checkin`
**Enum `DeviceStatus`**: `active` · `inactive` · `pending`

---

## 13. Check-in & Waiting

### `waiting_list`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| customer_name | String(255) | NOT NULL | |
| customer_phone | String(20) | | |
| guest_count | Integer | NOT NULL | |
| queue_number | Integer | NOT NULL | |
| status | String(20) | default `waiting`, INDEX | WaitingStatus enum |
| estimated_wait_minutes | Integer | | |
| created_at | DateTime(tz) | server_default now() | |
| called_at | DateTime(tz) | | |
| seated_at | DateTime(tz) | | |
| assigned_table_id | String(36) | FK → tables.id | |
| note | String(500) | | |

**Enum `WaitingStatus`**: `waiting` · `called` · `seated` · `cancelled` · `no_show`

### `checkin_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| event_type | String(50) | NOT NULL, INDEX | |
| booking_id | String(36) | FK → bookings.id | |
| waiting_id | String(36) | FK → waiting_list.id | |
| table_id | String(36) | FK → tables.id | |
| customer_name | String(255) | | |
| guest_count | Integer | | |
| event_data | Text | | JSON payload |
| created_at | DateTime(tz) | server_default now() | |

---

## 14. Chat & Insights

### `chat_messages`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_code | String(50) | NOT NULL, INDEX | |
| branch_customer_id | String(36) | FK → branch_customers.id | |
| session_id | String(100) | NOT NULL, INDEX | |
| role | String(20) | NOT NULL | `user`/`assistant` |
| content | String(5000) | NOT NULL | |
| insights_extracted | Boolean | default false | |
| created_at | DateTime(tz) | server_default now() | |

### `chat_insights`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String(36) | PK, uuid4 | |
| branch_customer_id | String(36) | FK → branch_customers.id | |
| message_id | String(36) | FK → chat_messages.id | |
| insight_type | String(50) | | |
| insight_value | String(500) | | |
| confidence | String(10) | | |
| created_at | DateTime(tz) | server_default now() | |

---

## ER Diagram

```
branches ─────────────┬──── staff ◄──── users (operators)
    │                 │
    │                 ├──── tables ◄──── devices
    │                 │       │              │
    │                 │       ├── table_assignments ◄── bookings
    │                 │       ├── table_availability
    │                 │       ├── table_sessions
    │                 │       └── waiting_list
    │                 │
    │                 ├──── menu_items (legacy)
    │                 │
    │                 ├──── item_categories ◄──── items
    │                 │                            │
    │                 │     item_option_groups ◄────┤ (via item_option_assignments)
    │                 │       └── item_options      │
    │                 │                             │
    │                 │     combos ◄── combo_items ─┘
    │                 │     promotions ◄── promotion_usages
    │                 │
    │                 └──── orders ◄── order_items
    │                        └── order_events
    │
    └── global_customers ── branch_customers
                              ├── customer_preferences
                              ├── chat_messages ── chat_insights
                              └── checkin_logs
```

---

## Seed Data Summary

| # | Table | CSV File | Rows | Description |
|---|-------|----------|------|-------------|
| 1 | branches | branches.csv | 5 | hirama, shinjuku, yaesu, shinagawa, yokohama |
| 2 | global_customers | customers.csv | 100 | Cross-branch customers |
| 3 | branch_customers | branch_customers.csv | 50 | Per-branch relationships |
| 4 | customer_preferences | customer_preferences.csv | 57 | Food preferences |
| 5 | staff | staff.csv | 34 | Employees across all branches |
| 6 | **users** | **users.csv** | **20** | **App operators (3 chef_mgr + 7 mgr + 10 staff)** |
| 7 | tables | tables.csv | 21 | Physical tables |
| 8 | bookings | bookings.csv | 25 | Reservations |
| 9 | menu_items | menu_items.csv | 40 | Legacy menu (hirama) |
| 10 | item_categories | item_categories.csv | 16 | 6 top + 10 sub-categories |
| 11 | items | items.csv | 63 | Enhanced menu items |
| 12 | item_option_groups | item_option_groups.csv | 7 | Option groups |
| 13 | item_options | item_options.csv | 28 | Option choices |
| 14 | item_option_assignments | item_option_assignments.csv | 29 | Item ↔ option links |
| 15 | combos | combos.csv | 9 | Combo deals |
| 16 | combo_items | combo_items.csv | 33 | Combo requirements |
| 17 | promotions | promotions.csv | 8 | Active promotions |

### Users Sample Data Breakdown

| Role | Count | Dashboard | Checkin | Table-Order | Kitchen | POS | Branch Scope |
|------|-------|-----------|---------|-------------|---------|-----|--------------|
| chef_manager | 3 | ✅ | ✅ | ✅ | ✅ | ✅ | Multi-branch / `*` |
| manager | 7 | ✅ | ✅ | ✅ | ✅ | ✅ | Single branch |
| staff | 10 | ❌ | varies | varies | varies | varies | Single branch |

**Staff role breakdown:**
- ホール (Hall): `can_checkin` + `can_table_order` + `can_kitchen`
- キッチン (Kitchen only): `can_kitchen` only
- レセプション (Reception): `can_checkin` + `can_table_order`
- レジ (Cashier): `can_table_order` + `can_pos`
