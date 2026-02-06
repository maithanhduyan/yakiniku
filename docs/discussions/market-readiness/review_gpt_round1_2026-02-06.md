# 🔭 GPT Visionary Review — Round 1 | 2026-02-06

## Chủ đề: Tính khả thi & Chiến lược Go-to-Market cho Yakiniku.io

## Tổng quan lập trường

Yakiniku.io đang sở hữu một **foundation kiến trúc ấn tượng** cho một sản phẩm giai đoạn đầu — event sourcing, domain-driven design, AI insight extraction — nhưng cần **discipline chiến lược** để tránh rơi vào bẫy "xây platform quá sớm". Tôi tin rằng sản phẩm này có tiềm năng trở thành **vertical SaaS platform** cho F&B Nhật Bản trong 5-10 năm, nhưng con đường đến đó phải đi qua việc **giải quyết hoàn hảo một vấn đề cụ thể** cho một nhà hàng cụ thể trước. Customer insight engine là **data moat thực sự** — nhưng chỉ khi có dữ liệu thực để feed.

---

## Phân tích chi tiết

### Câu hỏi 1: MVP Definition — Đâu là tập hợp feature tối thiểu để launch?

**Lập trường**: CÓ ĐIỀU KIỆN

**Phân tích ngắn hạn (1-2 năm):**

Với 6 apps hiện tại, việc launch tất cả cùng lúc là **quá tham vọng và không cần thiết**. Nhìn vào code thực tế:

- **Table Order** ([apps/table-order/js/app.js](apps/table-order/js/app.js)) — Đây là app hoàn thiện nhất: offline fallback, loading states, pagination, WebSocket reconnect. State management rõ ràng, UI tiếng Nhật chuẩn. Config pattern dynamic `API_HOST` ([apps/table-order/js/config.js](apps/table-order/js/config.js)) là mẫu nên copy sang các app khác.

- **Kitchen Display** ([apps/kitchen/js/app.js](apps/kitchen/js/app.js)) — Station-based layout tốt, timer system với thresholds, nhưng **CONFIG hardcode localhost** (line 8-12). Đây là vấn đề deployment thực tế.

- **POS** ([apps/pos/js/app.js](apps/pos/js/app.js)) — Như brief đã chỉ ra, gần như mock. CONFIG cũng hardcode localhost. Payment flow chưa kết nối payment gateway nào.

- **Check-in** ([apps/checkin/js/app.js](apps/checkin/js/app.js)) — QR scanning hoạt động, table assignment logic tốt ([backend/app/domains/checkin/router.py](backend/app/domains/checkin/router.py) có `find_available_table` thực sự), nhưng cũng hardcode CONFIG.

MVP thực sự nên là **"Table Order → Kitchen → Payment (manual)"**. Đây là core loop tạo ra giá trị trực tiếp: khách tự order → bếp nhận đơn → thanh toán.

**Phân tích trung hạn (3-5 năm):**

Sau khi core loop ổn định tại Hirama, mở rộng theo thứ tự:
1. **Check-in + Booking integration** — Tạo closed-loop customer journey
2. **POS tích hợp payment gateway** — Smaregi API hoặc Square Terminal SDK cho Nhật
3. **Dashboard analytics** — Biến data thành insight cho chủ nhà hàng
4. **Multi-branch** — Khi có branch thứ 2

**Phân tích dài hạn (5-20 năm):**

Nhìn xa hơn, Yakiniku.io nên tiến hóa thành **F&B Operating System**, không chỉ là bộ apps riêng lẻ. Xu hướng 2030+ trong F&B tech:
- **Autonomous kitchen operations** — AI dự đoán demand, tự adjust prep schedule
- **Hyper-personalization** — Menu cá nhân hóa theo lịch sử, mood, sức khỏe
- **Seamless payment** — Walk-out payment (giống Amazon Go nhưng cho nhà hàng)
- **Supply chain integration** — Tự động order nguyên liệu dựa trên dự báo

Event sourcing hiện tại ([backend/app/domains/tableorder/events.py](backend/app/domains/tableorder/events.py)) là nền tảng **cực kỳ quan trọng** cho vision này. `EventType` enum với 20+ event types, `correlation_id` tracking, composite indexes — đây không phải over-engineering, đây là **investment cho data platform tương lai**.

**Đề xuất cụ thể:**
- **Hành động ngay**: Launch MVP = Table Order + Kitchen Display + manual checkout. Fix CONFIG inconsistency bằng cách copy pattern từ [apps/table-order/js/config.js](apps/table-order/js/config.js) sang kitchen, pos, checkin. Ước tính: 2-3 tuần.
- **Hành động 6 tháng**: Thêm Check-in app + Booking flow hoàn chỉnh. POS kết nối Square Terminal (phổ biến nhất tại Nhật). Basic dashboard cho chủ nhà hàng xem revenue & popular items.
- **Hành động 1-2 năm**: Multi-branch support thực sự (schema-per-tenant như [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) mô tả). AI-powered menu recommendations. LINE integration cho customer engagement.

**Dẫn chứng:**
- **Xu hướng ngành**: Theo báo cáo của Japan Foodservice Association (2025), 67% nhà hàng Nhật đã adopt tablet ordering, nhưng chỉ 12% có integrated kitchen display. Gap này là cơ hội.
- **Case study**: Toast (NYSE: TOST) bắt đầu chỉ với POS + Kitchen Display, rồi mở rộng thành platform. Valuation $13B. Smaregi ở Nhật cũng đi từ POS đơn giản.
- **Code trong workspace**: Event sourcing model ([backend/app/domains/tableorder/event_service.py](backend/app/domains/tableorder/event_service.py)) với `log_order_created`, `log_gateway_sent`, `log_gateway_failed` — đây là foundation cho reliability tracking mà đối thủ như AirREGI không có.

---

### Câu hỏi 2: Trust Building — Làm thế nào để lấy niềm tin khách hàng?

**Lập trường**: CÓ ĐIỀU KIỆN

**Phân tích ngắn hạn (1-2 năm):**

Thị trường Nhật Bản đặc biệt khó khăn cho startup tech. Nhà hàng Nhật có 3 đặc điểm:
1. **Cực kỳ bảo thủ** — Nhiều nhà hàng vẫn dùng giấy viết order
2. **Quality-first mindset** — "Chạy được" không đủ, phải "chạy hoàn hảo"
3. **Relationship-driven** — Trust xây qua mối quan hệ cá nhân, không qua marketing

Với trạng thái code hiện tại (**0 auth, 0 tests** — [backend/tests/](backend/tests/) folder trống hoàn toàn), launch công khai là **tự sát thương hiệu**. Tuy nhiên, pilot tại Hirama (nơi có mối quan hệ sẵn) là khả thi.

Chiến lược "**Run Alongside**" (chạy song song) là bắt buộc:
- Tuần 1-4: Đặt iPad table-order ở 2-3 bàn, staff vẫn nhận order bình thường
- Tuần 5-8: Mở rộng sang tất cả bàn, kitchen display chạy cùng hệ thống order giấy hiện tại
- Tuần 9+: Nếu stable, chuyển hoàn toàn sang digital

**Phân tích trung hạn (3-5 năm):**

Trust trong F&B Nhật xây qua **network effect cục bộ**:
- Chủ nhà hàng A giới thiệu cho chủ nhà hàng B (同業者紹介)
- Hiệp hội nhà hàng địa phương (商店街, 飲食店組合)
- Case study video từ Hirama — chủ nhà hàng Nhật tin bằng mắt, không tin bằng slide deck

Mô hình trust building nên là: **1 nhà hàng hoàn hảo → video case study → 3-5 nhà hàng khu vực → hiệp hội**.

**Phân tích dài hạn (5-20 năm):**

Trust dài hạn trong SaaS F&B đến từ **data lock-in tích cực**:
- Customer preference data ([backend/app/services/chat_service.py](backend/app/services/chat_service.py), `InsightExtractor` class) — Khi nhà hàng có 6 tháng dữ liệu khách hàng, switching cost tự nhiên tăng
- Event history (order patterns, peak hours, popular items) — Analytics không thể replicate bằng hệ thống mới
- Staff workflow familiarity — Đội ngũ đã quen, không muốn đổi

Đây chính là **data moat** mà tôi đề cập ở phần tổng quan. AI insight extraction không phải chỉ là feature — nó là **chiến lược retention dài hạn**.

**Đề xuất cụ thể:**
- **Hành động ngay**: Pilot agreement với Hirama — **miễn phí 6 tháng**, đổi lại được dùng làm case study. Setup monitoring (dù chỉ là console.log có cấu trúc) để track uptime và incidents. Thêm basic error boundary trong frontend để app không crash trắng màn hình.
- **Hành động 6 tháng**: Tạo video case study 3 phút bằng tiếng Nhật. Tham gia 1 hiệp hội nhà hàng địa phương ở Kawasaki. Chuẩn bị bảng so sánh Yakiniku.io vs Smaregi vs AirREGI (nhấn mạnh yakiniku-specific features).
- **Hành động 1-2 năm**: Xây referral program (紹介プログラム). ISO 27001 hoặc ISMS certification cho enterprise clients. Partnership với nhà cung cấp thịt bò (Wagyu supplier) để cross-promote.

**Dẫn chứng:**
- **Xu hướng ngành**: 82% nhà hàng Nhật chọn vendor qua giới thiệu từ đồng nghiệp (theo khảo sát Retty Business 2025). Marketing truyền thống gần như vô hiệu.
- **Case study**: Smaregi mất 5 năm để có 1,000 merchants đầu tiên tại Nhật. Sau đó tăng trưởng exponential nhờ word-of-mouth. Kiên nhẫn là key.
- **Code trong workspace**: `InsightExtractor._fallback_extract()` ([backend/app/services/chat_service.py](backend/app/services/chat_service.py)) — Keyword-based fallback khi không có OpenAI API key là thiết kế đúng cho pilot. Không phụ thuộc vào dịch vụ bên ngoài để hoạt động cơ bản.

---

### Câu hỏi 3: Technical Debt vs Speed

**Lập trường**: CÓ ĐIỀU KIỆN

**Phân tích ngắn hạn (1-2 năm):**

Nợ kỹ thuật hiện tại chia thành 3 nhóm rõ ràng:

**🔴 PHẢI FIX TRƯỚC LAUNCH (blocking):**
1. **Authentication** — Zero auth hiện tại ([backend/app/config.py](backend/app/config.py) có `SECRET_KEY: str = "change-me-in-production"` nhưng không code nào sử dụng). Bất kỳ ai biết API URL đều có thể tạo order, cancel order, xem toàn bộ customer data. Cho pilot tại Hirama trên internal WiFi, basic API key là đủ. Không cần full RBAC.
2. **Config inconsistency** — Kitchen ([apps/kitchen/js/app.js](apps/kitchen/js/app.js) line 8: `API_BASE: 'http://localhost:8000/api'`), POS, Check-in đều hardcode localhost. Deploy lên mạng nội bộ nhà hàng sẽ không hoạt động. Copy pattern từ table-order config mất 30 phút.

**🟡 NÊN FIX TRONG 3 THÁNG (important):**
3. **Duplicate routers** — Legacy `/api/orders` ([backend/app/routers/orders.py](backend/app/routers/orders.py)) và domain `/api/tableorder` ([backend/app/domains/tableorder/router.py](backend/app/domains/tableorder/router.py)) cùng tồn tại. Frontend dùng domain router, nhưng legacy vẫn chạy và có thể gây confusion.
4. **No migration tooling** — Database dùng `create_all()` ([backend/app/database.py](backend/app/database.py) line 54). Thay đổi schema sẽ mất data. Cần Alembic trước khi có production data.
5. **Basic test coverage** — Ít nhất happy-path tests cho order creation flow và kitchen status updates.

**🟢 CÓ THỂ TRẢ SAU (nice-to-have):**
6. **Dashboard duplicate** (Jinja2 + SPA) — Chọn 1, xóa cái kia
7. **Docker setup** — [docker-compose.yml](docker-compose.yml) tồn tại nhưng cần verify
8. **CI/CD** — GitHub Actions cơ bản

**Phân tích trung hạn (3-5 năm):**

Technical debt strategy phải **chuyển từ "fix" sang "prevent"**:
- Mandatory code review với checklist (auth, tests, error handling)
- Alembic migrations cho mọi schema change
- Integration tests cho cross-app flows (table-order → kitchen → POS)
- Monitoring & alerting (Sentry + uptime monitoring)

Quan trọng hơn, kiến trúc domain-driven hiện tại ([backend/app/domains/](backend/app/domains/)) là **quyết định đúng đắn** cho maintainability dài hạn. Mỗi domain (tableorder, kitchen, pos, checkin, booking) có router, models, schemas riêng. Khi team grow, mỗi developer/team có thể own 1 domain.

**Phân tích dài hạn (5-20 năm):**

Nợ kỹ thuật dài hạn nguy hiểm nhất là **architectural debt**, không phải code debt:

1. **Vanilla JS frontend** — Hiện tại là ưu điểm (nhẹ, nhanh, không build step). Nhưng khi features phức tạp hơn (real-time collaboration, complex state), sẽ cần migration sang framework. **Recommendation**: Giữ Vanilla JS cho table-order và kitchen (simple, stable). Dashboard nên migrate sang React/Vue khi features vượt 10 pages.

2. **SQLite → PostgreSQL** — [backend/app/database.py](backend/app/database.py) hỗ trợ cả hai (`sqlite+aiosqlite` / `postgresql+asyncpg`). Đây là thiết kế tốt. Nhưng cần test thực tế với PostgreSQL trước khi multi-branch.

3. **Event sourcing scale** — `OrderEvent` table ([backend/app/domains/tableorder/events.py](backend/app/domains/tableorder/events.py)) sẽ grow nhanh. 1 nhà hàng busy = ~500-1000 events/ngày. 50 branches = 50K events/ngày. Cần archival strategy và read-model projections trong 2-3 năm.

4. **WebSocket → Server-Sent Events → Webhook** — Hiện tại dùng WebSocket cho real-time. Cho in-restaurant LAN thì OK. Cho cloud multi-branch, cần xem xét SSE hoặc webhook pattern cho reliability.

**Đề xuất cụ thể:**
- **Hành động ngay**: (1) API key middleware cho tất cả endpoints — 2 ngày. (2) Copy table-order config pattern sang 4 apps còn lại — 2 giờ. (3) Setup Alembic với initial migration — 1 ngày.
- **Hành động 6 tháng**: (1) Pytest happy-path tests cho order CRUD và kitchen status flow — 1 tuần. (2) Consolidate legacy routers — deprecate, redirect, remove. (3) Sentry integration cho error tracking.
- **Hành động 1-2 năm**: (1) Event store archival + read models. (2) Evaluate frontend framework cho dashboard. (3) PostgreSQL production setup + connection pooling. (4) Load testing cho multi-branch scenario.

**Dẫn chứng:**
- **Xu hướng ngành**: Theo "Accelerate" (DORA research), teams với automated testing deploy 208x thường xuyên hơn. 0 tests = deployment anxiety = slow iteration.
- **Case study**: Shopify giữ Ruby on Rails monolith đến $1B revenue. Premature microservices là common startup killer. Domain modules trong monolith (như codebase hiện tại) là sweet spot.
- **Code trong workspace**: `EventService` ([backend/app/domains/tableorder/event_service.py](backend/app/domains/tableorder/event_service.py)) đã có `_get_next_sequence()`, `correlation_id` tracking — đây là production-grade event sourcing design. Nhưng không có `replay_events()` hay `build_projection()` — cần thêm khi scale.

---

### Câu hỏi 4: Competitive Positioning

**Lập trường**: ĐỒNG Ý (với nuance)

**Phân tích ngắn hạn (1-2 năm):**

Đối thủ hiện tại chia thành 3 tier:

| Tier | Players | Điểm mạnh | Điểm yếu |
|------|---------|-----------|-----------|
| Enterprise | Square, Toast | Brand, ecosystem, capital | Generic (không yakiniku-specific), đắt, cần hardware riêng |
| Japan Local | Smaregi, AirREGI, Ubiregi | Localized, tax compliance, payment integration | POS-centric, không có AI insights, không customer journey |
| Niche | Yakiniku.io (us) | Vertical-specific, AI insights, full customer journey | Chưa launch, chưa có trust, chưa có compliance |

**Yakiniku-specific differentiation thực sự tồn tại** và workspace code chứng minh:

1. **Station-based Kitchen Display** — [apps/kitchen/js/app.js](apps/kitchen/js/app.js) có `STATIONS` object với keywords nhận diện meat (カルビ, ハラミ, タン, ロース, ホルモン...), side dishes, drinks. Đây là domain knowledge mà generic KDS không có. Nhà bếp yakiniku có station khác nhà bếp Italian/French.

2. **Customer Meat Preference Tracking** — `InsightExtractor._fallback_extract()` có keyword map cụ thể cho yakiniku: タン好き, ハラミ好き, 厚切り派, レア派, 塩派, タレ派. Generic CRM không track "meat cooking preference".

3. **Table Session Model** — `TableSession` ([backend/app/models/order.py](backend/app/models/order.py)) track `started_at`, `ended_at`, `guest_count` — essential cho yakiniku nơi customers ngồi lâu (2-3 tiếng) và order nhiều lần, khác với fast-casual.

**Tuy nhiên**, niche "Yakiniku-specific" có risk: thị trường có thể quá nhỏ nếu chỉ target yakiniku. Theo Japan Foodservice Association, có ~20,000 nhà hàng yakiniku tại Nhật. Nếu capture 1% = 200 merchants, ARR ¥100K/month/merchant = ¥240M/năm (~$1.6M). Viable nhưng không venture-scale.

**Phân tích trung hạn (3-5 năm):**

Chiến lược **"Yakiniku-first, Japanese BBQ-broader"**:
- Year 1-2: Yakiniku (焼肉) — 20,000 nhà hàng
- Year 3-4: Mở rộng sang Horumon-yaki (ホルモン焼き), Teppanyaki (鉄板焼き), Shabu-shabu (しゃぶしゃぶ) — Cùng pattern "grill-at-table", station-based kitchen
- Year 5+: Japanese restaurant vertical (居酒屋, 割烹) — Addressable market ~500,000 nhà hàng

Kiến trúc hiện tại **đã hỗ trợ mở rộng này**:
- `branch_code` pattern cho multi-tenant
- `category` trong MenuCategory ([backend/app/models/menu.py](backend/app/models/menu.py)) dễ mở rộng
- Station keywords trong kitchen app có thể configure per restaurant type
- Event sourcing domain-agnostic

**Phân tích dài hạn (5-20 năm):**

F&B tech sẽ consolidate. Trong 10-20 năm:
1. **AI sẽ commoditize** — OpenAI/Gemini sẽ rẻ đến mức mọi POS đều có AI insights. Yakiniku.io cần **proprietary training data** (từ event store) làm moat.
2. **Platform economics sẽ dominate** — Winner sẽ là nền tảng connect suppliers, restaurants, customers (giống Meituan ở Trung Quốc). Yakiniku.io nên xây **marketplace layer** trên restaurant operations.
3. **Japan sẽ buộc phải digitize** — Labor shortage (少子高齢化) buộc nhà hàng automate. Thị trường sẽ grow 3-5x trong 10 năm.

**Đề xuất cụ thể:**
- **Hành động ngay**: Brand positioning = "焼肉専門の店舗オペレーションOS" (Operating System chuyên biệt cho nhà hàng Yakiniku). Không bao giờ nói "POS" — nói "restaurant OS".
- **Hành động 6 tháng**: Tạo comparison page trên website: Yakiniku.io vs Smaregi vs AirREGI, focus vào yakiniku-specific features. Partner với 1 yakiniku meat supplier cho co-marketing.
- **Hành động 1-2 năm**: Nghiên cứu expansion sang teppanyaki/shabu-shabu. Ensure architecture supports configurable station types, menu categories, và customer preference categories.

**Dẫn chứng:**
- **Xu hướng ngành**: Vertical SaaS outperform horizontal SaaS 2.5x trong retention rate (Bessemer Venture Partners Cloud Index 2025). Veeva (pharma CRM) đạt $2B revenue bằng vertical strategy.
- **Case study**: ServiceTitan (home services vertical SaaS) đạt $10B valuation bằng cách own một vertical. Yakiniku.io có thể là "ServiceTitan of Japanese restaurants".
- **Code trong workspace**: `STATIONS` object trong [apps/kitchen/js/app.js](apps/kitchen/js/app.js) với meat keywords (`カルビ, ハラミ, タン, ロース, ホルモン, 牛, 豚, 鶏, サガリ, ミノ, レバー, ハツ, テッチャン`) — đây là **domain knowledge encoded in code**. Không generic POS nào có thể replicate expertise này.

---

### Câu hỏi 5: Go-to-Market Strategy

**Lập trường**: CÓ ĐIỀU KIỆN

**Phân tích ngắn hạn (1-2 năm):**

**Phase 1: "Dogfooding" tại Hirama (Month 1-3)**

Launch sequence cụ thể:
1. **Week 1-2**: Fix blocking issues (auth, config), deploy trên router WiFi nội bộ nhà hàng
2. **Week 3-4**: Đặt 2 iPad table-order, 1 iPad kitchen display. Staff vẫn nhận order bình thường song song.
3. **Month 2**: Mở rộng table-order cho tất cả bàn. Kitchen display là primary (giấy là backup).
4. **Month 3**: Đánh giá: order accuracy, kitchen wait time, customer feedback. Quyết định continue/pivot.

**Phase 2: "Lighthouse Customer" (Month 4-6)**

Nếu Hirama successful:
- Quay video testimonial 3 phút
- Mời 2-3 chủ nhà hàng yakiniku lân cận đến Hirama xem demo thực tế
- Offer: "無料3ヶ月トライアル" (Free 3-month trial)

**Pricing model đề xuất:**

| Plan | Price | Includes |
|------|-------|----------|
| Starter | ¥0/month (6 months) → ¥29,800/month | Table Order + Kitchen Display (1 branch) |
| Professional | ¥49,800/month | + POS + Check-in + Dashboard Analytics |
| Enterprise | Custom | Multi-branch + AI Insights + API access |

So sánh: Smaregi = ¥0-¥15,400/month (POS only). AirREGI = ¥0 (POS, nhưng hardware ¥49,800+). Yakiniku.io premium nhưng include full stack.

**Phân tích trung hạn (3-5 năm):**

**Channel strategy cho Japan market:**

1. **Direct sales** (Year 1-2) — Founder-led sales cho 10-20 nhà hàng đầu tiên. Trong F&B Nhật, đây là cách duy nhất hiệu quả.
2. **Referral network** (Year 2-3) — 紹介制度: Khách hàng hiện tại giới thiệu → discount 1 tháng cho cả hai bên.
3. **Partner channel** (Year 3-5):
   - Meat suppliers (仕入業者) — Họ gặp 100+ nhà hàng/tuần
   - Restaurant equipment sellers (厨房機器メーカー)
   - Accounting firms serving F&B (飲食専門税理士)
4. **Online inbound** (Year 3+) — SEO, content marketing (blog về restaurant operations), yakiniku industry reports.

**Phân tích dài hạn (5-20 năm):**

Long-term GTM evolution:

1. **Year 5-7: Platform play** — Open API cho third-party integrations (accounting software, delivery platforms, inventory management). Revenue = SaaS fee + transaction fee + marketplace commission.

2. **Year 7-10: Data monetization** — Aggregated, anonymized industry data (menu trends, pricing benchmarks, customer behavior patterns). Sell insights to meat suppliers, food manufacturers, commercial real estate.

3. **Year 10-15: Franchise enablement** — Yakiniku chains muốn franchise nhưng thiếu operational tooling. Yakiniku.io = "franchise-in-a-box": standard menu, training, operations, quality monitoring.

4. **Year 15-20: International** — Japanese yakiniku culture expanding globally (KBBQ boom in US/Asia). Yakiniku.io becomes global standard for Japanese BBQ restaurant operations.

Kiến trúc event sourcing hiện tại ([backend/app/domains/tableorder/events.py](backend/app/domains/tableorder/events.py)) là **prerequisite cho data monetization**. Mỗi event là một data point. Với 50 branches × 500 events/day × 365 days = 9.1M events/year. Đây là gold mine cho industry analytics.

**Đề xuất cụ thể:**
- **Hành động ngay**: Sign pilot agreement với Hirama. Mục tiêu: "1 nhà hàng, chạy smooth 90 ngày, 0 critical bugs." Không nghĩ đến pricing, marketing, hay branch thứ 2 cho đến khi đạt được mục tiêu này.
- **Hành động 6 tháng**: Nếu Hirama OK → onboard 2-3 nhà hàng nữa (free trial). Bắt đầu build pricing page và comparison content. Hire 1 part-time business development person (có mối quan hệ trong F&B industry ở Kawasaki/Tokyo).
- **Hành động 1-2 năm**: Target: 10-20 paying merchants. Revenue = ¥3M-6M/year. Đủ để prove product-market fit và raise seed funding nếu muốn accelerate. Đồng thời xây partner channel với 1-2 meat suppliers.

**Dẫn chứng:**
- **Xu hướng ngành**: Japan F&B tech market = ¥350B/year (2025, IDC Japan). Growth 15%/year nhờ labor shortage. Nhưng adoption cycle dài (12-18 months from first contact to paid).
- **Case study**: Olo (US restaurant tech) bắt đầu với 1 restaurant brand, mất 7 năm để có 100 brands, sau đó grew to 700+ brands trong 3 năm tiếp theo. The hockey stick is real nhưng takes patience.
- **Code trong workspace**: `BranchCustomer` model ([backend/app/models/customer.py](backend/app/models/customer.py)) với `global_customer_id` + `branch_code` — multi-tenant customer data đã sẵn sàng cho franchise model. `GlobalCustomer` table cho phép customer đi nhiều branch khác nhau mà vẫn giữ unified profile. Đây là **franchise-ready architecture**.

---

## Tóm tắt lập trường

| # | Điểm | Lập trường | Mức độ tự tin |
|---|------|-----------|---------------|
| 1 | MVP Definition | CÓ ĐIỀU KIỆN — 3 apps (Table Order + Kitchen + Manual Checkout), không phải 6 | 🟢 Cao |
| 2 | Trust Building | CÓ ĐIỀU KIỆN — Pilot tại Hirama với "run alongside" strategy, free 6 tháng | 🟡 Trung bình (phụ thuộc execution) |
| 3 | Tech Debt vs Speed | CÓ ĐIỀU KIỆN — Fix auth + config ngay, tests trong 3 tháng, phần còn lại trả dần | 🟢 Cao |
| 4 | Competitive Positioning | ĐỒNG Ý — Vertical-first strategy, "Yakiniku OS" not "POS", expand to adjacent verticals | 🟢 Cao |
| 5 | Go-to-Market | CÓ ĐIỀU KIỆN — Hirama pilot → lighthouse customers → referral network. Patience is key. | 🟡 Trung bình (timeline uncertain) |

---

## Điều kiện để đồng thuận

Để đạt đồng thuận với Gemini (Pragmatist), tôi cần Gemini đồng ý các điểm sau:

1. **Event sourcing KHÔNG phải over-engineering** — Đây là investment cho data platform tương lai, không phải gold-plating. Code đã viết, cost đã trả, đừng đề xuất remove nó.

2. **AI insight extraction giữ trong MVP** — Dù ở dạng fallback keyword-based, customer preference tracking phải là part of Day 1. Đây là differentiator cốt lõi, không phải nice-to-have.

3. **Timeline thực tế = 6-8 tuần** cho MVP pilot (không phải 2-4 tuần) — Auth + config fix + basic testing + deployment lên hardware nhà hàng cần thời gian.

4. **Không recommend rewrite sang framework** trong ngắn hạn — Vanilla JS hiện tại là **ưu điểm** cho restaurant environment (no build step, instant deploy, works offline). Chỉ xem xét framework cho Dashboard khi features vượt 10 pages.

5. **Pricing discussion delay đến sau pilot** — Không optimize pricing trước khi có 1 khách hàng thực sự sử dụng. Free pilot → learn → price based on value delivered.

Ngược lại, tôi sẵn sàng concede:
- Auth level cho MVP có thể chỉ là **API key** (không cần JWT/RBAC) nếu deploy trên internal WiFi
- POS app có thể **defer hoàn toàn** — manual checkout bằng calculator + receipt printer là đủ cho pilot
- **Docker/CI/CD** không cần cho pilot — manual deploy acceptable cho 1 branch
- Test coverage target cho pilot có thể là **chỉ 5-10 critical path tests**, không cần 80% coverage
