# 🤝 Final Consensus | Tính khả thi & Chiến lược Go-to-Market | 2026-02-06

---

## Tổng quan
- **Chủ đề**: Tính khả thi & Chiến lược Go-to-Market cho Yakiniku.io
- **Số vòng thảo luận**: 2
- **Ngày bắt đầu → Đồng thuận**: 2026-02-06 → 2026-02-06
- **Participants**: GPT (Visionary), Gemini (Pragmatist)
- **Tỷ lệ đồng thuận cuối**: 15/15 = 100%

---

## Kết luận đồng thuận

### 1. MVP Definition: 3 Apps Core + Keyword AI

**Quyết định**: Launch MVP gồm **Table Order + Kitchen Display + POS Basic**. Check-in, Dashboard SPA, Web booking → Phase 2.

**Lý do**:
- *Visionary*: Core loop (khách order → bếp nhận → thanh toán) tạo giá trị trực tiếp, đủ để validate "Yakiniku OS" concept.
- *Pragmatist*: 3 apps có mức hoàn thiện cao nhất trong codebase. POS backend đã implement 100% (272 LOC), frontend chỉ cần wire 4 API calls.

**Chi tiết kỹ thuật**:
- Table Order (`apps/table-order/`): ✅ Sẵn sàng 80%, app hoàn thiện nhất
- Kitchen Display (`apps/kitchen/`): ✅ Sẵn sàng 65% sau fix config
- POS Basic (`apps/pos/`): 🟡 Cần wire frontend → real API (~0.5 sprint)
- AI: Giữ keyword-based preference tracking (code đã có, cost = 0), tắt OpenAI API

**Hành động tiếp theo**:
- [ ] Copy config pattern từ `apps/table-order/js/config.js` → kitchen, POS (2 giờ)
- [ ] POS frontend: thay mock `loadTables()`, `loadTableOrder()`, `confirmPayment()` bằng real API calls (2-3 ngày)
- [ ] Đảm bảo `OPENAI_API_KEY` để trống trong production config

---

### 2. Trust Building: Pilot tại Hirama, "Run Alongside"

**Quyết định**: Pilot miễn phí 3 tháng tại chi nhánh Hirama (平間), chạy song song với hệ thống hiện tại.

**Lý do**:
- *Visionary*: Thị trường Nhật relationship-driven, trust xây qua demo thực tế tại quán, không qua slide deck. 1 nhà hàng hoàn hảo → video case study → referral network.
- *Pragmatist*: Internal network deployment giảm security risk. Offline fallback của table-order app là điểm mạnh cho trust. UI tiếng Nhật hoàn chỉnh sẵn sàng.

**Chi tiết triển khai**:
- Tuần 1-4: Đặt 2-3 iPad table-order + 1 iPad kitchen display, staff vẫn nhận order song song
- Tuần 5-8: Mở rộng tất cả bàn, kitchen display là primary
- Tuần 9+: Evaluate → chuyển hoàn toàn nếu stable
- Free trial: 3 tháng, auto-extend nếu nhà hàng active (≥50 orders/tuần). Review meeting tháng 3.

**Hành động tiếp theo**:
- [ ] Sign pilot agreement với Hirama (miễn phí, đổi case study rights)
- [ ] Setup dedicated WiFi cho hệ thống tại nhà hàng
- [ ] Nhập real menu data từ nhà hàng (seed framework có sẵn tại `backend/data/seed_data.py`)
- [ ] Tạo video demo 2-3 phút showing full flow

---

### 3. Technical Debt: Fix BLOCKING Only, Defer Phần Còn Lại

**Quyết định**: Phân loại debt thành 3 nhóm rõ ràng. Chỉ fix nhóm BLOCKING trước launch.

**Lý do**:
- *Visionary*: Auth + config là blocking thực sự — deploy không có auth trên network bất kỳ là rủi ro chết người. Nhưng domain-driven architecture hiện tại (5 domain modules) là quyết định đúng cho maintainability.
- *Pragmatist*: "Debt that kills" ≠ "Debt that annoys". POS mock data = kills. Duplicate routers = annoys. Doc-code gap = irrelevant cho pilot.

**🔴 BLOCKING (fix trước launch — Sprint 1-2):**

| # | Item | Effort | Owner |
|---|------|--------|-------|
| 1 | Config unification (copy table-order pattern → 4 apps) | 2 giờ | Frontend |
| 2 | Auth: API key middleware cho tất cả endpoints | 2 ngày | Backend |
| 3 | POS frontend wire real API | 2-3 ngày | Frontend |
| 4 | SQLite → PostgreSQL migration | 0.5 ngày | Backend |
| 5 | Alembic setup (initial migration) | 1 ngày | Backend |

**🟡 ANNOYING (fix trong 3 tháng sau launch):**

| # | Item | Effort |
|---|------|--------|
| 6 | Deprecate legacy order router (`/api/orders` → `/api/tableorder`) | 1 sprint |
| 7 | 5-10 critical path integration tests | 1 tuần |
| 8 | Sentry/error tracking integration | 1-2 ngày |
| 9 | Consolidate dashboards (chọn SPA hoặc Jinja2) | 1 sprint |

**🟢 DEFERRED (sau khi pilot validate PMF):**

| # | Item | Khi nào |
|---|------|---------|
| 10 | Full test coverage (>50%) | Trước branch 2 |
| 11 | CI/CD pipeline | Trước branch 2 |
| 12 | Multi-tenant architecture | Khi có branch 2 |
| 13 | Docker production setup | Khi deploy ngoài internal network |
| 14 | Doc-code gap: tách `ARCHITECTURE.md` thành VISION vs CURRENT | Khi cần onboard dev mới |

---

### 4. Competitive Positioning: "Yakiniku OS", Không Phải "POS"

**Quyết định**: Brand positioning = **"焼肉専門の店舗オペレーションOS"** (Operating System chuyên biệt cho nhà hàng Yakiniku). Không cạnh tranh generic POS.

**Lý do**:
- *Visionary*: Vertical SaaS outperform horizontal 2.5x retention. Market ~20,000 nhà hàng yakiniku → expand sang teppanyaki, shabu-shabu (500K+ nhà hàng) trong 3-5 năm. Event sourcing data = long-term moat.
- *Pragmatist*: 2 differentiators thực sự tồn tại trong code: (1) Station-based kitchen display với yakiniku keywords, (2) Event sourcing order lifecycle tracking. Không thể cạnh tranh Square/Smaregi ở generic POS.

**USP cụ thể (đã có trong code):**
1. **Station-based Kitchen Display**: `STATIONS` object trong `apps/kitchen/js/app.js` phân loại items theo meat keywords (カルビ, ハラミ, タン, ロース, ホルモン...) — domain knowledge mà generic KDS không có
2. **Full Order Lifecycle Tracking**: 21 event types trong `domains/tableorder/events.py` — từ ORDER_CREATED → SERVED, bao gồm GATEWAY tracking
3. **Customer Preference Tracking**: Keyword-based extraction cho yakiniku-specific preferences (タン好き, 厚切り派, 塩派, タレ派)
4. **Table Session Model**: Track thời gian ngồi, phù hợp yakiniku (2-3 tiếng/session, multi-round ordering)

**Hành động tiếp theo**:
- [ ] Landing page: messaging "焼肉専用" rõ ràng
- [ ] Polish kitchen station routing demo với real data
- [ ] Chuẩn bị comparison table: Yakiniku.io vs Smaregi vs AirREGI (focus yakiniku-specific)

---

### 5. Go-to-Market: Hirama Pilot → Lighthouse → Referral

**Quyết định**: Launch sequence 4 phase trong 12-18 tháng đầu.

**Lý do**:
- *Visionary*: Trust trong F&B Nhật xây qua network effect cục bộ — 82% nhà hàng chọn vendor qua giới thiệu. Patience is key — Smaregi mất 5 năm cho 1,000 merchants đầu.
- *Pragmatist*: Infrastructure cho 1 branch chỉ ~¥2,000-3,000/tháng. ROI rõ ràng: validate PMF trước khi invest thêm.

**Phase 1: Dogfooding tại Hirama (Tháng 1-3)**
- Fix blocking tech debt, deploy trên internal WiFi
- 2-3 iPad table-order + 1 iPad kitchen + 1 POS station
- "Run alongside" hệ thống cũ → chuyển dần khi stable

**Phase 2: Lighthouse Customers (Tháng 4-6)**
- Video testimonial từ Hirama (3 phút, tiếng Nhật)
- Mời 2-3 chủ nhà hàng yakiniku lân cận đến Hirama xem demo thực tế
- Free 3-month trial cho lighthouse customers

**Phase 3: Early Growth (Tháng 7-12)**
- Target: 5-10 paying merchants
- Pricing: Starter ¥29,800/tháng (Table Order + Kitchen + POS Basic)
- Bắt đầu referral program (紹介プログラム)

**Phase 4: Channel Expansion (Tháng 12-18)**
- Partner với 1-2 meat suppliers (仕入業者) cho co-marketing
- Mở rộng sang restaurant equipment sellers, accounting firms
- Evaluate expansion sang teppanyaki/shabu-shabu

**Chi phí vận hành (1 branch)**:
| Item | Cost/tháng |
|------|-----------|
| VPS (2GB RAM) | ~¥1,800 ($12) |
| PostgreSQL | Included |
| Domain (optional) | ~¥100 ($1) |
| OpenAI (tắt cho pilot) | ¥0 |
| **Total** | **~¥2,000-3,000/tháng** |

---

## Lộ trình thực hiện

| Giai đoạn | Timeline | Hành động | Ưu tiên |
|-----------|----------|-----------|---------|
| **Sprint 1-2** | Tuần 1-4 | Config fix, Auth, PostgreSQL, Alembic, POS wire | P0 — BLOCKING |
| **Sprint 3-4** | Tuần 5-8 | Integration testing, on-site deploy, staff training | P0 — LAUNCH |
| **Sprint 5-6** | Tuần 9-12 | Parallel run, bug fixing, feedback iteration | P0 — STABILIZE |
| **Quarter 2** | Tháng 4-6 | Lighthouse customers, video case study, fix ANNOYING debt | P1 |
| **Quarter 3-4** | Tháng 7-12 | Early growth, pricing, referral program | P1 |
| **Year 2** | Tháng 13-24 | 10-20 merchants, multi-branch architecture, partner channels | P2 |
| **Year 3-5** | Tháng 25-60 | Expand verticals, AI enhancement, platform play | P2 |
| **Year 5-10+** | 60+ tháng | F&B Operating System, data monetization, franchise enablement | P3 |

---

## Trade-offs đã chấp nhận

| # | Trade-off | Tại sao cả hai chấp nhận |
|---|-----------|-------------------------|
| 1 | **Skip 3 apps (checkin, dashboard SPA, web)** cho MVP | Focus > breadth. 3 apps core tạo complete loop. Các app còn lại thêm sau khi pilot stable. |
| 2 | **Tắt OpenAI API** cho pilot | Chi phí không justify khi chưa có data thực. Keyword fallback đủ cho preference tracking ban đầu. Bật khi có ≥100 conversations. |
| 3 | **POS Basic thay vì Full POS** | Không payment gateway, không discount, không receipt printer. Manual cash/card collection. Đủ cho pilot, upgrade dần. |
| 4 | **3 tháng free thay vì dài hơn** | Tạo urgency tích cực, tránh precedent xấu cho pricing. Auto-extend nếu active. |
| 5 | **No full RBAC, chỉ API key + PIN** | Internal network deployment giảm risk. Full auth cho phase 2 khi expose ra internet. |
| 6 | **No CI/CD, no full tests** cho pilot | Manual deploy + manual test chấp nhận được cho 1 branch. Invest trước branch 2. |
| 7 | **Doc-code gap giữ nguyên** | Docs là vision document, không phải current state. Mark rõ ràng, fix khi onboard dev mới. |

---

## Appendix: Lịch sử thảo luận

| Round | GPT Review | Gemini Review | Synthesis | Đồng thuận |
|-------|-----------|---------------|-----------|------------|
| 1 | [review_gpt_round1](review_gpt_round1_2026-02-06.md) | [review_gemini_round1](review_gemini_round1_2026-02-06.md) | [synthesis_round1](synthesis_round1_2026-02-06.md) | 73% (11/15) |
| 2 | [review_gpt_round2](review_gpt_round2_2026-02-06.md) | [review_gemini_round2](review_gemini_round2_2026-02-06.md) | [synthesis_round2](synthesis_round2_2026-02-06.md) | 100% (15/15) |

---

## Checklist hành động ngay (tuần 1-2)

- [ ] Config: Copy `window.location.hostname` pattern → kitchen, POS, checkin, dashboard
- [ ] Auth: Implement API key middleware cho backend endpoints
- [ ] DB: Switch SQLite → PostgreSQL (docker-compose config sẵn)
- [ ] DB: Setup Alembic initial migration
- [ ] POS: Wire `loadTables()`, `loadTableOrder()`, `confirmPayment()` → real API
- [ ] Kitchen: Fix route từ legacy `/api/orders/kitchen` → domain `/api/kitchen/orders`
- [ ] Config: Đảm bảo `OPENAI_API_KEY` để trống trong production
- [ ] Business: Liên hệ Hirama, ký pilot agreement
- [ ] Data: Nhập real menu data từ nhà hàng vào seed script
