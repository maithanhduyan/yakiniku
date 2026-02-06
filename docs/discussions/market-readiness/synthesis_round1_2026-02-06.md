# 🎼 Synthesis — Round 1 | 2026-02-06

## Chủ đề: Tính khả thi & Chiến lược Go-to-Market cho Yakiniku.io

---

## 📊 Bảng đồng thuận

| # | Điểm thảo luận | GPT (Visionary) | Gemini (Pragmatist) | Đồng thuận? |
|---|----------------|-----------------|---------------------|-------------|
| 1 | MVP = 3 apps core (table-order + kitchen + checkout) | ✅ Đồng ý 3 apps, đề xuất "manual checkout" thay POS | ✅ Đồng ý 3 apps, nhưng muốn POS kết nối real API | ⚠️ Gần đồng thuận |
| 2 | Pilot tại Hirama, miễn phí | ✅ Free 6 tháng, "run alongside" strategy | ✅ Free 3 tháng, parallel run 2 tuần | ⚠️ Gần đồng thuận |
| 3 | Fix config inconsistency ngay | ✅ Copy table-order pattern, ~2 giờ | ✅ Copy table-order pattern, ~15 phút/app | ✅ Đồng thuận |
| 4 | Fix auth trước launch | ✅ API key middleware, 2 ngày | ✅ Network isolation + PIN cho POS | ✅ Đồng thuận |
| 5 | Vertical positioning "Yakiniku OS" | ✅ "焼肉専門の店舗オペレーションOS" | ✅ Niche có giá trị, cần prove bằng pilot | ✅ Đồng thuận |
| 6 | Defer multi-tenant, K8s, Redis | ✅ Multi-tenant khi branch 2 | ✅ 1 VPS + 1 PostgreSQL đủ | ✅ Đồng thuận |
| 7 | Defer full test coverage | ✅ Chỉ 5-10 critical path tests | ✅ Manual testing cho pilot, tests trước branch 2 | ✅ Đồng thuận |
| 8 | Vanilla JS giữ nguyên | ✅ Ưu điểm cho restaurant env, không rewrite | ✅ Không cần framework cho pilot | ✅ Đồng thuận |
| 9 | Event sourcing giữ nguyên | ✅ Investment cho data platform tương lai | (Không phản đối, nhưng không nhắc đến) | ✅ Đồng thuận |
| 10 | AI/OpenAI trong MVP | ✅ Giữ ít nhất fallback keyword-based | ❌ DEFERRED hoàn toàn, tắt cho pilot | ❌ Bất đồng |
| 11 | POS trong MVP | ✅ Defer POS, manual checkout đủ | ❌ POS kết nối real API, backend đã implement | ❌ Bất đồng |
| 12 | Timeline pilot-ready | ✅ 6-8 tuần | ✅ 8-12 tuần | ⚠️ Gần đồng thuận |
| 13 | Pricing discussion | ✅ Delay đến sau pilot | ✅ Delay, free 3 tháng | ✅ Đồng thuận |
| 14 | Doc-code gap xử lý | (Không nhắc cụ thể) | ✅ Tách ARCHITECTURE_VISION vs CURRENT | ✅ Đồng thuận |
| 15 | Consolidate duplicate routers | ✅ Deprecate legacy trong 6 tháng | ✅ Deprecate, redirect legacy → domain | ✅ Đồng thuận |

---

## ✅ Các điểm đã đồng thuận (11/15)

1. **MVP = 3 apps core**: Cả hai đồng ý không launch 6 apps cùng lúc. Core loop: khách order → bếp nhận → thanh toán.
2. **Pilot tại Hirama**: Cả hai đồng ý pilot miễn phí, "run alongside" hệ thống cũ.
3. **Config fix ngay lập tức**: Copy dynamic `API_HOST` pattern từ `apps/table-order/js/config.js` sang 4 apps còn lại.
4. **Auth trước launch**: Cần security tối thiểu, ít nhất network-level + API key/PIN.
5. **Vertical positioning**: "Yakiniku OS" — không cạnh tranh generic POS, tập trung niche.
6. **Defer infrastructure phức tạp**: Multi-tenant, K8s, Redis, microservices — tất cả sau pilot.
7. **Defer full testing**: Chỉ critical path tests cho pilot, full coverage khi scale.
8. **Vanilla JS giữ nguyên**: Không framework rewrite, ưu điểm cho restaurant environment.
9. **Event sourcing giữ nguyên**: Code đã viết, cost đã trả, không remove.
10. **Pricing delay**: Không tối ưu pricing trước khi có khách hàng thực.
11. **Consolidate duplicate routers**: Deprecate legacy `/api/orders`, giữ domain `/api/tableorder`.

---

## ❌ Các điểm bất đồng (2/15)

### Bất đồng #1: AI/OpenAI features trong MVP

- **GPT nói**: "AI insight extraction giữ trong MVP — dù ở dạng fallback keyword-based, customer preference tracking phải là part of Day 1. Đây là differentiator cốt lõi, không phải nice-to-have." GPT coi data moat từ customer insights là chiến lược retention dài hạn, và `InsightExtractor._fallback_extract()` đã có sẵn không phụ thuộc OpenAI.

- **Gemini nói**: "AI/OpenAI features là DEFERRED — Không nằm trong MVP. Chat integration và customer insight extraction không cần cho pilot. Chi phí OpenAI API không justify khi chưa có data." Gemini coi đây là distraction khỏi core value (ordering flow).

- **Khoảng cách**: Thực tế khá hẹp. GPT đề xuất giữ **keyword-based fallback** (không cần OpenAI API, chi phí = 0). Gemini phản đối **OpenAI integration** (chi phí $5-20/tháng). Cả hai có thể đồng ý nếu phân biệt rõ: (a) keyword-based preference tracking = giữ, (b) OpenAI API call = defer.

- **Gợi ý compromise**: Giữ chat widget với **fallback keyword responses** trong MVP (code đã có, chi phí = 0). Tắt OpenAI API call. Customer preference tracking chạy ở dạng keyword-based. Khi pilot có real data → bật OpenAI để enhance.

### Bất đồng #2: POS app trong MVP

- **GPT nói**: "POS app có thể defer hoàn toàn — manual checkout bằng calculator + receipt printer là đủ cho pilot." GPT ưu tiên speed-to-pilot, coi checkout flow hiện tại là phức tạp không cần thiết khi backend POS API chưa connected.

- **Gemini nói**: "MVP là table-order + kitchen + POS... POS frontend cần kết nối real API. Backend POS API đã implement đầy đủ (`GET /pos/tables`, `POST /checkout`). Chỉ cần fix frontend mock data thay bằng real API calls." Gemini thấy POS backend đã sẵn sàng, chỉ cần wire frontend.

- **Khoảng cách**: Đáng kể. GPT muốn skip POS hoàn toàn (calculator thủ công), Gemini muốn POS là core app thứ 3. Khác biệt gốc rễ: GPT muốn launch sớm hơn (6-8 tuần), Gemini sẵn sàng thêm thời gian (8-12 tuần) để có POS thực.

- **Gợi ý compromise**: POS ở **mức basic** — kết nối real API để hiển thị bill tổng (subtotal + tax) và đánh dấu "đã thanh toán", nhưng KHÔNG cần payment gateway integration. Tức là: xem bill → thu tiền mặt/card thủ công → confirm trên POS → close table. Effort: ~1-2 sprints thêm so với GPT proposal, nhưng ít hơn full POS mà Gemini muốn.

---

## ⚠️ Các điểm gần đồng thuận (2/15)

### Gần đồng thuận #1: Free trial duration
- **GPT**: 6 tháng miễn phí
- **Gemini**: 3 tháng miễn phí
- **Gap**: Chỉ timeline, cả hai đồng ý miễn phí. Compromise: 3 tháng, tự động gia hạn nếu đang tích cực dùng.

### Gần đồng thuận #2: Timeline pilot-ready
- **GPT**: 6-8 tuần
- **Gemini**: 8-12 tuần (bao gồm POS)
- **Gap**: 2-4 tuần, phụ thuộc vào quyết định POS (bất đồng #2).

---

## 📈 Tỷ lệ đồng thuận: 11/15 = 73%

---

## 🎯 Hướng dẫn cho Round 2

### Câu hỏi cho GPT:
1. Bạn có thể chấp nhận giữ **keyword-based preference tracking** (không OpenAI) thay vì full AI integration cho MVP không? Điều kiện cụ thể?
2. Nếu POS basic (xem bill + confirm payment, không payment gateway) mất thêm 1-2 sprints, bạn có chấp nhận đưa vào MVP không? Vì Gemini chỉ ra backend POS API đã implement xong.
3. Free trial 3 tháng (thay vì 6) có OK không? Reasoning?

### Câu hỏi cho Gemini:
1. Nếu tách AI features thành (a) keyword-based fallback = giữ, (b) OpenAI API = defer, bạn có đồng ý giữ phần (a) trong MVP không? Chi phí = 0.
2. POS "basic" (hiển thị bill + confirm manual payment + close table, KHÔNG payment gateway) — effort estimate cụ thể bao nhiêu sprints?
3. Free trial 3 tháng với auto-extend option, hay hard cutoff?

### Đề xuất compromise cần cả hai phản hồi:
1. **AI compromise**: MVP bao gồm chat widget fallback mode + keyword preference tracking. OpenAI API disabled by default, enable khi có data + budget.
2. **POS compromise**: POS basic = view bill + manual payment confirm + close table. No payment gateway. Effort thêm ~1 sprint.
3. **Timeline compromise**: Target 8-10 tuần pilot-ready (giữa hai estimate).

### Data/evidence cần bổ sung:
- GPT: Có case study nào về restaurant pilot thất bại vì thiếu POS integration?
- Gemini: Effort estimate cụ thể cho "POS basic" (chỉ wire 3-4 API calls)?
