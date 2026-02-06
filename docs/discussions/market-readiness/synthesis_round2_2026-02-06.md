# 🎼 Synthesis — Round 2 | 2026-02-06

## Chủ đề: Tính khả thi & Chiến lược Go-to-Market cho Yakiniku.io

---

## 📊 Bảng đồng thuận (cập nhật)

| # | Điểm thảo luận | GPT (Visionary) | Gemini (Pragmatist) | Đồng thuận? |
|---|----------------|-----------------|---------------------|-------------|
| 1 | AI/OpenAI trong MVP | ✅ Giữ keyword fallback, tắt OpenAI API | ✅ Đồng ý giữ keyword fallback, DEFER OpenAI | ✅ **Đồng thuận** |
| 2 | POS trong MVP | ✅ Đưa POS Basic vào (view bill + confirm + close) | ✅ POS Basic, 0.5 sprint, backend đã xong | ✅ **Đồng thuận** |
| 3 | Free trial duration | ✅ 3 tháng + review meeting tháng 3 | ✅ 3 tháng + auto-extend nếu active | ✅ **Đồng thuận** |
| 4 | Timeline pilot-ready | ✅ 8-10 tuần | ✅ 8-10 tuần | ✅ **Đồng thuận** |

*Cộng 11 điểm đã đồng thuận từ Round 1.*

---

## ✅ Tất cả 15/15 điểm đã đồng thuận!

### Điểm giải quyết trong Round 2:

**1. AI/OpenAI → Keyword fallback giữ, OpenAI defer**
- Cả hai chấp nhận tách (a) keyword-based preference tracking (cost = 0, code đã có) vs (b) OpenAI API calls (cost > 0, chưa cần)
- Chat widget chạy fallback-only mode, `OPENAI_API_KEY` để trống
- GPT nhượng bộ: không còn yêu cầu "Day 1 differentiator", chỉ yêu cầu giữ code đã viết
- Gemini thừa nhận sai "all-or-nothing thinking" khi gộp cả hai scope

**2. POS → POS Basic vào MVP**
- GPT thay đổi lập trường lớn nhất: từ "defer hoàn toàn" → "đưa POS Basic vào"
- Gemini thuyết phục bằng evidence: backend 272 LOC đã sẵn sàng, frontend chỉ cần wire 4 fetch calls
- Effort ước tính: 0.5 sprint (2-3 ngày) — backend 0, frontend 5-7 giờ code + 1 ngày test
- Scope: view tables → view bill → confirm payment (manual) → close table. Không discount, không receipt printer, không payment gateway

**3. Free trial → 3 tháng + review checkpoint**
- GPT nhượng bộ từ 6 → 3 tháng
- Gemini thêm flexibility: auto-extend nếu active (≥50 orders/tuần)
- Cả hai đồng ý: review meeting tháng 3, không hard cutoff nhưng có checkpoint

**4. Timeline → 8-10 tuần**
- GPT điều chỉnh từ 6-8 → 8-10 (do thêm POS Basic)
- Gemini thu hẹp từ 8-12 → 8-10 (do POS scope giảm)
- Hai range overlap hoàn hảo tại 8-10 tuần

---

## 📈 Tỷ lệ đồng thuận: 15/15 = 100% ✅

---

**→ Chuyển sang Phase cuối: Tổng kết Final Consensus**
