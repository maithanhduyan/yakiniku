# Backend Architecture - Yakiniku Jinan

> **Core Philosophy**: Customer Insights là tài sản quan trọng nhất. Mọi interaction đều được capture để hiểu khách hàng.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Existing)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Booking     │  │ Chat        │  │ Menu        │          │
│  │ Widget      │  │ Widget      │  │ Display     │          │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘          │
└─────────┼────────────────┼──────────────────────────────────┘
          │ JSON           │ JSON
          ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Python/FastAPI)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ /api/book   │  │ /api/chat   │  │ /admin/*    │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│  ┌─────────────────────────────────────────────────┐        │
│  │              Business Logic Layer                │        │
│  │  • Booking State Machine                        │        │
│  │  • Customer Insights Engine                     │        │
│  │  • Dashboard Analytics                          │        │
│  └──────────────────────┬──────────────────────────┘        │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐             │
│  │ SQLite/   │   │ LLM API   │   │ Redis     │             │
│  │ PostgreSQL│   │ (OpenAI)  │   │ (Cache)   │             │
│  └───────────┘   └───────────┘   └───────────┘             │
└─────────────────────────────────────────────────────────────┘
```

**Nguyên tắc:**
- LLM **KHÔNG** quyết định UI trực tiếp
- LLM gọi function để cập nhật state
- Backend quyết định UI tiếp theo
- Customer insights được tập trung 1 nơi (không LINE, không đa kênh phân tán)

---

## 2. Database Schema

```sql
-- Khách hàng (nguồn duy nhất của customer data)
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_visit TIMESTAMP,
    visit_count INTEGER DEFAULT 0,
    is_vip BOOLEAN DEFAULT FALSE
);

-- Customer Insights (tài sản cốt lõi)
CREATE TABLE customer_preferences (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    preference TEXT NOT NULL,      -- 'レバ刺し', '厚切り', etc.
    category TEXT,                 -- 'meat', 'cooking', 'allergy', 'occasion'
    note TEXT,
    confidence REAL DEFAULT 1.0,   -- 0.0-1.0 (AI inferred vs explicit)
    source TEXT DEFAULT 'chat',    -- 'chat', 'booking', 'manual'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Đặt bàn
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    date DATE NOT NULL,
    time TEXT NOT NULL,
    guests INTEGER NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, confirmed, cancelled, completed
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat history (để train model & phân tích)
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,            -- 'user' or 'assistant'
    content TEXT NOT NULL,
    insights_extracted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. API Endpoints

### Public (Frontend)

```python
POST /api/bookings              # Tạo đặt bàn
GET  /api/bookings/slots        # Lấy slot trống (date param)
POST /api/chat                  # Chat message → response + insight extraction
POST /api/customer/identify     # Nhận diện khách qua tên/phone
```

### Admin (Dashboard)

```python
GET  /admin/                           # Dashboard home
GET  /admin/api/bookings               # List bookings (date filter)
PUT  /admin/api/bookings/{id}/status   # Update status
GET  /admin/api/customers              # List customers (search, filter VIP)
GET  /admin/api/customers/{id}         # Customer detail + preferences
POST /admin/api/customers/{id}/note    # Add manual note/preference
GET  /admin/api/analytics              # Overview metrics
GET  /admin/api/insights/popular       # Popular preferences ranking
```

---

## 4. Restaurant Dashboard

### 4.1 Today's Bookings

```
┌─────────────────────────────────────────────────────────────┐
│  📅 本日の予約: 2026/02/04                         [Today] │
├─────────────────────────────────────────────────────────────┤
│  17:00  ██████ 渡辺様 (4名) ⭐VIP                          │
│         💬 レバ好き・生肉系                                 │
│  18:00  ████████ 田中様 (6名)                              │
│         🎂 記念日                                           │
│  19:00  ████ 新規 (2名)                                    │
│  19:30  ──── 空席 ────                                     │
│  20:00  ████ 鈴木様 (3名)                                  │
│         💬 ホルモン好き                                     │
├─────────────────────────────────────────────────────────────┤
│  総予約: 4件 | 総人数: 15名 | 空き: 2 slots               │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Customer Insights (Core Feature)

```
┌─────────────────────────────────────────────────────────────┐
│  👤 お客様インサイト                         [CSV出力]     │
├─────────────────────────────────────────────────────────────┤
│  🔍 [検索____________] [VIP ▼] [来店順 ▼]                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ⭐ 渡辺様                         来店: 12回        │   │
│  │ 📱 090-xxxx-xxxx                                    │   │
│  │ ┌─────────────────────────────────────────────┐     │   │
│  │ │ 🥩 レバ刺し  🥩 生肉系  🍖 厚切り           │     │   │
│  │ └─────────────────────────────────────────────┘     │   │
│  │ 📝 赤身より脂身を好む。日本酒と合わせる。           │   │
│  │ 🕐 最終: 2026/01/28 | 次回予約: 2026/02/04 17:00   │   │
│  │                                                     │   │
│  │ [詳細] [メモ追加] [+タグ追加]                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 田中様                            来店: 5回         │   │
│  │ 📱 080-xxxx-xxxx                                    │   │
│  │ 🥩 上タン塩  🍖 厚切り  🎂 記念日利用              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Analytics

```
┌─────────────────────────────────────────────────────────────┐
│  📊 分析                        [今週] [今月] [全期間]     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ 総予約       │ │ リピート率   │ │ VIP客数      │        │
│  │    156件     │ │    68%       │ │    23名      │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                             │
│  人気の好み TOP 5:                                         │
│  ████████████████████ 上タン塩 (45人)                      │
│  ██████████████████ 厚切り (38人)                          │
│  ████████████████ ハラミ (32人)                            │
│  ██████████████ ホルモン (28人)                            │
│  ████████████ レバー系 (24人)                              │
│                                                             │
│  ピーク時間: 18:00-19:00 (最混雑)                          │
│  平均滞在: 1.5時間 | 平均単価: ¥4,200                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. LLM Integration

### Function Calling Schema

```python
functions = [
    {
        "name": "update_booking",
        "description": "Cập nhật thông tin đặt bàn",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "time": {"type": "string"},
                "guests": {"type": "integer"},
                "name": {"type": "string"},
                "phone": {"type": "string"}
            }
        }
    },
    {
        "name": "extract_preference",
        "description": "Trích xuất sở thích từ hội thoại",
        "parameters": {
            "type": "object",
            "properties": {
                "preference": {"type": "string"},
                "category": {"type": "string", "enum": ["meat", "cooking", "allergy", "occasion"]},
                "confidence": {"type": "number"}
            }
        }
    }
]
```

### System Prompt

```text
Bạn là AI assistant cho nhà hàng Yakiniku Jinan.

MỤC TIÊU:
1. Hỗ trợ đặt bàn: date, time, guests, name, phone
2. Trả lời về menu, giờ mở cửa
3. QUAN TRỌNG: Trích xuất sở thích khách hàng

QUY TẮC:
- Trả lời tiếng Nhật, lịch sự
- KHÔNG bịa thông tin
- Khi khách nhắc món yêu thích → gọi extract_preference
- Chỉ hỏi 1 câu/lần
- Backend quyết định UI
```

---

## 6. Implementation Phases

### Phase 1: Core (Week 1-2)
- [ ] FastAPI + SQLite setup
- [ ] Booking CRUD API
- [ ] Customer identification by phone
- [ ] Basic admin: booking list

### Phase 2: Chat Backend (Week 2-3)
- [ ] Connect chat widget → backend
- [ ] LLM with function calling
- [ ] Auto-extract preferences
- [ ] Chat history storage

### Phase 3: Dashboard (Week 3-4)
- [ ] Booking calendar view
- [ ] Customer insights panel
- [ ] Manual tagging UI
- [ ] CSV export

### Phase 4: Analytics (Week 4-5)
- [ ] Metrics dashboard
- [ ] Popular preferences chart
- [ ] VIP customer tracking

---

## 7. Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Backend | FastAPI | Async, type hints, auto docs |
| Database | SQLite → PostgreSQL | Simple start, scale later |
| LLM | OpenAI API | Reliable function calling |
| Dashboard | HTMX + Jinja2 | No SPA complexity |
| Auth | Session-based | Simple admin login |

---

## 8. Key Design Decisions

1. **No LINE Integration**: Tập trung insights vào 1 hệ thống duy nhất để dễ thống kê
2. **Phone as Identifier**: Khách nhận diện qua SĐT, không cần đăng ký
3. **Preference Confidence**: AI-extracted có confidence thấp hơn manual
4. **Backend-Driven UI**: LLM không render UI, chỉ extract data
