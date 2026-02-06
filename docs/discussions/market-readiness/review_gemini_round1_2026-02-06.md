# ⚡ Gemini Pragmatist Review — Round 1 | 2026-02-06

## Chủ đề: Tính khả thi & Chiến lược Go-to-Market cho Yakiniku.io

## Tổng quan lập trường

Yakiniku.io có nền tảng kỹ thuật **tốt hơn mong đợi** cho giai đoạn prototype — event sourcing, async backend, offline fallback đã hoạt động. Tuy nhiên, khoảng cách từ prototype đến **production-ready pilot** vẫn còn đáng kể: zero auth, zero tests, POS hoàn toàn mock, và config inconsistency. Chiến lược đúng là **thu hẹp scope xuống 3 app core** (table-order + kitchen + POS), fix chỉ những gì "kill" được sản phẩm, và pilot tại Hirama trong 8-12 tuần. Mọi thứ khác — multi-tenant, AI insights, K8s — là DEFERRED, không phải BLOCKED.

---

## Phân tích chi tiết

### Câu hỏi 1: MVP Definition — Đâu là tập hợp feature tối thiểu để launch?

**Lập trường**: CÓ ĐIỀU KIỆN — Đồng ý thu hẹp scope, nhưng cần rõ ràng "tối thiểu" nghĩa là gì

**Thực trạng hiện tại:**

Codebase có 6 frontend apps với mức hoàn thiện rất khác nhau:

| App | Trạng thái | Kết nối API | Sẵn sàng pilot? |
|-----|-----------|-------------|-----------------|
| **table-order** | ✅ Hoàn thiện nhất | Dynamic `API_HOST` via `window.location.hostname` | 🟢 80% |
| **kitchen** | ✅ Functional | ❌ Hardcode `localhost:8000` | 🟡 65% sau fix config |
| **POS** | ❌ Mock data hoàn toàn | ❌ Hardcode `localhost:8000` | 🔴 30% |
| **checkin** | ✅ Logic tốt | ❌ Hardcode `localhost:8000` | 🟡 50% |
| **dashboard** | ⚠️ 2 hệ thống song song | ❌ Hardcode `localhost:8000` | 🔴 20% |
| **web** | Branding/booking site | N/A | 🟡 Có thể dùng riêng |

Backend có **2 order systems song song**:
- **Legacy**: `app/routers/orders.py` (421 dòng) — dùng `app.models.order`
- **Domain**: `app/domains/tableorder/router.py` (329 dòng) — re-import từ legacy models nhưng thêm event sourcing

Cả hai đều registered trong `app/main.py`: legacy tại `/api/orders`, domain tại `/api/tableorder`. Table-order frontend gọi đúng `/api/tableorder/`, nhưng kitchen frontend gọi `/api/orders/kitchen` (legacy route).

**Chi phí thực hiện:**
- Effort: **12-16 story points** cho MVP core (3 apps)
- Risk: 🟡 Trung bình — POS cần work thực sự, nhưng có backend API sẵn
- Dependencies: Config unification phải làm trước, POS frontend phải kết nối real API

**ROI Analysis:**
- Benefit: Pilot tại 1 nhà hàng = validate toàn bộ product concept, có case study thật
- Cost: ~8-12 tuần dev (1-2 người), hosting ~$20-50/tháng (VPS + domain)
- Payback period: Pilot miễn phí → feedback 2-3 tháng → pricing từ tháng 6-7
- Opportunity cost: Nếu làm 6 apps cùng lúc → chậm 3-4 tháng, risk cao hơn nhiều

**Đề xuất thực tế:**

- **Làm ngay (< 1 sprint):**
  - Unify config pattern: Copy config.js từ table-order sang kitchen, POS, checkin — thay `localhost` bằng `window.location.hostname`
  - Chọn 1 order router: Kitchen frontend đổi từ `/api/orders/kitchen` sang `/api/kitchen/orders` (domain router đã có)
  - POS frontend: Thay mock `loadTables()` bằng call `/api/pos/tables`, thay mock `loadTableOrder()` bằng call `/api/pos/sessions/{id}/bill`

- **Làm sớm (1-3 sprints):**
  - POS checkout flow kết nối real API (`/api/pos/checkout` — backend đã implement!)
  - Basic auth (xem câu hỏi 3)
  - Kitchen ↔ Table-order WebSocket integration (TODO trong code: "Send to kitchen via WebSocket")

- **Để sau / Không làm:**
  - ❌ Dashboard SPA — dùng Jinja2 dashboard hiện tại cho pilot
  - ❌ Check-in kiosk — staff có thể check-in manual trong pilot
  - ❌ Web booking site — dùng điện thoại / line cho pilot đầu tiên
  - ❌ Multi-tenant features
  - ❌ AI customer insights (OpenAI integration)

**Dẫn chứng từ codebase:**
- File: `apps/table-order/js/config.js` — Pattern đúng: `const API_HOST = window.location.hostname` cho phép deploy trên mọi network
- File: `apps/kitchen/js/app.js#L8-L12` — Hardcode: `API_BASE: 'http://localhost:8000/api'` → broken khi deploy production
- File: `apps/pos/js/app.js#L140-L170` — Mock data: `loadTables()` trả về hardcoded array, `loadTableOrder()` trả về hardcoded object
- File: `backend/app/domains/pos/router.py` — Backend POS API **đã implement đầy đủ**: `GET /tables`, `GET /sessions/{id}/bill`, `POST /checkout`, `POST /tables/{id}/close`
- File: `backend/app/main.py#L87-L89` — Duplicate routes: cả `/api/orders` và `/api/tableorder` đều active

---

### Câu hỏi 2: Trust Building — Làm thế nào để lấy niềm tin khách hàng?

**Lập trường**: ĐỒNG Ý — Pilot-first approach, nhưng cần "safety net" kỹ thuật tối thiểu

**Thực trạng hiện tại:**

Nhà hàng Nhật (đặc biệt yakiniku) có workflow rất rõ ràng: khách ngồi → gọi món qua iPad → bếp nhận → phục vụ → thanh toán. Yakiniku.io đã cover được flow này **trong demo mode**. Vấn đề là:

1. **Zero authentication** — `backend/app/config.py` có `SECRET_KEY: str = "change-me-in-production"` nhưng **không có middleware nào dùng nó**. Folder `backend/app/middleware/` trống hoàn toàn. Bất kỳ ai biết IP có thể gọi mọi API, kể cả `POST /api/pos/checkout`.

2. **Data persistence questionable** — `database.py` dùng `sqlite+aiosqlite` cho dev, `init_db()` gọi `create_all()`. Không có Alembic, không có migration strategy. Nếu model thay đổi, data mất.

3. **Offline fallback tốt** — Table-order app load demo menu khi API fail, hiển thị connection status rõ ràng. Đây là **điểm mạnh thực sự** cho trust building.

4. **UI tiếng Nhật hoàn chỉnh** — Toàn bộ UI text đã bằng tiếng Nhật, bao gồm status labels, error messages, notifications. Đây là yếu tố quan trọng cho thị trường Nhật.

**Chi phí thực hiện:**
- Effort: **5-8 story points** cho trust minimum
- Risk: 🟡 Trung bình — Auth là công việc rõ ràng, nhưng cần design đúng
- Dependencies: Auth phải xong trước khi có real customer data

**ROI Analysis:**
- Benefit: Chủ nhà hàng thấy hệ thống hoạt động tại quán mình → trust tự nhiên
- Cost: 2-3 tuần cho auth + data safety
- Payback period: Immediate — không có trust = không có customer
- Opportunity cost: Nếu skip auth → 1 incident = mất toàn bộ trust, có thể mất luôn pilot

**Đề xuất thực tế:**

- **Làm ngay (< 1 sprint):**
  - **Network-level security**: Deploy backend trên internal network của nhà hàng, không expose ra internet. Table-order iPad kết nối qua WiFi nội bộ → không cần auth phức tạp cho MVP
  - **Receipt/bill hiển thị chính xác**: POS phải tính đúng subtotal, tax (10%), total — backend code tại `domains/pos/router.py` đã implement `TAX_RATE = Decimal("0.10")`
  - Tạo 1 video demo 2-3 phút showing full flow

- **Làm sớm (1-3 sprints):**
  - Basic PIN-based auth cho POS (4 số, không cần RBAC phức tạp)
  - SQLite → PostgreSQL migration cho production (docker-compose.yml đã config PostgreSQL)
  - Backup script đơn giản (pg_dump cron)

- **Để sau / Không làm:**
  - ❌ Full RBAC system
  - ❌ JWT token-based auth
  - ❌ Customer-facing auth (booking, loyalty)
  - ❌ Audit trail cho security (event sourcing đã cover order audit)

**Dẫn chứng từ codebase:**
- File: `backend/app/config.py#L17` — `SECRET_KEY: str = "change-me-in-production"` — chưa có code nào consume key này
- File: `backend/app/middleware/` — Folder trống, zero middleware
- File: `backend/app/database.py#L52-L58` — `init_db()` dùng `create_all()`, không có migration
- File: `docker-compose.yml#L27-L34` — PostgreSQL config sẵn sàng: `postgres:15-alpine` với `yakiniku` database
- File: `apps/table-order/js/app.js#L88-L100` — Connection status bar: hiển thị 🟢/🔴 cho online/offline rõ ràng

---

### Câu hỏi 3: Technical Debt vs Speed — Xử lý nợ kỹ thuật thế nào?

**Lập trường**: CÓ ĐIỀU KIỆN — Phân loại rõ "debt that kills" vs "debt that annoys"

**Thực trạng hiện tại:**

Technical debt hiện tại có thể chia 3 nhóm:

**🔴 BLOCKING (fix trước launch):**

1. **Config inconsistency** — 4/6 apps hardcode `localhost:8000`. Deploy lên bất kỳ server nào khác đều broken. Fix: 15 phút/app, copy pattern từ table-order.

2. **POS = 100% mock** — `apps/pos/js/app.js` function `loadTables()` trả về hardcoded array 10 tables. `loadTableOrder()` trả về hardcoded menu items. `confirmPayment()` chỉ update local state. Backend POS API đã sẵn sàng tại `domains/pos/router.py` nhưng frontend **không gọi bất kỳ API nào**.

3. **No data persistence strategy** — SQLite file sẽ mất nếu server restart không đúng cách. Cho production cần PostgreSQL.

**🟡 ANNOYING (fix sau launch được):**

4. **Duplicate order routers** — 2 router cùng manage orders nhưng từ models khác nhau. Domains re-export từ legacy (`domains/tableorder/models.py` chỉ có `from app.models.order import ...`), nên thực tế dùng chung model. Risk: confusion, không phải data inconsistency.

5. **Duplicate dashboard** — Jinja2 dashboard (`routers/dashboard.py`, 648 dòng) vs SPA dashboard (`apps/dashboard/`). Cho pilot, Jinja2 dashboard đủ dùng.

6. **Zero tests** — `backend/tests/` folder trống hoàn toàn. Cho pilot 1 branch, manual testing chấp nhận được. Trước khi scale lên branch 2, cần integration tests.

**🟢 DEFERRED (không ảnh hưởng launch):**

7. **Doc-Code gap** — Architecture docs mô tả K8s, Redis caching, multi-tenant. Code chưa implement. Đây không phải debt, đây là **aspirational documentation**. Ghi chú "Future Vision" và move on.

8. **No CI/CD** — Cho pilot 1 branch, deploy manual acceptable. CI/CD cần khi có branch 2.

9. **Notification types limited** — `NotificationType` enum chỉ có booking-related types (NEW_BOOKING, VIP_ARRIVED, etc.). Không có ORDER_CREATED, ORDER_READY. Workaround: kitchen app đã dùng polling + WebSocket riêng.

**Chi phí thực hiện:**
- Effort: **8-10 story points** cho BLOCKING items, **15-20 points** cho ANNOYING items
- Risk: 🔴 Cao nếu ship BLOCKING items unfixed — POS không hoạt động = nhà hàng không thể thanh toán
- Dependencies: Config fix → POS connection → POS testing → Launch

**ROI Analysis:**
- Benefit: Fix blocking = product hoạt động end-to-end. Fix annoying = dev velocity tăng 30-40%
- Cost: BLOCKING = 2-3 tuần. ANNOYING = 2-3 tuần thêm. DEFERRED = 0 cost now
- Payback period: BLOCKING = immediate (product works). ANNOYING = khi team scale lên 3+ devs
- Opportunity cost: Fix annoying trước launch = chậm 3 tuần cho zero user benefit

**Đề xuất thực tế:**

- **Làm ngay (< 1 sprint):**
  - Config unification (tạo shared config pattern)
  - POS frontend kết nối real API (backend đã implement)
  - Switch dev DB sang PostgreSQL (test với docker-compose)

- **Làm sớm (1-3 sprints):**
  - Deprecate legacy order router, redirect `/api/orders/*` → `/api/tableorder/*`
  - Thêm 5-10 integration tests cho critical path: create order → kitchen view → POS checkout
  - Alembic setup cho migration

- **Để sau / Không làm:**
  - ❌ Consolidate dashboards (pilot dùng Jinja2)
  - ❌ Full test coverage (>80%)
  - ❌ CI/CD pipeline
  - ❌ Fix doc-code gap (mark docs as "vision")

**Dẫn chứng từ codebase:**
- File: `apps/pos/js/app.js#L139-L150` — `loadTables()` toàn mock: 10 tables hardcoded, `loadDailyStats()` hardcode `'¥128,500'`
- File: `backend/app/domains/pos/router.py#L27-L100` — Backend `GET /pos/tables` **đã implement đầy đủ** với real DB queries, session tracking, summary calculation
- File: `backend/app/domains/tableorder/models.py` — Chỉ là re-export: `from app.models.order import Order, OrderItem, OrderStatus, TableSession`
- File: `backend/app/main.py#L82-L84` — Legacy router: `app.include_router(orders.router, prefix="/api/orders", ...)`
- File: `backend/app/main.py#L91-L93` — Domain router: `app.include_router(tableorder_router, prefix="/api/tableorder", ...)`
- File: `backend/app/services/notification_service.py#L12-L18` — `NotificationType` chỉ có 5 types, tất cả booking-related

---

### Câu hỏi 4: Competitive Positioning — Yakiniku.io khác gì đối thủ?

**Lập trường**: CÓ ĐIỀU KIỆN — Niche "Yakiniku-specific" có giá trị, nhưng cần chứng minh bằng feature, không phải marketing

**Thực trạng hiện tại:**

So sánh thực tế với đối thủ:

| Feature | Square/AirREGI | Smaregi | Yakiniku.io |
|---------|---------------|---------|------------|
| POS | ✅ Full | ✅ Full | ❌ Mock |
| Table ordering (iPad) | ✅ Generic | ✅ Plugin | ✅ Yakiniku-optimized |
| Kitchen display | ⚠️ Basic | ✅ Plugin | ✅ Station-based |
| Offline mode | ✅ | ✅ | ✅ Demo fallback |
| Pricing | ¥0 + 3.25%/tx | ¥5,500/tháng~ | TBD |
| Setup time | 30 phút | 1-2 ngày | ??? |
| Japanese UI | ✅ Native | ✅ Native | ✅ |
| Auth/Security | ✅ Enterprise | ✅ | ❌ Zero |
| Payment integration | ✅ Built-in | ✅ Built-in | ❌ None |

**Honest assessment:** Yakiniku.io hiện tại **không thể cạnh tranh trực tiếp** với Square hay Smaregi. Đối thủ có POS thật, payment processing thật, và hàng ngàn nhà hàng đang dùng.

**Nhưng** có 2 điểm khác biệt thực sự trong code:

1. **Kitchen Display với station-based routing** — `apps/kitchen/js/app.js` có `STATIONS` object phân loại items theo keywords (肉/meat, 他/sides, 飲物/drinks). Đây là feature mà Square/AirREGI **không có sẵn**. Nhà hàng yakiniku có nhiều station (thịt, đồ ăn phụ, đồ uống) và cần routing order items đến đúng station.

2. **Event sourcing cho order tracking** — `domains/tableorder/events.py` track toàn bộ lifecycle: `ORDER_CREATED → CONFIRMED → PREPARING → READY → SERVED`. Bao gồm cả `GATEWAY_SENT/FAILED` cho delivery tracking. Đối thủ generic không cần level này.

**Chi phí thực hiện:**
- Effort: **3-5 story points** để polish 2 differentiators thành "demo-able" features
- Risk: 🟡 Trung bình — Differentiators có trong code nhưng chưa được highlight trong UX
- Dependencies: Kitchen app cần kết nối real data (không chỉ demo)

**ROI Analysis:**
- Benefit: Unique selling point cho yakiniku restaurants = smaller market nhưng deeper penetration
- Cost: Gần như 0 — code đã có, cần polish UX
- Payback period: Từ pilot demo đầu tiên
- Opportunity cost: Nếu bỏ niche focus để làm generic restaurant POS → cạnh tranh với Square bằng 0.01% resources của họ

**Đề xuất thực tế:**

- **Làm ngay (< 1 sprint):**
  - Kitchen station routing: Demo với real order data, show station-based view hoạt động
  - Landing page focus: "焼肉専用" (yakiniku-specific) messaging rõ ràng

- **Làm sớm (1-3 sprints):**
  - Timer-based alerts cho yakiniku (thịt nướng có thời gian chuẩn bị khác nhau)
  - Course management (食べ放題/nomihoudai tracking — eat-all-you-can timer)
  - Table session time tracking (đã có `TableSession.started_at`)

- **Để sau / Không làm:**
  - ❌ AI customer insights (OpenAI integration) — chưa phải USP, chi phí API cao, chưa có data
  - ❌ Payment integration (partner với payment provider sau khi có traction)
  - ❌ Generic restaurant features (cạnh tranh Red Ocean)

**Dẫn chứng từ codebase:**
- File: `apps/kitchen/js/app.js#L23-L45` — `STATIONS` object: meat station detect keywords `['カルビ', 'ハラミ', 'タン', 'ロース', ...]`, side station detect `['ライス', 'ナムル', 'キムチ', ...]`. Đây là domain knowledge thật
- File: `backend/app/domains/tableorder/events.py#L27-L67` — 21 event types covering full lifecycle + gateway tracking
- File: `backend/app/routers/chat.py` — OpenAI integration hoạt động nhưng là "nice to have". `chat_service.chat()` fallback to keyword matching khi API key missing
- File: `apps/table-order/js/app.js#L263-L400` — Demo menu 40 items với categories yakiniku-specific: meat, drinks, salad, rice, side, dessert, set menu

---

### Câu hỏi 5: Go-to-Market Strategy — Bước đi cụ thể đầu tiên?

**Lập trường**: ĐỒNG Ý — Pilot tại Hirama là bước đi đúng, nhưng cần timeline thực tế

**Thực trạng hiện tại:**

Code hiện tại đã hardcode `BRANCH_CODE: 'hirama'` ở mọi nơi — cả frontend và backend. Đây vừa là limitation (chưa multi-tenant), vừa là advantage (đã sẵn sàng cho pilot branch đầu tiên).

Infrastructure cần cho pilot 1 branch:

| Component | Hiện tại | Cần cho pilot | Effort |
|-----------|---------|--------------|--------|
| Server | Local dev | 1 VPS (2GB RAM đủ) | 1 ngày |
| Database | SQLite file | PostgreSQL (docker-compose sẵn) | 0.5 ngày |
| SSL | Không | Không cần (internal network) | 0 |
| Domain | Không | Không cần cho pilot | 0 |
| Menu data | Demo/seed data | Real menu từ nhà hàng | 1-2 ngày |
| Devices | Browser dev | 2-3 iPad + 1 PC (POS) | Hardware cost |
| Network | Local WiFi | Dedicated WiFi cho system | Setup cost |

**Chi phí vận hành thực tế (1 branch):**
- VPS (Vultr/Linode 2GB): **~$12/tháng** (~¥1,800)
- PostgreSQL: Included trong VPS
- Domain (optional): ~$12/năm
- OpenAI API (nếu dùng chat): **~$5-20/tháng** tùy usage — nhưng đề xuất tắt cho pilot
- **Total: ~¥2,000-3,000/tháng** cho infrastructure

**Chi phí thực hiện:**
- Effort: **20-25 story points** tổng cộng (từ hiện tại → pilot-ready)
- Risk: 🟡 Trung bình — Technical risk thấp, business risk (nhà hàng adopt) trung bình
- Dependencies: Cần partnership với 1 nhà hàng yakiniku thật tại Hirama

**ROI Analysis:**
- Benefit: Real validation, real feedback, real case study
- Cost: 8-12 tuần dev + ~¥3,000/tháng ops + hardware (one-time ~¥100,000 cho iPads)
- Payback period: Nếu pilot thành công → tháng 6-7 bắt đầu charge → break-even tháng 10-12
- Opportunity cost: Nếu không pilot mà tiếp tục dev → 6 tháng code thêm vẫn chưa validate PMF

**Đề xuất thực tế:**

- **Làm ngay (< 1 sprint):**
  - Liên hệ 2-3 nhà hàng yakiniku tại Hirama, demo prototype
  - Fix 3 blocking issues (config, POS API, PostgreSQL)
  - Tạo seed script cho real menu data (framework sẵn tại `backend/data/seed_data.py`)

- **Làm sớm (1-3 sprints):**
  - Sprint 1: Config unification + POS real API + PostgreSQL
  - Sprint 2: Basic auth (PIN for POS) + Kitchen-TableOrder WebSocket + Testing critical path
  - Sprint 3: On-site deployment + Staff training + Bug fixing
  - Sprint 4: Parallel run (2 tuần) — Yakiniku.io chạy song song với system hiện tại

- **Để sau / Không làm:**
  - ❌ Pricing model (pilot miễn phí 3 tháng, collect feedback)
  - ❌ Marketing website
  - ❌ Sales team / channel partnerships
  - ❌ Multi-branch features

**Timeline đề xuất:**

```
Tuần 1-2:   Config + POS fix + PostgreSQL migration
Tuần 3-4:   Auth + WebSocket integration + Menu data entry
Tuần 5-6:   Integration testing + Bug fixing
Tuần 7-8:   On-site setup + Staff training
Tuần 9-12:  Parallel run + Iteration based on feedback
Tháng 4-5:  Pilot chính thức (hệ thống cũ backup)
Tháng 6:    Evaluate → quyết định pricing + scale
```

**Dẫn chứng từ codebase:**
- File: `backend/app/config.py#L23` — `DEFAULT_BRANCH: str = "hirama"` — hardcode sẵn cho pilot
- File: `apps/table-order/js/config.js#L17` — `BRANCH_CODE: 'hirama'`
- File: `docker-compose.yml` — PostgreSQL + Redis config sẵn sàng, chỉ thiếu Dockerfile cho backend
- File: `backend/data/seed_data.py` — Seed framework có sẵn cho branches, tables, menu items, customers
- File: `backend/pyproject.toml` — Dependencies clean: `fastapi`, `sqlalchemy`, `asyncpg` (prod), `aiosqlite` (dev), `openai`, `uvicorn`. Không bloated

---

## Tóm tắt lập trường

| # | Điểm | Lập trường | Mức độ tự tin | Effort estimate |
|---|------|-----------|---------------|-----------------|
| 1 | MVP Definition | CÓ ĐIỀU KIỆN — 3 apps (table-order + kitchen + POS), không phải 6 | 🟢 Cao | 3-4 sprints |
| 2 | Trust Building | ĐỒNG Ý — Internal network + PIN auth đủ cho pilot | 🟢 Cao | 2 sprints |
| 3 | Tech Debt vs Speed | CÓ ĐIỀU KIỆN — Fix BLOCKING only, defer ANNOYING | 🟢 Cao | 2-3 sprints |
| 4 | Competitive Positioning | CÓ ĐIỀU KIỆN — Niche yakiniku có giá trị, nhưng cần prove bằng pilot | 🟡 Trung bình | 1-2 sprints |
| 5 | Go-to-Market | ĐỒNG Ý — Pilot Hirama, 8-12 tuần, miễn phí 3 tháng | 🟢 Cao | 4-6 sprints |

**Tổng effort estimate: 8-12 sprints (16-24 tuần) từ hiện tại → pilot chạy ổn định**
**Nếu chỉ tính đến "pilot bắt đầu": 4-6 sprints (8-12 tuần)**

---

## Điều kiện để đồng thuận

Để tôi (Gemini) hoàn toàn đồng ý với chiến lược chung, GPT (Visionary) cần chấp nhận:

1. **AI/OpenAI features là DEFERRED** — Không nằm trong MVP. Chat integration và customer insight extraction (`routers/chat.py`) không cần cho pilot. Chi phí OpenAI API không justify khi chưa có data để extract insights.

2. **Multi-tenant architecture là DEFERRED** — Code hiện tại hardcode `hirama` khắp nơi. Đây là **chấp nhận được** cho pilot. Multi-tenant refactor chỉ khi có branch 2 (estimate: thêm 4-6 sprints).

3. **3 apps, không phải 6** — MVP là table-order + kitchen + POS. Check-in, dashboard SPA, web booking là phase 2. Dashboard Jinja2 legacy dùng cho admin trong pilot.

4. **"Good enough" auth, không phải enterprise auth** — PIN-based cho POS + network-level isolation. Không JWT, không RBAC, không OAuth.

5. **Pilot miễn phí** — Không charge tiền trong 3 tháng đầu. Focus vào learn, không phải earn. Pricing strategy quyết định sau khi có real usage data.

6. **Không Kubernetes, không Redis, không microservices** — 1 VPS, 1 PostgreSQL, 1 FastAPI process. Scale khi cần, không trước.

7. **Doc-code gap được acknowledge** — `docs/ARCHITECTURE.md` là vision document, không phải current state. Thêm disclaimer rõ ràng hoặc tách thành `ARCHITECTURE_VISION.md` và `ARCHITECTURE_CURRENT.md`.

Nếu GPT đồng ý 7 điểm trên, tôi sẵn sàng support vision dài hạn (platform play, AI features, multi-tenant) như **roadmap items** sau khi pilot validate được PMF.
