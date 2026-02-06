# 🔭 GPT (Visionary) — Round 1 Review | 2026-02-06

## Tổng quan quan điểm

Trong 5-10 năm tới, trải nghiệm yakiniku sẽ chuyển từ **"iPad đặt món"** sang **"Digital Dining Companion"** — một hệ thống thông minh hiểu ngữ cảnh bữa ăn, dự đoán nhu cầu khách hàng, và orchestrate toàn bộ dining journey từ lúc ngồi xuống đến lúc rời bàn. Event sourcing không chỉ là audit log mà là **nền tảng cho AI-driven personalization**, predictive kitchen management, và cross-location intelligence.

Với kiến trúc hiện tại — Vanilla JS offline-first + FastAPI event sourcing — chúng ta đang ở vị trí rất thuận lợi. Vanilla JS cho phép kiểm soát hoàn toàn performance trên iPad (không có framework overhead), offline-first đảm bảo reliability trong môi trường nhà hàng (Wi-Fi không ổn định), và event sourcing tạo ra **data goldmine** cho business intelligence. Điều quan trọng là thiết kế session lifecycle đúng từ đầu — vì mỗi event được ghi lại hôm nay sẽ trở thành training data cho AI recommendations 2-3 năm sau.

Tầm nhìn 20 năm: mỗi nhà hàng Yakiniku Jinan sẽ là một **autonomous dining ecosystem** — iPad biết bạn thích thịt nướng medium-rare, biết khi nào grill cần thay, biết nhóm 6 người nên được suggest thêm 2 portion nữa vào phút thứ 40 của bữa ăn, và biết rằng khách hàng VIP nên được chào đón bằng tên ngay khi check-in.

---

## Q1: Session Lifecycle Design

### Tầm nhìn: Session as a First-Class Entity

Session không chỉ là container cho orders — nó là **complete narrative của một bữa ăn**. Mỗi session kể một câu chuyện: ai đến, họ ăn gì, bao lâu, hài lòng không, và bao giờ trở lại.

### Phase Design (6 phases + 2 implicit states)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TABLE SESSION LIFECYCLE                          │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │  READY   │──▶│ WELCOME  │──▶│ ORDERING │──▶│ DINING   │        │
│  │ (待機中)  │   │(ようこそ) │   │ (注文中)  │   │ (お食事中) │        │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘        │
│       ▲                                             │              │
│       │          ┌──────────┐   ┌──────────┐        │              │
│       └──────────│ CLEANING │◀──│ PAYMENT  │◀───────┘              │
│                  │ (片付け中) │   │ (お会計)  │                      │
│                  └──────────┘   └──────────┘                       │
│                                                                     │
│  Implicit: OFFLINE_RECOVERY, ERROR_STATE                           │
└─────────────────────────────────────────────────────────────────────┘
```

### Chi tiết từng Phase

#### Phase 0: READY (待機中) — Chờ khách
```
┌─────────────────────────────────────────────┐
│                                             │
│         🏮  焼肉 じなん  🏮                  │
│                                             │
│          YAKINIKU JINAN                      │
│          ── HIRAMA ──                        │
│                                             │
│     ┌───────────────────────────┐           │
│     │                           │           │
│     │   テーブル T5              │           │
│     │   Table T5                │           │
│     │                           │           │
│     │   🔥 タッチしてスタート     │           │
│     │      Touch to Start       │           │
│     │                           │           │
│     └───────────────────────────┘           │
│                                             │
│    ┌─────┐  ┌─────┐  ┌─────┐              │
│    │ JP  │  │ EN  │  │ VI  │   ← i18n     │
│    └─────┘  └─────┘  └─────┘              │
│                                             │
│  ───────────────────────────────            │
│  🔒 スタッフモード (長押し5秒)               │
│     Staff Mode (hold 5s)                    │
└─────────────────────────────────────────────┘
```

**Behaviour:**
- Full-screen welcome, branding nổi bật
- Auto-rotate promotional images/videos (từ `branch` config)
- Language selector hiển thị sẵn
- **Staff lock**: Long-press 5 giây góc dưới → nhập PIN → vào Staff Mode (xem analytics, reset session, config)
- **Trigger → WELCOME**: Khách touch anywhere hoặc staff scan QR check-in

**Events emitted:**
```javascript
// Khi khách touch
{ type: "SESSION_STARTED", source: "TABLE_ORDER", data: { trigger: "customer_touch" } }
// Khi staff check-in
{ type: "SESSION_STARTED", source: "SYSTEM", data: { trigger: "staff_checkin", booking_id: "..." } }
```

#### Phase 1: WELCOME (ようこそ) — Thiết lập session
```
┌─────────────────────────────────────────────┐
│  ようこそ！ Welcome!          テーブル T5    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  何名様ですか？                      │    │
│  │  How many guests?                   │    │
│  │                                     │    │
│  │  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐   │    │
│  │  │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5 │   │    │
│  │  └───┘ └───┘ └───┘ └───┘ └───┘   │    │
│  │  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐   │    │
│  │  │ 6 │ │ 7 │ │ 8 │ │ 9 │ │10+│   │    │
│  │  └───┘ └───┘ └───┘ └───┘ └───┘   │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  📋 コースをお選びください              │    │
│  │  Select your plan:                  │    │
│  │                                     │    │
│  │  ┌─────────────┐ ┌─────────────┐   │    │
│  │  │ 🍖 食べ放題  │ │ 📜 アラカルト │   │    │
│  │  │ All-you-can  │ │ À la carte  │   │    │
│  │  │ ¥3,980/人   │ │             │   │    │
│  │  │  90 min     │ │  自由注文    │   │    │
│  │  └─────────────┘ └─────────────┘   │    │
│  └─────────────────────────────────────┘    │
│                                             │
│     ┌──────────────────────────────┐        │
│     │     ▶ メニューへ進む          │        │
│     │       Go to Menu             │        │
│     └──────────────────────────────┘        │
└─────────────────────────────────────────────┘
```

**Behaviour:**
- Số khách: required (default highlight 2 hoặc từ booking data)
- Course selection: tabehoudai vs à la carte (ảnh hưởng toàn bộ UX sau đó)
- Nếu có booking link: auto-fill guest count, show tên khách "田中様、いらっしゃいませ"
- Timeout 3 phút không tương tác → fallback về READY
- **Trigger → ORDERING**: Tap "Go to Menu"

**Events emitted:**
```javascript
{
  type: "SESSION_STARTED",
  data: {
    guest_count: 4,
    dining_mode: "tabehoudai", // or "alacarte"
    plan_id: "plan_90min_3980",
    language: "ja",
    has_booking: true,
    booking_id: "booking_xxx"
  }
}
```

#### Phase 2: ORDERING (注文中) — Đây là app hiện tại, enhanced
```
┌─────────────────────────────────────────────────────────┐
│ 🏮 T5 │ 4名 │ 食べ放題 90min │ ⏱ 52:30 │ 🛎 │ 📜 │ 🛒3│
├────────┼────────────────────────────────────────────────┤
│ 🥩    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│ 肉     │  │ 和牛 │ │厚切り│ │ 特選 │ │カルビ│ │上ロース│   │
│        │  │ハラミ│ │ タン │ │カルビ│ │     │ │      │   │
│ 🍺    │  │¥1800│ │¥2200│ │¥1800│ │¥1500│ │ ¥1700│   │
│ 飲物   │  │ 🔥  │ │ 🔥  │ │ 🔥  │ │     │ │      │   │
│        │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘   │
│ 🥗    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│ サラダ  │  │ロース│ │ホルモ│ │ 特選 │ │豚カル│ │鶏モモ  │   │
│        │  │     │ │  ン │ │盛合せ│ │  ビ │ │      │   │
│ 🍚    │  │¥1400│ │¥1400│ │¥4500│ │ ¥900│ │ ¥800 │   │
│ ごはん  │  │     │ │     │ │ ⭐  │ │     │ │      │   │
│        │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘   │
│ 🍲    │                                              │
│ 一品   │  ◀  1 / 1  ▶                                │
│        ├────────────────────────────────────────────────┤
│ 🍨    │ 💡 タンを注文した方に: ネギ塩追加はいかが？      │
│ デザート │    Recommended: Add green onion salt topping   │
│        │                                    [＋追加]    │
│ 🍱    ├────────────────────────────────────────────────┤
│ セット  │ 🛒 3品  ¥5,800        [カートを見る ▶]       │
└────────┴────────────────────────────────────────────────┘
```

**Enhanced features (5-year vision):**

1. **Smart Header Bar**: Session timer (đặc biệt quan trọng cho tabehoudai 90min), guest count, dining mode badge
2. **Contextual Recommendations Strip**: AI-powered suggestion dựa trên cart hiện tại + historical data
3. **Tabehoudai Timer**: Countdown prominent, warnings at 15min/5min remaining
4. **Order Pacing Indicator**: "Bạn đã order 3 lần, trung bình nhóm 4 người order 5-6 lần"

**State transitions:**
- Luôn ở phase này cho đến khi gọi bill (CALL_BILL) hoặc staff trigger payment
- Cart và history persist qua page refresh
- **Trigger → DINING**: Tự động — phase này merge với DINING (xem giải thích bên dưới)

> **Quan điểm kiến trúc**: ORDERING và DINING không nên là 2 phase riêng biệt trên iPad. Trong nhà hàng yakiniku, khách gọi món liên tục trong suốt bữa ăn. iPad luôn ở trạng thái "sẵn sàng nhận order". Sự khác biệt giữa "đang order" và "đang ăn" chỉ có ý nghĩa về mặt analytics (events), không phải UI.

#### Phase 3: PAYMENT (お会計) — Chờ thanh toán
```
┌─────────────────────────────────────────────┐
│  🏮 T5 │ お会計  │ Check                    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  本日のご注文 / Today's Orders       │    │
│  │                                     │    │
│  │  🥩 和牛ハラミ         ×2   ¥3,600  │    │
│  │  🥩 厚切りタン塩       ×1   ¥2,200  │    │
│  │  🍺 生ビール           ×4   ¥2,400  │    │
│  │  🥗 チョレギサラダ     ×1     ¥600  │    │
│  │  🍚 ライス             ×3     ¥600  │    │
│  │  🍨 バニラアイス       ×2     ¥800  │    │
│  │  ─────────────────────────────────  │    │
│  │  小計                       ¥10,200 │    │
│  │  消費税 (10%)                ¥1,020 │    │
│  │  ─────────────────────────────────  │    │
│  │  合計 / Total            ¥11,220    │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  スタッフがお会計に参ります            │    │
│  │  Staff will assist with payment      │    │
│  │  🔄 しばらくお待ちください...          │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌──────────┐  ┌──────────────────────┐    │
│  │ 📋 追加注文 │  │ ⭐ ご意見 / Feedback │    │
│  │ Add more   │  │                     │    │
│  └──────────┘  └──────────────────────┘    │
│                                             │
│  ご来店ありがとうございました 🙏              │
└─────────────────────────────────────────────┘
```

**Behaviour:**
- Triggered by: customer CALL_BILL, hoặc POS staff initiate checkout
- Hiển thị full order summary grouped by order time
- "追加注文" button cho phép quay lại ORDERING (edge case: quên gọi dessert)
- **Feedback form**: 5-star rating + optional comment (captured as event)
- iPad **locked khỏi ordering mới** (trừ khi tap "Add more")
- **Trigger → CLEANING**: POS gửi `SESSION_PAID` event qua WebSocket

**Events emitted:**
```javascript
{ type: "CALL_BILL", data: { total_preview: 11220 } }
{ type: "SESSION_PAID", source: "POS", data: {
    payment_method: "credit_card",
    total: 11220,
    tip: 0
}}
```

#### Phase 4: CLEANING (片付け中) — Lock screen dọn bàn
```
┌─────────────────────────────────────────────┐
│                                             │
│                                             │
│           🧹                                │
│                                             │
│         片付け中                             │
│         Cleaning in Progress                │
│                                             │
│         ─────────────────                   │
│                                             │
│         テーブル T5                          │
│         Table T5                            │
│                                             │
│                                             │
│                                             │
│                                             │
│                                             │
│  ───────────────────────────────            │
│  🔒 スタッフのみ解除可能                     │
│     Staff only: hold 5s + PIN to unlock     │
│                                             │
│  📊 Session: 87分 │ 6注文 │ ¥11,220        │
└─────────────────────────────────────────────┘
```

**Behaviour:**
- **Completely locked** — không có interaction nào cho khách
- Background hiển thị session summary cho staff reference
- Chỉ unlock bằng staff long-press + PIN
- **Trigger → READY**: Staff unlock (log `SESSION_ENDED` event)

**Events emitted:**
```javascript
{ type: "SESSION_ENDED", source: "POS", data: {
    duration_minutes: 87,
    total_orders: 6,
    total_amount: 11220,
    guest_count: 4,
    dining_mode: "alacarte"
}}
```

### Transition Matrix

| From | To | Trigger | Auto/Manual | Event |
|------|----|---------|-------------|-------|
| READY | WELCOME | Customer touch / Staff scan | Manual | SESSION_STARTED |
| WELCOME | ORDERING | "Go to Menu" tap | Manual | (part of SESSION_STARTED) |
| WELCOME | READY | 3min timeout | Auto | (no event — session not yet created) |
| ORDERING | PAYMENT | CALL_BILL or POS trigger | Manual | CALL_BILL |
| PAYMENT | ORDERING | "Add more" tap | Manual | ITEM_ADDED |
| PAYMENT | CLEANING | SESSION_PAID from POS | Auto (WS) | SESSION_PAID |
| CLEANING | READY | Staff unlock + PIN | Manual | SESSION_ENDED |

### Edge Cases

**Khách bỏ về (walkout):**
```javascript
// Detected by: no interaction for 30+ minutes while in ORDERING phase
// OR: Staff manually triggers via Staff Mode
{ type: "SESSION_ENDED", data: {
    reason: "walkout",
    unpaid_amount: 5400,
    alert_sent_to: "pos"
}}
// iPad → CLEANING phase (staff needs to handle)
```

**Hệ thống crash / Power loss:**
```javascript
// On restart, check localStorage for active session
const activeSession = localStorage.getItem(`yakiniku_active_session_${TABLE_ID}`);
if (activeSession) {
    const session = JSON.parse(activeSession);
    // Replay events to rebuild state
    const events = JSON.parse(localStorage.getItem(`yakiniku_events_${session.id}`) || '[]');
    // Determine phase from last event
    const lastEvent = events[events.length - 1];
    // Resume from correct phase
    restoreSessionFromEvents(events);
}
```

**Đổi bàn:**
```javascript
// Staff Mode action: "Transfer Session"
{ type: "SESSION_ENDED", data: { reason: "table_transfer", transfer_to: "T8" }}
// New session started at T8 with reference to old session
{ type: "SESSION_STARTED", source: "SYSTEM", data: {
    transferred_from: "T5",
    original_session_id: "session_xxx",
    carry_over_orders: true
}}
```

**Nhiều nhóm khách cùng bàn (rare, large tables):**
```javascript
// Future: Sub-sessions within a session
// Each "seat group" can have independent carts but shared bill
// For now: single session per table, split bill handled at POS
```

---

## Q2: Event Sourcing Strategy (Client-side localStorage)

### Tầm nhìn: Client-side Event Store as Offline-First Foundation

localStorage trên iPad không chỉ là cache — nó là **local event store** cho phép app hoạt động hoàn toàn offline và sync khi có mạng. Đây là pattern tương tự **CRDTs** (Conflict-free Replicated Data Types) trong distributed systems.

### Schema Design

```javascript
// ============ localStorage Key Structure ============
//
// yakiniku_device_{TABLE_ID}          → Device config (persistent)
// yakiniku_active_session_{TABLE_ID}  → Current active session metadata
// yakiniku_events_{SESSION_ID}        → Event log for a session
// yakiniku_cart_{SESSION_ID}          → Current cart state
// yakiniku_sync_queue                 → Events pending sync to backend
// yakiniku_sessions_index_{TABLE_ID}  → Index of all sessions on this device

// ============ Device Config ============
const deviceConfig = {
    table_id: "T5",
    branch_code: "hirama",
    device_id: "ipad_hirama_t5_001",  // Unique per physical device
    registered_at: "2026-01-15T10:00:00Z",
    last_sync: "2026-02-06T19:45:00Z",
    firmware_version: "1.2.0"
};

// ============ Active Session ============
const activeSession = {
    id: "session_1738856400_abc123def",
    table_id: "T5",
    branch_code: "hirama",
    phase: "ordering",        // ready|welcome|ordering|payment|cleaning
    guest_count: 4,
    dining_mode: "tabehoudai", // tabehoudai|alacarte
    plan_id: "plan_90min_3980",
    language: "ja",
    started_at: "2026-02-06T18:30:00Z",
    booking_id: null,
    order_count: 0,
    total_amount: 0
};

// ============ Event Format ============
const eventSchema = {
    id: "evt_1738856400123_x7k9m",    // Unique, sortable
    type: "ORDER_CREATED",             // Maps to backend EventType
    source: "TABLE_ORDER",             // Maps to backend EventSource
    timestamp: "2026-02-06T18:35:22.456Z",
    session_id: "session_1738856400_abc123def",
    table_id: "T5",
    branch_code: "hirama",

    // Event-specific payload
    data: {
        order_id: "local_ord_001",     // Local ID until synced
        items: [
            { menu_item_id: "menu-001", name: "和牛ハラミ", price: 1800, qty: 2 },
            { menu_item_id: "menu-002", name: "厚切りタン塩", price: 2200, qty: 1 }
        ],
        total: 5800
    },

    // Sync metadata
    _synced: false,                    // Has been sent to backend?
    _sync_attempts: 0,                 // Retry count
    _server_id: null,                  // Backend event ID after sync
    _correlation_id: "corr_abc123"     // Links related events
};

// ============ Session Index (per device) ============
const sessionsIndex = [
    {
        id: "session_1738856400_abc123def",
        started_at: "2026-02-06T18:30:00Z",
        ended_at: null,                // null = active
        phase: "ordering",
        guest_count: 4,
        event_count: 12,
        total_amount: 5800,
        synced: false
    },
    {
        id: "session_1738770000_prev456",
        started_at: "2026-02-05T19:00:00Z",
        ended_at: "2026-02-05T21:15:00Z",
        phase: "completed",
        guest_count: 2,
        event_count: 8,
        total_amount: 4200,
        synced: true
    }
];
```

### Event ID Generation (Client-side, sortable, unique)

```javascript
/**
 * Generate a sortable, unique event ID
 * Format: evt_{timestamp_ms}_{random_5char}
 * Sortable by timestamp, unique across devices
 */
function generateEventId() {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 5);
    return `evt_${timestamp}_${random}`;
}

/**
 * Generate session ID with device context
 * Format: ses_{table}_{timestamp}_{random}
 */
function generateSessionId(tableId) {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    return `ses_${tableId}_${timestamp}_${random}`;
}
```

### Client-side Event Store Implementation

```javascript
/**
 * EventStore - Client-side event sourcing engine
 * Manages localStorage-based event log with sync capabilities
 */
class ClientEventStore {
    constructor(tableId, branchCode) {
        this.tableId = tableId;
        this.branchCode = branchCode;
        this.syncQueue = this._loadSyncQueue();
        this.listeners = new Map(); // event_type → [callbacks]
    }

    /**
     * Append an event to the local store
     * @returns {object} The created event
     */
    append(eventType, data = {}, source = 'TABLE_ORDER') {
        const session = this.getActiveSession();

        const event = {
            id: generateEventId(),
            type: eventType,
            source: source,
            timestamp: new Date().toISOString(),
            session_id: session?.id || null,
            table_id: this.tableId,
            branch_code: this.branchCode,
            data: data,
            _synced: false,
            _sync_attempts: 0,
            _server_id: null,
            _correlation_id: data._correlation_id || generateEventId()
        };

        // Append to session event log
        if (session) {
            const key = `yakiniku_events_${session.id}`;
            const events = JSON.parse(localStorage.getItem(key) || '[]');
            events.push(event);
            localStorage.setItem(key, JSON.stringify(events));
        }

        // Add to sync queue
        this.syncQueue.push(event);
        this._saveSyncQueue();

        // Notify listeners
        this._emit(eventType, event);

        // Attempt immediate sync if online
        if (navigator.onLine) {
            this.syncNext();
        }

        return event;
    }

    /**
     * Replay events to rebuild state
     * @param {string} sessionId - Session to replay
     * @returns {object} Reconstructed state
     */
    replay(sessionId) {
        const events = JSON.parse(
            localStorage.getItem(`yakiniku_events_${sessionId}`) || '[]'
        );

        let state = {
            phase: 'ready',
            guest_count: 0,
            dining_mode: null,
            orders: [],
            current_cart: [],
            total_amount: 0,
            calls: []
        };

        for (const event of events) {
            state = this._applyEvent(state, event);
        }

        return state;
    }

    /**
     * Apply a single event to state (reducer pattern)
     */
    _applyEvent(state, event) {
        switch (event.type) {
            case 'SESSION_STARTED':
                return {
                    ...state,
                    phase: 'ordering',
                    guest_count: event.data.guest_count || state.guest_count,
                    dining_mode: event.data.dining_mode || state.dining_mode,
                    started_at: event.timestamp
                };

            case 'ORDER_CREATED':
                return {
                    ...state,
                    orders: [...state.orders, {
                        id: event.data.order_id,
                        items: event.data.items,
                        total: event.data.total,
                        time: event.timestamp
                    }],
                    total_amount: state.total_amount + (event.data.total || 0)
                };

            case 'ITEM_ADDED':
                return {
                    ...state,
                    current_cart: [...state.current_cart, event.data.item]
                };

            case 'ITEM_REMOVED':
                return {
                    ...state,
                    current_cart: state.current_cart.filter(
                        i => i.id !== event.data.item_id
                    )
                };

            case 'CALL_BILL':
                return { ...state, phase: 'payment' };

            case 'SESSION_PAID':
                return { ...state, phase: 'cleaning', is_paid: true };

            case 'SESSION_ENDED':
                return { ...state, phase: 'completed', ended_at: event.timestamp };

            case 'CALL_STAFF':
            case 'CALL_WATER':
                return {
                    ...state,
                    calls: [...state.calls, {
                        type: event.type,
                        time: event.timestamp,
                        acknowledged: false
                    }]
                };

            case 'CALL_ACKNOWLEDGED':
                const calls = [...state.calls];
                const lastUnacked = calls.findLastIndex(c => !c.acknowledged);
                if (lastUnacked >= 0) calls[lastUnacked].acknowledged = true;
                return { ...state, calls };

            default:
                return state;
        }
    }

    // ============ Sync Engine ============

    /**
     * Sync pending events to backend (one at a time, ordered)
     * Uses exponential backoff on failure
     */
    async syncNext() {
        if (this.syncQueue.length === 0) return;
        if (this._syncing) return; // Prevent parallel syncs

        this._syncing = true;

        try {
            const event = this.syncQueue[0];

            const response = await fetch(`${CONFIG.API_URL}/tableorder/events/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    event_type: event.type.toLowerCase().replace('_', '.'),
                    event_source: event.source.toLowerCase().replace('_', '-'),
                    branch_code: event.branch_code,
                    table_id: event.table_id,
                    session_id: event.session_id,
                    data: event.data,
                    correlation_id: event._correlation_id,
                    // Client timestamp for ordering
                    client_timestamp: event.timestamp
                })
            });

            if (response.ok) {
                const serverEvent = await response.json();
                // Mark as synced
                event._synced = true;
                event._server_id = serverEvent.id;
                // Remove from queue
                this.syncQueue.shift();
                this._saveSyncQueue();
                // Update in session log
                this._updateEventInLog(event);
                // Continue syncing
                this._syncing = false;
                if (this.syncQueue.length > 0) {
                    setTimeout(() => this.syncNext(), 100);
                }
            } else {
                throw new Error(`Sync failed: ${response.status}`);
            }
        } catch (error) {
            const event = this.syncQueue[0];
            event._sync_attempts++;
            this._saveSyncQueue();

            // Exponential backoff: 1s, 2s, 4s, 8s, 16s, max 30s
            const delay = Math.min(1000 * Math.pow(2, event._sync_attempts - 1), 30000);
            console.warn(`[EventStore] Sync failed, retry in ${delay}ms`, error);

            this._syncing = false;
            setTimeout(() => this.syncNext(), delay);
        }
    }

    /**
     * Batch sync all pending events (for reconnection scenarios)
     */
    async syncAll() {
        if (this.syncQueue.length === 0) return;

        try {
            const response = await fetch(`${CONFIG.API_URL}/tableorder/events/batch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    events: this.syncQueue.map(e => ({
                        event_type: e.type.toLowerCase().replace('_', '.'),
                        event_source: e.source.toLowerCase().replace('_', '-'),
                        branch_code: e.branch_code,
                        table_id: e.table_id,
                        session_id: e.session_id,
                        data: e.data,
                        correlation_id: e._correlation_id,
                        client_timestamp: e.timestamp
                    }))
                })
            });

            if (response.ok) {
                const results = await response.json();
                // Mark all as synced
                this.syncQueue = [];
                this._saveSyncQueue();
            }
        } catch (error) {
            console.warn('[EventStore] Batch sync failed', error);
        }
    }

    // ============ Sync Queue Persistence ============

    _loadSyncQueue() {
        try {
            return JSON.parse(localStorage.getItem('yakiniku_sync_queue') || '[]');
        } catch { return []; }
    }

    _saveSyncQueue() {
        localStorage.setItem('yakiniku_sync_queue', JSON.stringify(this.syncQueue));
    }

    _updateEventInLog(event) {
        if (!event.session_id) return;
        const key = `yakiniku_events_${event.session_id}`;
        const events = JSON.parse(localStorage.getItem(key) || '[]');
        const idx = events.findIndex(e => e.id === event.id);
        if (idx >= 0) {
            events[idx] = event;
            localStorage.setItem(key, JSON.stringify(events));
        }
    }

    // ============ Session Management ============

    getActiveSession() {
        try {
            const raw = localStorage.getItem(`yakiniku_active_session_${this.tableId}`);
            return raw ? JSON.parse(raw) : null;
        } catch { return null; }
    }

    setActiveSession(session) {
        localStorage.setItem(
            `yakiniku_active_session_${this.tableId}`,
            JSON.stringify(session)
        );
    }

    clearActiveSession() {
        localStorage.removeItem(`yakiniku_active_session_${this.tableId}`);
    }

    // ============ Event Listeners ============

    on(eventType, callback) {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, []);
        }
        this.listeners.get(eventType).push(callback);
    }

    _emit(eventType, event) {
        const callbacks = this.listeners.get(eventType) || [];
        callbacks.forEach(cb => cb(event));
        // Also emit wildcard
        const wildcardCallbacks = this.listeners.get('*') || [];
        wildcardCallbacks.forEach(cb => cb(event));
    }
}
```

### Sync Strategy: Hybrid Real-time + Batch

```
┌─────────────────────────────────────────────────────┐
│              SYNC STRATEGY DIAGRAM                   │
│                                                       │
│  Client (iPad)              Backend (FastAPI)         │
│  ─────────────              ───────────────           │
│                                                       │
│  [Event Created] ──────────▶ POST /events/            │
│       │                         │                     │
│       │  if online:             │  ✓ 201              │
│       │  sync immediately       │                     │
│       │                         │                     │
│       │  if offline:            │                     │
│       │  queue in localStorage  │                     │
│       │       │                 │                     │
│       │       ▼                 │                     │
│       │  [Reconnect]           │                     │
│       │       │                 │                     │
│       │       ▼                 │                     │
│       │  POST /events/batch ──▶│  Batch insert        │
│       │                         │  Dedup by client_id  │
│       │                         │                     │
│  [WS Message] ◀────────────── │  Push updates         │
│       │                         │  (from kitchen/POS)  │
│       ▼                         │                     │
│  [Update local state]           │                     │
└─────────────────────────────────────────────────────┘
```

**Sync rules:**
1. **Critical events** (ORDER_CREATED, CALL_BILL, SESSION_PAID): Sync immediately, show spinner until confirmed
2. **Informational events** (ITEM_ADDED, ITEM_REMOVED, WS_CONNECTED): Batch sync every 30 seconds
3. **Analytics events** (page views, interaction timing): Batch sync at session end
4. **Offline**: Queue everything, batch sync on reconnect

### Retention Policy

```javascript
/**
 * Session Retention Manager
 * Runs on app startup and after each session ends
 */
class RetentionManager {
    static POLICIES = {
        ACTIVE: Infinity,          // Never delete active session
        COMPLETED_SYNCED: 48,      // 48 hours after session end if synced
        COMPLETED_UNSYNCED: 168,   // 7 days if not yet synced (保険)
        MAX_SESSIONS_PER_DEVICE: 50,  // Hard limit
        MAX_STORAGE_MB: 4          // localStorage ~5MB limit, keep 1MB buffer
    };

    static cleanup(tableId) {
        const indexKey = `yakiniku_sessions_index_${tableId}`;
        const index = JSON.parse(localStorage.getItem(indexKey) || '[]');
        const now = Date.now();
        const toDelete = [];

        for (const session of index) {
            if (!session.ended_at) continue; // Skip active

            const endedAt = new Date(session.ended_at).getTime();
            const hoursElapsed = (now - endedAt) / (1000 * 60 * 60);
            const maxHours = session.synced
                ? this.POLICIES.COMPLETED_SYNCED
                : this.POLICIES.COMPLETED_UNSYNCED;

            if (hoursElapsed > maxHours) {
                toDelete.push(session.id);
            }
        }

        // Also enforce MAX_SESSIONS_PER_DEVICE
        const completedSynced = index
            .filter(s => s.ended_at && s.synced)
            .sort((a, b) => new Date(a.ended_at) - new Date(b.ended_at));

        while (index.length - toDelete.length > this.POLICIES.MAX_SESSIONS_PER_DEVICE) {
            const oldest = completedSynced.shift();
            if (oldest && !toDelete.includes(oldest.id)) {
                toDelete.push(oldest.id);
            } else break;
        }

        // Delete
        for (const sessionId of toDelete) {
            localStorage.removeItem(`yakiniku_events_${sessionId}`);
            localStorage.removeItem(`yakiniku_cart_${sessionId}`);
        }

        // Update index
        const remaining = index.filter(s => !toDelete.includes(s.id));
        localStorage.setItem(indexKey, JSON.stringify(remaining));

        console.log(`[Retention] Cleaned up ${toDelete.length} sessions, ${remaining.length} remaining`);
    }
}
```

### Offline Conflict Resolution

```javascript
/**
 * Conflict Resolution Strategy: "Client Wins + Server Reconciles"
 *
 * Rationale: In a restaurant, the iPad IS the source of truth for what
 * the customer ordered. Server can enrich but never reject client events.
 *
 * Conflicts only arise in specific scenarios:
 */

const ConflictResolution = {
    // Scenario 1: Same order submitted twice (network glitch)
    // Solution: Idempotency key (correlation_id)
    ORDER_DUPLICATE: 'server_dedup_by_correlation_id',

    // Scenario 2: Menu price changed between offline order and sync
    // Solution: Use price at time of order (snapshot in event data)
    PRICE_MISMATCH: 'client_price_wins_flag_for_review',

    // Scenario 3: Item sold out between offline order and sync
    // Solution: Accept order, notify kitchen, staff handles manually
    ITEM_UNAVAILABLE: 'accept_and_flag',

    // Scenario 4: Session ended on POS but iPad still has orders in queue
    // Solution: Still sync the events (historical record), but mark as late
    SESSION_ALREADY_ENDED: 'sync_as_late_events',

    // Scenario 5: Clock drift between iPad and server
    // Solution: Server records both client_timestamp and server_timestamp
    CLOCK_DRIFT: 'dual_timestamp'
};
```

---

## Q3: Yakiniku-specific UX Features

### Tầm nhìn 5 năm: "Intelligent Yakiniku Companion"

Yakiniku là unique trong ngành F&B: khách hàng **tự nấu** (grill) thức ăn, gọi món **nhiều rounds**, và bữa ăn kéo dài 60-120 phút. Đây là cơ hội cho UX innovations mà nhà hàng thường không cần.

### Feature 1: 🔥 Grilling Guide & Timer System

```
┌─────────────────────────────────────────────┐
│  🔥 焼き方ガイド / Grilling Guide            │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  和牛ハラミ (Wagyu Harami)           │    │
│  │                                     │    │
│  │  ┌───────────────────────────┐      │    │
│  │  │     🥩                    │      │    │
│  │  │                           │      │    │
│  │  │    ████████░░░░  60%     │      │    │
│  │  │                           │      │    │
│  │  │  ⏱ 0:45 / 1:15           │      │    │
│  │  │  FLIP NOW! 裏返して！      │      │    │
│  │  └───────────────────────────┘      │    │
│  │                                     │    │
│  │  🌡 推奨: ミディアムレア              │    │
│  │     Recommended: Medium-Rare         │    │
│  │                                     │    │
│  │  片面: 45秒 → 裏返し → 30秒          │    │
│  │  Side 1: 45s → Flip → Side 2: 30s   │    │
│  │                                     │    │
│  │  💡 ハラミは焼きすぎ注意！            │    │
│  │     Don't overcook harami!           │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  [⏱ タイマー開始]  [📖 もっと詳しく]        │
│  [Start Timer]     [Learn More]             │
└─────────────────────────────────────────────┘
```

**Implementation approach:**
```javascript
// Grilling data embedded in menu item metadata
const GRILL_GUIDES = {
    'menu-001': {  // Wagyu Harami
        meat_type: 'beef',
        thickness: 'medium',     // thin|medium|thick
        recommended_doneness: 'medium_rare',
        timers: {
            rare:        { side1: 30, side2: 20 },
            medium_rare: { side1: 45, side2: 30 },
            medium:      { side1: 60, side2: 45 },
            well_done:   { side1: 90, side2: 60 }
        },
        tips: {
            ja: 'ハラミは焼きすぎると硬くなります。ミディアムレアがおすすめ！',
            en: 'Harami gets tough if overcooked. Medium-rare recommended!'
        },
        flip_alert: true,  // Vibrate/sound on flip
        rest_time: 10      // Seconds to rest after grilling
    }
};

// Timer component (Vanilla JS)
class GrillTimer {
    constructor(menuItemId, doneness = 'medium_rare') {
        this.guide = GRILL_GUIDES[menuItemId];
        this.doneness = doneness;
        this.side = 1;
        this.elapsed = 0;
        this.interval = null;
    }

    start() {
        const target = this.guide.timers[this.doneness];
        this.interval = setInterval(() => {
            this.elapsed++;
            const currentTarget = this.side === 1 ? target.side1 : target.side2;

            if (this.elapsed >= currentTarget) {
                if (this.side === 1) {
                    // Time to flip!
                    this._alertFlip();
                    this.side = 2;
                    this.elapsed = 0;
                } else {
                    // Done!
                    this._alertDone();
                    this.stop();
                }
            }

            this._render();
        }, 1000);

        // Log event for analytics
        eventStore.append('ITEM_STATUS_CHANGED', {
            menu_item_id: menuItemId,
            action: 'grill_timer_started',
            doneness: this.doneness
        });
    }

    _alertFlip() {
        // Haptic feedback (iPad supports)
        if (navigator.vibrate) navigator.vibrate(200);
        // Visual + audio alert
        showNotification('🔄 裏返してください！ Flip now!', 'warning');
        // Play flip sound
        new Audio('/assets/sounds/flip.mp3').play().catch(() => {});
    }

    _alertDone() {
        if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
        showNotification('✅ 焼き上がり！ Ready to eat!', 'success');
        new Audio('/assets/sounds/done.mp3').play().catch(() => {});
    }
}
```

### Feature 2: 🎯 Smart Recommendations Engine

**Recommendation Triggers & Rules:**

```javascript
const RECOMMENDATION_ENGINE = {
    rules: [
        // Rule 1: Pairing recommendations
        {
            trigger: { item_category: 'meat', action: 'added_to_cart' },
            suggest: [
                { type: 'drink_pairing', message_ja: 'お肉に合うビールはいかがですか？' },
                { type: 'side_pairing', message_ja: 'サラダも一緒にいかがですか？' }
            ],
            cooldown: 300 // Don't suggest again for 5 min
        },

        // Rule 2: Tempo-based suggestions
        {
            trigger: { minutes_since_last_order: 20, phase: 'ordering' },
            suggest: [
                { type: 'course_next', message_ja: 'デザートはいかがですか？' },
                { type: 'reorder', message_ja: 'もう一杯いかがですか？',
                  items: 'previous_drinks' }
            ]
        },

        // Rule 3: Group-size suggestions
        {
            trigger: { guest_count_gte: 4, order_count: 1 },
            suggest: [
                { type: 'sharing', message_ja: '盛り合わせがお得です！',
                  item_id: 'menu-008' } // Tokusen Moriawase
            ]
        },

        // Rule 4: Tabehoudai time warnings
        {
            trigger: { dining_mode: 'tabehoudai', remaining_minutes: 15 },
            suggest: [
                { type: 'last_order',
                  message_ja: '⏰ ラストオーダーまであと15分です！',
                  priority: 'high' }
            ]
        },

        // Rule 5: Weather/Season-based (future - API integration)
        {
            trigger: { season: 'winter' },
            suggest: [
                { type: 'seasonal', message_ja: '寒い日には温かいスープはいかが？',
                  item_category: 'side', filter: 'warm' }
            ]
        }
    ],

    // Cross-session intelligence (5-year vision)
    // Uses aggregated data from backend, not individual customer tracking
    crossSessionRules: [
        {
            // "Tables that ordered X also ordered Y"
            type: 'collaborative_filtering',
            source: 'backend_api',
            endpoint: '/api/recommendations/similar-orders',
            cache_ttl: 3600  // Refresh hourly
        },
        {
            // "Most popular items this week"
            type: 'trending',
            source: 'backend_api',
            endpoint: '/api/recommendations/trending',
            cache_ttl: 1800
        }
    ]
};
```

**Recommendation UI — Non-intrusive strip:**
```
┌────────────────────────────────────────────────────┐
│ 💡 ビールを注文された方に: 枝豆はいかがですか？ ¥350 │
│    Beer pairs great with edamame!          [＋追加] │
└────────────────────────────────────────────────────┘
```

### Feature 3: 🍖 Course/Tempo Ordering

```
┌─────────────────────────────────────────────────────┐
│  📋 おすすめの流れ / Recommended Course               │
│                                                       │
│  ① 前菜 Appetizer     ✅ 注文済                      │
│     └─ チョレギサラダ, 枝豆                            │
│                                                       │
│  ② メイン Main         🔥 今ここ                      │
│     └─ 和牛ハラミ, カルビ, タン                        │
│     └─ 💡 ホルモンも追加？                             │
│                                                       │
│  ③ 〆 Finishing        ⏳ あと20分後                   │
│     └─ ビビンバ or 冷麺                               │
│                                                       │
│  ④ デザート Dessert    ⏳                             │
│     └─ バニラアイス, 杏仁豆腐                          │
│                                                       │
│  [このコースで注文] [カスタマイズ]                      │
└─────────────────────────────────────────────────────┘
```

**Implementation**: Course template stored as JSON in menu data. Khách có thể follow template hoặc order tự do. Template chỉ là **suggestion layer** — không bao giờ block free ordering.

### Feature 4: 🍽 Tabehoudai (食べ放題) Mode

```javascript
/**
 * All-you-can-eat mode management
 * Changes entire UX when dining_mode === 'tabehoudai'
 */
const TabehoudaiManager = {
    config: {
        plans: [
            {
                id: 'plan_90min_3980',
                duration: 90,       // minutes
                price: 3980,        // per person
                last_order: 15,     // minutes before end
                excluded_items: ['menu-008'], // No tokusen moriawase
                drink_included: false,
                drink_plan_addon: 1500  // +¥1,500 for nomihoudai
            },
            {
                id: 'plan_120min_4980',
                duration: 120,
                price: 4980,
                last_order: 20,
                excluded_items: [],
                drink_included: true
            }
        ]
    },

    // UI changes in tabehoudai mode:
    uiModifications: {
        // 1. Hide prices on menu cards (it's all-you-can-eat!)
        showPrices: false,

        // 2. Show prominent timer in header
        showTimer: true,
        timerStyle: 'countdown',  // countdown vs elapsed

        // 3. Show remaining/last-order warnings
        warnings: [
            { minutesLeft: 30, message: '残り30分です', level: 'info' },
            { minutesLeft: 15, message: 'ラストオーダー！', level: 'warning' },
            { minutesLeft: 5,  message: '残り5分', level: 'critical' },
            { minutesLeft: 0,  message: '時間終了', level: 'ended' }
        ],

        // 4. Gray out excluded items
        excludedItemStyle: 'grayed_with_label',
        excludedLabel: '食べ放題対象外',

        // 5. Show quantity guidance
        quantityGuidance: true, // "4名様: 1人2-3皿が目安です"

        // 6. Anti-waste nudge (5-year vision)
        wasteWarning: {
            threshold: 3, // If > 3 items of same type ordered
            message: '残さずお召し上がりください 🙏'
        }
    }
};
```

**Tabehoudai Timer UI in header:**
```
┌──────────────────────────────────────────────┐
│ 🏮 T5 │ 4名 │ 🔥食べ放題 │ ⏱ 37:42 残り  │
│                              ████████░░░░░  │
└──────────────────────────────────────────────┘
```

### Feature 5: 🎮 Gamification (10-year vision)

```javascript
// Future: Make dining fun with light gamification
const GamificationFeatures = {
    // "Grill Master" badge for using timer consistently
    achievements: ['grill_master', 'meat_lover', 'full_course', 'speed_eater'],

    // "Try something new" - suggest item they've never ordered
    discovery: {
        trackOrderedItems: true, // via customer loyalty (opt-in)
        newItemBonus: '次回10%オフクーポン'
    },

    // Group challenges (large parties)
    groupChallenges: {
        'clear_the_menu': {
            description: '全カテゴリーから注文してコンプリート！',
            reward: 'デザートサービス'
        }
    }
};
```

---

## Q4: "Dọn bàn" Mode & Staff Handoff

### Tầm nhìn: Seamless Staff-Customer Handoff

"Dọn bàn" là **khoảnh khắc chuyển giao** quan trọng nhất trong restaurant operations. Đây là lúc dễ xảy ra lỗi nhất (khách mới order vào session cũ, data chưa clear, bàn chưa sạch). Design phải **fool-proof**.

### Payment → Cleaning Flow

```
                    iPad (Table)           POS (Staff)          Kitchen
                    ────────────           ──────────           ───────
                         │                      │                  │
Customer taps            │                      │                  │
"お会計" (Bill)          │                      │                  │
                         │──CALL_BILL──────────▶│                  │
                         │                      │                  │
iPad shows               │                      │ Staff processes  │
payment summary          │                      │ payment          │
                         │                      │                  │
                         │◀──SESSION_PAID───────│                  │
                         │    (via WebSocket)    │                  │
                         │                      │                  │
iPad auto-transitions    │                      │                  │
to "Thank You" (5s)      │                      │──TABLE_STATUS──▶│
then CLEANING screen     │                      │  "cleaning"      │
                         │                      │                  │
Staff clears table       │                      │                  │
Long-press + PIN         │                      │                  │
                         │──SESSION_ENDED──────▶│                  │
                         │                      │──TABLE_STATUS──▶│
iPad shows READY         │                      │  "available"     │
                         │                      │                  │
```

### Detailed UI States

#### Transition: "Thank You" Screen (5 seconds, auto)
```
┌─────────────────────────────────────────────┐
│                                             │
│                                             │
│              🙏                             │
│                                             │
│     ありがとうございました                    │
│     Thank you for dining with us            │
│                                             │
│     ──────────────────────                  │
│                                             │
│     またのご来店を                           │
│     お待ちしております                       │
│                                             │
│     We look forward to                      │
│     seeing you again!                       │
│                                             │
│                                             │
│     ┌─────────────────────────────┐         │
│     │  ⭐ ご意見をお聞かせください   │         │
│     │  Quick Feedback (optional)  │         │
│     │                             │         │
│     │  😍  😊  😐  😕  😢       │         │
│     └─────────────────────────────┘         │
│                                             │
│     ▓▓▓▓▓▓▓▓▓░░░  auto-close 5s           │
└─────────────────────────────────────────────┘
```

**Feedback data capture:**
```javascript
// Optional quick feedback before cleaning screen
eventStore.append('SESSION_ENDED', {
    reason: 'completed',
    feedback_rating: 4,  // 1-5 emoji scale
    duration_minutes: 87,
    total_orders: 6,
    total_amount: 11220
});
```

#### Cleaning Screen (Locked)
```
┌─────────────────────────────────────────────┐
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │                                     │    │
│  │           🧹 片付け中               │    │
│  │           Cleaning                  │    │
│  │                                     │    │
│  │           テーブル T5               │    │
│  │                                     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─ Session Summary (for staff) ───────┐    │
│  │                                     │    │
│  │  ⏱ 87分  │  📋 6回注文  │  💴¥11,220│    │
│  │  👥 4名   │  🍖 食べ放題  │  ⭐ 4/5  │    │
│  │                                     │    │
│  │  Top items: ハラミ×4, タン×3, ビール×8│    │
│  │  Calls: 🛎×2 (avg response: 2.1min) │    │
│  │                                     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  🔒 長押しで解除 / Hold to unlock    │    │
│  │  ▓▓▓▓░░░░░░░░░░  (hold 5s)        │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  PIN: [____]  (after long-press)            │
└─────────────────────────────────────────────┘
```

### Staff Unlock Flow

```javascript
/**
 * Staff unlock mechanism for cleaning screen
 * Security: Long-press 5s + 4-digit PIN
 */
class StaffLock {
    constructor() {
        this.holdDuration = 5000; // 5 seconds
        this.holdTimer = null;
        this.holdProgress = 0;
        this.pins = {
            'hirama': ['1234', '5678', '0000'] // Branch-specific PINs
        };
    }

    startHold(progressCallback) {
        this.holdProgress = 0;
        this.holdTimer = setInterval(() => {
            this.holdProgress += 100;
            progressCallback(this.holdProgress / this.holdDuration);

            if (this.holdProgress >= this.holdDuration) {
                this.stopHold();
                this.showPinDialog();
            }
        }, 100);
    }

    stopHold() {
        clearInterval(this.holdTimer);
        this.holdProgress = 0;
    }

    showPinDialog() {
        // Show numeric PIN pad overlay
        const overlay = document.createElement('div');
        overlay.className = 'pin-overlay';
        overlay.innerHTML = `
            <div class="pin-dialog">
                <h3>スタッフ認証</h3>
                <div class="pin-display">____</div>
                <div class="pin-pad">
                    ${[1,2,3,4,5,6,7,8,9,'C',0,'✓'].map(n =>
                        `<button class="pin-key" data-key="${n}">${n}</button>`
                    ).join('')}
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        // ... PIN verification logic
    }

    verifyPin(pin) {
        const branchPins = this.pins[CONFIG.BRANCH_CODE] || [];
        return branchPins.includes(pin);
    }

    async unlock(pin) {
        if (!this.verifyPin(pin)) {
            showNotification('PINが違います', 'error');
            return false;
        }

        // Log unlock event
        eventStore.append('SESSION_ENDED', {
            reason: 'staff_unlock',
            staff_pin_hash: this._hashPin(pin), // Never store raw PIN
            unlock_time: new Date().toISOString()
        });

        // Clear session
        eventStore.clearActiveSession();

        // Transition to READY
        transitionToPhase('ready');

        return true;
    }
}
```

### Who Triggers Phase Changes?

| Transition | Primary Trigger | Secondary Trigger | Failsafe |
|-----------|----------------|-------------------|----------|
| READY → WELCOME | Customer touch | Staff check-in via POS | — |
| WELCOME → ORDERING | Customer "Go to Menu" | — | 3min timeout → READY |
| ORDERING → PAYMENT | Customer "Bill" button | POS staff initiate | Staff can force via Staff Mode |
| PAYMENT → CLEANING | POS `SESSION_PAID` WebSocket | — | Staff Mode force-close after 30min |
| CLEANING → READY | Staff long-press + PIN | — | Auto-reset after 60min (safety) |

### Emergency Overrides (Staff Mode)

```javascript
// Accessible from any phase via long-press corner
const StaffMode = {
    actions: [
        {
            label: 'セッション強制終了',
            action: 'force_end_session',
            requires_pin: true,
            log_event: 'SESSION_ENDED',
            event_data: { reason: 'staff_force_close' }
        },
        {
            label: 'テーブル移動',
            action: 'transfer_table',
            requires_pin: true,
            log_event: 'SESSION_ENDED',
            event_data: { reason: 'table_transfer' }
        },
        {
            label: 'セッション再開',
            action: 'reopen_session',
            requires_pin: true,
            description: 'Payment cancelled, resume ordering'
        },
        {
            label: 'デバイス設定',
            action: 'device_settings',
            requires_pin: true,
            description: 'Change table_id, branch_code, etc.'
        }
    ]
};
```

---

## Q5: Data Architecture

### Tầm nhìn: Data as the Core Asset

Trong 5-10 năm, dữ liệu session sẽ là **tài sản giá trị nhất** của chuỗi nhà hàng — quan trọng hơn cả công thức nấu ăn. Mỗi event kể một phần câu chuyện, và khi aggregate qua hàng ngàn sessions, chúng reveal patterns mà con người không thể nhìn thấy.

### localStorage Schema (Complete)

```javascript
// ============ COMPLETE localStorage KEY MAP ============
//
// PERSISTENT (survive session changes):
//   yakiniku_device_{TABLE_ID}           → Device registration & config
//   yakiniku_sessions_index_{TABLE_ID}   → Index of all sessions
//   yakiniku_sync_queue                  → Pending sync events
//   yakiniku_grill_guides_cache          → Cached grill guide data
//   yakiniku_recommendations_cache       → Cached recommendation data
//
// PER-SESSION (created/destroyed with session lifecycle):
//   yakiniku_active_session_{TABLE_ID}   → Current session metadata
//   yakiniku_events_{SESSION_ID}         → Event log
//   yakiniku_cart_{SESSION_ID}           → Cart state
//
// TOTAL ESTIMATED STORAGE PER SESSION:
//   ~2KB metadata + ~500B per event × ~30 events = ~17KB per session
//   With 50 sessions retained: ~850KB (well under 5MB limit)

// ============ Complete Schema Definitions ============

/**
 * @typedef {Object} DeviceConfig
 * @property {string} table_id
 * @property {string} branch_code
 * @property {string} device_id        - Unique hardware identifier
 * @property {string} registered_at    - ISO timestamp
 * @property {string} last_sync        - Last successful backend sync
 * @property {string} app_version      - Current app version
 * @property {Object} preferences      - Device-level settings
 * @property {string} preferences.language - Default language
 * @property {number} preferences.brightness - Screen brightness hint
 * @property {boolean} preferences.sound_enabled - Sound effects
 */

/**
 * @typedef {Object} SessionIndex
 * @property {string} id
 * @property {string} started_at
 * @property {string|null} ended_at
 * @property {string} phase
 * @property {number} guest_count
 * @property {string} dining_mode       - tabehoudai|alacarte
 * @property {number} event_count
 * @property {number} order_count
 * @property {number} total_amount
 * @property {boolean} synced           - All events synced to backend?
 * @property {number|null} feedback     - 1-5 rating
 */

/**
 * @typedef {Object} SessionEvent
 * @property {string} id               - Sortable unique ID
 * @property {string} type             - EventType enum value
 * @property {string} source           - EventSource enum value
 * @property {string} timestamp        - ISO timestamp (client clock)
 * @property {string} session_id
 * @property {string} table_id
 * @property {string} branch_code
 * @property {Object} data             - Event-specific payload
 * @property {boolean} _synced
 * @property {number} _sync_attempts
 * @property {string|null} _server_id
 * @property {string} _correlation_id
 */

/**
 * @typedef {Object} CartState
 * @property {string} session_id
 * @property {Array<CartItem>} items
 * @property {string} last_modified     - ISO timestamp
 */

/**
 * @typedef {Object} CartItem
 * @property {string} id               - menu_item_id
 * @property {string} name
 * @property {number} price
 * @property {string} image_url
 * @property {number} quantity
 * @property {string} notes
 */
```

### Retention Rules (Decision Matrix)

```
┌──────────────────────────────────────────────────────┐
│              DATA RETENTION MATRIX                    │
│                                                       │
│  Location      │ Retention    │ Condition              │
│  ──────────────┼──────────────┼────────────────────── │
│  localStorage   │ 48 hours     │ After session end,     │
│  (events)       │              │ if synced to backend   │
│                 │ 7 days       │ If NOT synced          │
│                 │              │ (insurance against     │
│                 │              │  data loss)            │
│  ──────────────┼──────────────┼────────────────────── │
│  localStorage   │ Immediate    │ On session end,        │
│  (cart)         │              │ clear cart             │
│  ──────────────┼──────────────┼────────────────────── │
│  localStorage   │ Permanent    │ Device config never    │
│  (device)       │              │ auto-deleted           │
│  ──────────────┼──────────────┼────────────────────── │
│  Backend DB     │ 90 days      │ Hot storage            │
│  (events)       │ 2 years      │ Warm (compressed)      │
│                 │ Forever      │ Cold (aggregated only) │
│  ──────────────┼──────────────┼────────────────────── │
│  Backend DB     │ Forever      │ Orders are financial   │
│  (orders)       │              │ records (法的義務)      │
│  ──────────────┼──────────────┼────────────────────── │
│  Analytics      │ Forever      │ Aggregated, anonymized │
│  (aggregated)   │              │ No PII                 │
└──────────────────────────────────────────────────────┘
```

### Backend Schema Additions (for multi-session analytics)

```python
# New model: SessionAnalytics (materialized view, updated on SESSION_ENDED)
class SessionAnalytics(Base):
    """Pre-computed session metrics for fast dashboard queries"""
    __tablename__ = "session_analytics"

    session_id = Column(String(36), primary_key=True)
    branch_code = Column(String(50), nullable=False, index=True)
    table_id = Column(String(36), nullable=False, index=True)

    # Timing
    date = Column(Date, nullable=False, index=True)           # For date-range queries
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)

    # Dining info
    guest_count = Column(Integer)
    dining_mode = Column(String(20))    # tabehoudai|alacarte
    plan_id = Column(String(50))

    # Order metrics
    order_count = Column(Integer)
    item_count = Column(Integer)       # Total items ordered
    unique_items = Column(Integer)     # Distinct menu items

    # Financial
    gross_amount = Column(Numeric(10, 0))
    tax_amount = Column(Numeric(10, 0))
    total_amount = Column(Numeric(10, 0))
    amount_per_guest = Column(Numeric(10, 0))  # 客単価

    # Service quality
    staff_calls = Column(Integer)
    avg_call_response_seconds = Column(Integer)
    feedback_rating = Column(Integer)  # 1-5

    # Operational
    first_order_minutes = Column(Integer)  # Time from session start to first order
    order_intervals_avg = Column(Integer)  # Avg minutes between orders

    # Category breakdown (JSON)
    category_breakdown = Column(JSON)  # {"meat": 5800, "drinks": 2400, ...}

    # Computed indexes
    __table_args__ = (
        Index('ix_session_analytics_branch_date', 'branch_code', 'date'),
        Index('ix_session_analytics_table_date', 'table_id', 'date'),
    )
```

### Staff Analytics Dashboard (What staff needs to see)

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Dashboard — Hirama Branch — 2026-02-06                       │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ 本日売上  │ │ 組数     │ │ 客単価   │ │ 平均滞在  │           │
│  │ ¥186,400 │ │ 18組    │ │ ¥2,850  │ │ 78分     │           │
│  │ ↑12%     │ │ ↑3      │ │ ↓¥200   │ │ ↑5min    │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                   │
│  ┌─ テーブル稼働状況 ──────────────────────────────────┐         │
│  │                                                     │         │
│  │  T1 🟢   T2 🔴   T3 🟡   T4 🟢   T5 🔴           │         │
│  │  空席    食事中   お会計   空席    片付け中           │         │
│  │  --     45min   82min   --     3min              │         │
│  │                                                     │         │
│  │  T6 🔴   T7 🟢   T8 🔴   T9 🟢   T10 🟡          │         │
│  │  食事中   空席    食事中   空席    お会計            │         │
│  │  23min   --     67min   --     90min             │         │
│  └─────────────────────────────────────────────────────┘         │
│                                                                   │
│  ┌─ 人気メニュー (本日) ───────────────────────────────┐         │
│  │  1. 和牛ハラミ     42皿  │ ████████████████ 42    │         │
│  │  2. 生ビール       38杯  │ ███████████████  38    │         │
│  │  3. カルビ         31皿  │ ████████████     31    │         │
│  │  4. タン           28皿  │ ███████████      28    │         │
│  │  5. ハイボール     25杯  │ █████████        25    │         │
│  └─────────────────────────────────────────────────────┘         │
│                                                                   │
│  ┌─ サービス品質 ──────────────────────────────────────┐         │
│  │  🛎 スタッフコール: 平均応答 2.3分 (目標: <3min)    │         │
│  │  ⭐ 顧客満足度: 4.2/5.0 (24件)                      │         │
│  │  ⏱ 初回注文までの時間: 平均 4.5分                    │         │
│  └─────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Privacy Handling

```javascript
/**
 * Privacy-by-Design Principles
 *
 * 1. NO PII on iPad: iPad never stores customer names, phone numbers,
 *    email addresses, or payment card details.
 *
 * 2. Session = Anonymous: Sessions are identified by UUID, not customer.
 *    Linking session to customer (via booking) happens only on backend.
 *
 * 3. Feedback is optional: Rating is stored as integer, no text required.
 *
 * 4. Client-side data is ephemeral: Retention policy ensures cleanup.
 *
 * 5. Analytics are aggregated: Dashboard shows trends, not individuals.
 */

const PrivacyPolicy = {
    // Data classification
    classification: {
        'session_id': 'internal',        // Not PII
        'table_id': 'internal',
        'guest_count': 'internal',
        'order_items': 'business',       // Business data, not PII
        'feedback_rating': 'anonymous',
        'booking_id': 'sensitive',       // Can link to PII on backend
        'staff_pin': 'never_stored'      // Only hash, never raw
    },

    // Data minimization rules
    minimization: {
        // Don't log what you don't need
        exclude_from_events: [
            'customer_name',
            'customer_phone',
            'payment_card_number',
            'customer_address'
        ],

        // Anonymize after retention period
        anonymize_after_days: 90,
        anonymize_fields: ['booking_id'] // Remove link to customer
    },

    // GDPR/APPI compliance (Japan's Act on Protection of Personal Information)
    compliance: {
        framework: 'APPI',  // 個人情報保護法
        data_controller: 'Yakiniku Jinan Co., Ltd.',
        retention_notice: true,  // Display in welcome screen
        opt_out_analytics: false // Analytics are anonymized, no opt-out needed
    }
};
```

### Scaling to 100+ Locations

```
┌──────────────────────────────────────────────────────────────┐
│                 MULTI-LOCATION DATA FLOW                      │
│                                                                │
│  Location 1        Location 2        Location N               │
│  (Hirama)          (Shibuya)         (...)                    │
│  ┌──────┐          ┌──────┐          ┌──────┐                │
│  │iPads │          │iPads │          │iPads │                │
│  │(5-10)│          │(5-10)│          │(5-10)│                │
│  └──┬───┘          └──┬───┘          └──┬───┘                │
│     │                  │                  │                    │
│     ▼                  ▼                  ▼                    │
│  ┌──────┐          ┌──────┐          ┌──────┐                │
│  │Local │          │Local │          │Local │                │
│  │FastAPI│         │FastAPI│         │FastAPI│  ← Edge        │
│  │+SQLite│         │+SQLite│         │+SQLite│    Servers     │
│  └──┬───┘          └──┬───┘          └──┬───┘                │
│     │                  │                  │                    │
│     └──────────────────┼──────────────────┘                    │
│                        │                                       │
│                        ▼                                       │
│              ┌─────────────────────┐                          │
│              │  Central Data Lake   │  ← Cloud                │
│              │  (PostgreSQL +       │                          │
│              │   TimescaleDB for    │                          │
│              │   event time-series) │                          │
│              └────────┬────────────┘                          │
│                       │                                        │
│                       ▼                                        │
│              ┌─────────────────────┐                          │
│              │  Analytics Engine    │                          │
│              │  - Cross-location    │                          │
│              │    comparisons       │                          │
│              │  - ML predictions    │                          │
│              │  - Menu optimization │                          │
│              └─────────────────────┘                          │
└──────────────────────────────────────────────────────────────┘
```

**Key scaling decisions:**
1. **branch_code in every event**: Already in schema ✅ — enables multi-tenant from day one
2. **Local-first**: Each location runs independently, syncs to central when available
3. **Event dedup**: `correlation_id` + `client_timestamp` prevents double-counting
4. **Schema evolution**: JSON `data` field allows adding new fields without migrations
5. **Sharding**: Events partitioned by `branch_code` + `date` for query performance

---

## Tổng kết & Tầm nhìn dài hạn

### Ngắn hạn (6 tháng): Foundation
- ✅ Implement 6-phase session lifecycle trên iPad
- ✅ Client-side `EventStore` class với sync engine
- ✅ Cleaning/Lock screen với staff PIN
- ✅ Cart key theo `session_id` thay vì `TABLE_ID`
- ✅ `RetentionManager` cho localStorage cleanup
- ✅ Welcome screen với guest count + dining mode selection

### Trung hạn (1-2 năm): Intelligence
- 🔥 Grill timer/guide cho top 20 menu items
- 🎯 Recommendation engine (rule-based → collaborative filtering)
- 🍽 Tabehoudai mode với countdown timer
- 📊 Session analytics dashboard cho managers
- 🔄 Batch event sync endpoint ở backend

### Dài hạn (3-5 năm): Platform
- 🤖 ML-powered recommendations (cross-location learning)
- 📱 Customer app integration (loyalty, pre-order, favorites)
- 🌡 IoT grill temperature sensors → auto-suggest timing
- 🎮 Gamification layer (badges, challenges, rewards)
- 🌏 Multi-brand support (không chỉ yakiniku — sushi, ramen, izakaya)

### Moonshot (10-20 năm): Autonomous Dining
- 🧠 AI Dining Concierge: Hiểu dietary preferences, allergies, mood
- 🤖 Robotic serving integration: Event triggers robot delivery
- 🔮 Predictive inventory: ML dự đoán demand per item per hour per location
- 🌐 Global franchise platform: 1000+ locations, 100+ brands, 1 platform
- 🧬 Personalized nutrition: Kết hợp health data (opt-in) để suggest balanced meals

### Triết lý thiết kế

> **"Every event is a pixel. Enough pixels make a picture. Enough pictures tell a story. The story of how people eat together."**

Event sourcing không phải chỉ là technical pattern — nó là cách chúng ta **capture the human experience** của dining. Mỗi `ORDER_CREATED` là một quyết định. Mỗi `CALL_STAFF` là một nhu cầu. Mỗi `SESSION_ENDED` là một kỷ niệm. Khi có đủ events từ đủ sessions qua đủ thời gian, chúng ta sẽ hiểu dining experience ở mức mà chưa nhà hàng nào từng hiểu.

Kiến trúc hiện tại — Vanilla JS + FastAPI + Event Sourcing — là foundation đúng đắn. Nó đơn giản, nó reliable, và nó extensible. Đừng add complexity quá sớm. Hãy để data guide the evolution.

**Priority #1 bây giờ**: Ship session lifecycle + cleaning screen. Mọi thứ khác sẽ follow from the data.
