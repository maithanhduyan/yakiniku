# Kitchen Display System — Quy trình trải nghiệm ứng dụng bếp

**Dành cho nhân viên chế biến (Chef / Cook) thao tác trên màn hình Kitchen Display (KDS)**

---

## Tổng quan ứng dụng

Kitchen Display System (KDS) là ứng dụng hiển thị trên màn hình lớn trong bếp. Nhân viên chế biến nhìn vào màn hình để biết món nào cần chuẩn bị, thứ tự ưu tiên, và đánh dấu hoàn thành khi món đã sẵn sàng phục vụ.

- **URL**: `http://localhost:5500/kitchen/` (dev) hoặc `http://localhost:8082/` (http.server)
- **Thiết bị**: Màn hình cảm ứng trong bếp hoặc tablet
- **Ngôn ngữ UI**: Tiếng Nhật (mặc định), có thể chuyển sang Tiếng Anh

---

## Bố cục màn hình

```
┌──────────────────────────────────────────────────────────┐
│ 🍳 キッチン   [●接続中]     合計:5  3分超:2  5分超:1  00:00 │  ← Header
├──────────────────────────────────────────────────────────┤
│ 📋すべて(5) │ 🥩肉(2) │ 🍚他(2) │ 🍺飲物(1)             │  ← Station Tabs
├──────────────────────────────────────────────────────────┤
│                          │  🥩 肉 (2)                    │
│   📋 すべて (5)          │  ┌─────────────────┐          │
│   ┌─────────────────┐    │  │ 特選カルビ ×2 T3 │          │
│   │ 特選カルビ ×2 T3 │    │  └─────────────────┘          │
│   │ 上ハラミ   ×1 T3 │    ├──────────────────────────────┤
│   │ ライス    ×2 T3 │    │  🍚 他 (2)                    │
│   │ 牛タン塩   ×2 T7 │    │  ┌─────────────────┐          │
│   │ 生ビール   ×3 T7 │    │  │ ライス     ×2 T3 │          │
│   └─────────────────┘    │  └─────────────────┘          │
│                          ├──────────────────────────────┤
│     Main Panel           │  🍺 飲物 (1)                  │
│                          │  ┌─────────────────┐          │
│                          │  │ 生ビール   ×3 T7 │          │
│                          │  └─────────────────┘          │
│                          │     Mini Panels               │
├──────────────────────────────────────────────────────────┤
│ ⏱ 警告:3分 / 緊急:5分          [EN][📜][🔔][⛶]          │  ← Footer
└──────────────────────────────────────────────────────────┘
```

### Thành phần UI chính

| Thành phần | Mô tả |
|-----------|-------|
| **Header** | Logo, trạng thái kết nối (●接続中/●オフライン), thống kê (合計/3分超/5分超), đồng hồ |
| **Station Tabs** | 4 tab lọc: すべて (tất cả), 🥩肉 (thịt), 🍚他 (khác), 🍺飲物 (đồ uống) |
| **Main Panel** | Hiển thị đầy đủ danh sách món của station đang chọn |
| **Mini Panels** | 3 panel thu nhỏ hiển thị tóm tắt các station còn lại, nhấn để chuyển |
| **Footer** | Ngưỡng thời gian, nút chuyển ngôn ngữ (EN), lịch sử (📜), âm thanh (🔔), toàn màn hình (⛶) |

---

## Mỗi dòng món ăn (Item Row)

```
┌──────────────────────────────────────────────────────────┐
│  特選カルビ          ×2       T3       4分      ✕    ✓   │
│  ※よく焼き                                              │
└──────────────────────────────────────────────────────────┘
  ↑ Tên món + ghi chú   ↑Qty   ↑Bàn   ↑Timer  ↑Hủy ↑Xong
```

### Hệ thống cảnh báo thời gian

| Thời gian chờ | Trạng thái | Màu hiển thị |
|---------------|-----------|-------------|
| < 3 phút | Bình thường | Không đổi (xanh dương nhạt) |
| 3–5 phút | ⚠️ Cảnh báo (`status-warning`) | Vàng |
| > 5 phút | 🚨 Khẩn cấp (`status-urgent`) | Đỏ |

---

## Quy trình thao tác chi tiết

### Phase 0: Khởi động — Loading & Kết nối

```
Mở ứng dụng → Loading Overlay hiển thị:
  🍳
  注文データを読み込み中...
  ⏳ API接続
  ⏳ リアルタイム

→ Kết nối API thành công: ✓ API接続
→ Kết nối WebSocket thành công: ✓ リアルタイム
→ Loading biến mất sau 800ms
→ Nếu API thất bại → chuyển sang Demo Mode (hiện banner vàng "⚠️ デモモード")
```

### Phase 1: Giám sát đơn hàng — Monitoring

Sau khi load xong, nhân viên bếp nhìn vào màn hình:

1. **Kiểm tra tổng quan**: Nhìn header stats (合計, 3分超, 5分超) để biết có bao nhiêu món đang chờ
2. **Kiểm tra ưu tiên**: Món nào hiển thị **màu đỏ** (>5 phút) → cần ưu tiên làm ngay
3. **Lọc theo station**: Nhấn tab station để xem chỉ nhóm món thuộc chuyên môn của mình
   - 🥩 **肉 (Thịt)**: カルビ, ハラミ, タン, ロース, ホルモン, 牛, 豚, 鶏...
   - 🍚 **他 (Khác)**: ライス, ナムル, キムチ, サラダ, ビビンバ, 麺...
   - 🍺 **飲物 (Đồ uống)**: ビール, ハイボール, サワー, ジュース...

### Phase 2: Nhận đơn hàng mới — New Order Notification

Khi khách hàng đặt món từ table-order app:

```
WebSocket event "new_order" →
  🔔 Âm thanh thông báo (two-tone bell chime)
  📋 Toast notification: "テーブル T3 から新しい注文"
  → Danh sách món tự động cập nhật
  → Thống kê header tự động tăng
```

### Phase 3: Chế biến & hoàn thành món — Mark as Served

Khi món ăn đã chế biến xong:

1. **Tìm món**: Nhìn dòng món cần đánh dấu (tìm theo tên món + số bàn)
2. **Nhấn nút ✓ (Done)**: Nhấn vào nút ✓ ở bên phải dòng món
3. **Xác nhận modal**: Modal xác nhận hiện ra với thông tin:
   ```
   ┌───────────────────────┐
   │  ✅ 提供確認           │
   │                       │
   │  特選カルビ            │
   │  数量: ×2             │
   │  テーブル: T3          │
   │  待ち: 4分             │
   │                       │
   │  この料理を提供済みに   │
   │  しますか？            │
   │                       │
   │  [キャンセル] [提供済み] │
   └───────────────────────┘
   ```
4. **Nhấn "提供済み" (Đã phục vụ)**: Xác nhận hoàn thành
5. **Kết quả**:
   - Dòng món có animation biến mất (slide out 300ms)
   - ✅ Âm thanh xác nhận (gentle positive tone)
   - API call: `PATCH /api/kitchen/items/{id}/done`
   - Event log: `kitchen.item.served` ghi vào hệ thống event sourcing
   - WebSocket broadcast: Các tablet KDS khác tự động xóa món này

### Phase 4: Hủy món — Cancel Item

Khi cần hủy món (hết nguyên liệu, khách đổi ý...):

1. **Nhấn nút ✕ (Cancel)**: Nhấn vào nút ✕ ở bên trái nút ✓
2. **Xác nhận modal**: Modal hủy hiện ra:
   ```
   ┌───────────────────────┐
   │  ❌ キャンセル確認      │
   │                       │
   │  特選カルビ            │
   │  数量: ×2             │
   │  テーブル: T3          │
   │                       │
   │  理由（任意）:          │
   │  [品切れ、お客様都合  ] │
   │                       │
   │  この料理をキャンセル   │
   │  しますか？            │
   │                       │
   │  [戻る] [キャンセルする] │
   └───────────────────────┘
   ```
3. **Nhập lý do (tùy chọn)**: Gõ lý do hủy vào ô input
4. **Nhấn "キャンセルする"**: Xác nhận hủy
5. **Kết quả**:
   - Dòng món có animation biến mất
   - ❌ Âm thanh hủy (subtle low tone)
   - Toast notification hiển thị
   - Event log: `kitchen.item.cancelled` với lý do

### Phase 5: Đồng bộ thiết bị chéo — Cross-Device Sync

Khi có nhiều tablet KDS trong bếp:

- Khi tablet A đánh dấu món hoàn thành → tablet B, C tự động xóa món đó
- WebSocket events: `kitchen.item.served`, `kitchen.item.cancelled`
- Notification trên tablet khác: "✅ 特選カルビ — 他のデバイスで提供済み"

### Phase 6: Xem lịch sử — History Panel

1. **Nhấn nút 📜 (History)** ở footer
2. **History panel mở ra** overlay toàn màn hình:
   - **Thống kê tóm tắt**: Số món đã phục vụ, số món đã hủy, thời gian chờ trung bình
   - **Bộ lọc**: Lọc theo station (すべて/肉/他/飲物) và loại event (全イベント/提供済み/キャンセル)
   - **Danh sách sự kiện**: Mỗi dòng hiển thị icon (✅/❌), tên món, giờ, số lượng, bàn, thời gian chờ
3. **Đóng**: Nhấn nút ✕ hoặc nhấn vào vùng trống bên ngoài panel

---

## Tính năng phụ trợ

| Tính năng | Thao tác | Mô tả |
|----------|---------|-------|
| **Chuyển ngôn ngữ** | Nhấn nút `EN` ở footer | Chuyển đổi Nhật ↔ Anh, lưu vào localStorage |
| **Tắt/Bật âm thanh** | Nhấn nút 🔔 ở footer | Toggle âm thanh thông báo |
| **Toàn màn hình** | Nhấn nút ⛶ ở footer | Vào/thoát chế độ fullscreen |
| **Chuyển station** | Nhấn mini panel | Mini panel thu nhỏ trở thành main panel |

---

## Quy tắc ưu tiên chế biến

1. **Ưu tiên theo thời gian**: Món đặt trước được hiển thị trên cùng (sắp xếp oldest-first)
2. **Ưu tiên khẩn cấp**: Món hiển thị **đỏ** (>5 phút) → chế biến ngay
3. **Ưu tiên cảnh báo**: Món hiển thị **vàng** (>3 phút) → chuẩn bị ưu tiên
4. **Đúng bàn**: Đảm bảo giao đúng bàn khách ghi trên mỗi dòng món
5. **Tối đa 5 phút**: Mục tiêu — không có món nào chờ quá 5 phút

---

## Luồng dữ liệu kỹ thuật

```
Khách đặt món (table-order app)
  → POST /api/tableorder/
  → WebSocket broadcast "new_order"
  → KDS nhận event → loadOrders() → hiển thị món mới

Nhân viên đánh dấu hoàn thành
  → PATCH /api/kitchen/items/{id}/done
  → POST /api/kitchen/events/ (event sourcing log)
  → WebSocket broadcast "kitchen.item.served"
  → Các KDS khác → removeItemBySync()

Polling fallback (30s)
  → GET /api/kitchen/orders?branch_code=hirama
  → Cập nhật toàn bộ danh sách
```

---

## Xử lý sự cố

| Tình huống | Biểu hiện | Hành động |
|-----------|----------|---------|
| Mất kết nối API | ●オフライン đỏ, chuyển sang Demo Mode | Chờ kết nối lại tự động (30s polling) |
| Mất WebSocket | Trạng thái chuyển offline | Tự động reconnect (tối đa 20 lần, backoff tăng dần) |
| Không có đơn hàng | Hiển thị "☕ 注文を待っています" | Chờ đơn hàng mới |
| Demo Mode | Banner vàng "⚠️ デモモード" | Dữ liệu mẫu, không ảnh hưởng hệ thống thật |
