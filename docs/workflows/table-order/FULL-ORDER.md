# Table Order — Quy trình trải nghiệm khách hàng

> Mô tả chi tiết từng bước khách hàng thao tác trên máy tính bảng (iPad) đặt tại bàn ăn.
> Ứng dụng hoạt động theo vòng đời 4 pha: **WELCOME → ORDERING → BILL_REVIEW → CLEANING → WELCOME**

---

## Phase 1: WELCOME — Màn hình chào mừng

1. Nhân viên đặt máy tính bảng tại bàn ăn, màn hình hiển thị **Welcome Screen**:
   - Logo 🍖 và tên nhà hàng「焼肉ジナン」
   - Số bàn (ví dụ: **T5**) và số khách (ví dụ: **4名様**)
   - Gợi ý chuyển ngôn ngữ: `🌐 English available`
2. Khách hàng chạm nút **「タッチして注文を始める」** (Touch để bắt đầu đặt món).
3. Hệ thống tạo `session_id` mới, chuyển sang pha **ORDERING**.

---

## Phase 2: ORDERING — Duyệt menu & đặt món

### 2.1 Giao diện chính

Màn hình chia thành các vùng:

| Vùng | Mô tả |
|------|--------|
| **Header** | Logo, số bàn, số khách, các nút: 🔔 呼出 (gọi nhân viên), 💳 会計 (yêu cầu thanh toán), 📋 履歴 (lịch sử), 🛒 giỏ hàng |
| **Category Tabs** | Thanh danh mục cuộn ngang (肉, サイド, ドリンク, ...) |
| **Menu Grid** | Lưới hiển thị các món ăn (hình ảnh, tên, giá) |
| **Floating Cart Bar** | Thanh nổi ở dưới cùng: số lượng món, tổng tiền, nút「注文へ →」|

### 2.2 Chọn món ăn

4. Khách hàng chạm **tab danh mục** (ví dụ: 肉 → サイド → ドリンク) để duyệt menu.
5. Chạm vào **hình ảnh hoặc tên món** để mở **Item Detail Modal**:
   - Hình ảnh lớn, tên món, mô tả, giá
   - Bộ chọn số lượng: **−** / **+** (mặc định: 1)
   - Ô ghi chú tùy chọn (ví dụ: よく焼き、タレ多め)
   - Nút **「カートに追加」** (Thêm vào giỏ)
6. Chạm **「カートに追加」** → modal đóng, hiện thông báo **"〇〇をカートに追加しました"**, badge giỏ hàng cập nhật.
7. Khách hàng lặp lại bước 4-6 để chọn thêm món.

### 2.3 Xem & gửi đơn hàng

8. Chạm **🛒 badge** trên header hoặc **thanh nổi「注文へ →」** → mở **Cart Drawer** (trượt từ phải):
   - Danh sách các món đã chọn (tên, số lượng ×, giá, nút xóa)
   - Tổng tiền ở cuối
   - Nút **「注文を確定する」** (Xác nhận đặt món)
9. Khách hàng có thể:
   - Điều chỉnh số lượng (＋/−) hoặc xóa món khỏi giỏ
   - Đóng giỏ hàng để tiếp tục chọn thêm
10. Chạm **「注文を確定する」** → đơn hàng gửi đến bếp (API POST `/api/tableorder/`):
    - Giỏ hàng xóa sạch, thông báo **"注文を送信しました"**
    - Đơn hàng lưu vào **lịch sử** (`orderHistory`)
    - Máy tính bảng bếp (Kitchen Display) nhận đơn hàng qua WebSocket

### 2.4 Theo dõi đơn hàng

11. Chạm **📋 履歴** trên header → mở **History Drawer**:
    - Danh sách tất cả món đã đặt, nhóm theo thời gian gửi
    - Trạng thái mỗi món: ⏳ (đang chờ) hoặc ✓ (đã giao)
    - Tổng số món và tổng tiền
12. Khi bếp đánh dấu món đã xong → trạng thái cập nhật real-time qua WebSocket.

### 2.5 Gọi nhân viên

13. Chạm **🔔 呼出** → gửi yêu cầu hỗ trợ đến hệ thống (nhân viên nhận thông báo).

### 2.6 Đặt thêm món (lặp lại)

14. Khách hàng có thể đặt thêm nhiều lần (bước 4-10) trong suốt bữa ăn.
    - Mỗi lần đặt tạo một đơn hàng riêng, tất cả gom vào lịch sử.

---

## Phase 3: BILL_REVIEW — Xem hóa đơn & yêu cầu thanh toán

### 3.1 Chuyển sang BILL_REVIEW

15. Khi dùng bữa xong, khách hàng chạm **💳 会計** trên header.
    - Nếu đã có đơn hàng → chuyển sang màn hình **Bill Review**.
    - Nếu chưa đặt món nào → chỉ gửi thông báo gọi nhân viên.

### 3.2 Màn hình Bill Review

16. Màn hình hiển thị:
    - Tiêu đề **「📋 ご注文内容」** (Nội dung đơn hàng)
    - Danh sách tất cả món đã đặt trong session, nhóm theo thời gian
    - Tổng số món và **tổng tiền**
    - Hai nút hành động nằm ngang:
      - **「＋ 追加注文」** — quay lại menu để đặt thêm
      - **「💰 お会計をお願いする」** — yêu cầu thanh toán

### 3.3 Thêm món (tùy chọn)

17. Chạm **「＋ 追加注文」** → quay lại pha **ORDERING**, tiếp tục đặt món.
    - Sau khi đặt xong, chạm **💳 会計** lần nữa để quay lại Bill Review.

### 3.4 Yêu cầu thanh toán

18. Chạm **「💰 お会計をお願いする」**:
    - Gửi sự kiện `call-staff (bill)` đến backend → thông báo đến POS
    - Hai nút ẩn đi, hiển thị **"お会計を準備中です..."** (đang chuẩn bị hóa đơn) với hiệu ứng nhấp nháy
    - Nhân viên thu ngân nhận thông báo trên máy POS

---

## Phase 4: CLEANING — Kết thúc session

19. Sau khi POS xác nhận thanh toán xong → hệ thống tự động chuyển sang **Cleaning Screen**:
    - Hiển thị **「🙏 ありがとうございました」** (Cảm ơn quý khách)
    - Tóm tắt session: số lần đặt, tổng số món, tổng tiền
20. **Chỉ nhân viên** mới có thể reset bàn: nhấn giữ nút **「リセット」** trong **3 giây**.
    - Xóa toàn bộ dữ liệu session (giỏ hàng, lịch sử, session_id)
    - Quay về pha **WELCOME**, sẵn sàng cho khách mới.

---

## Tính năng bổ sung

| Tính năng | Mô tả |
|-----------|--------|
| **Đa ngôn ngữ** | Chạm nút `EN` trên header để chuyển English ↔ 日本語 |
| **Offline-capable** | Đơn hàng lưu localStorage, tự gửi lại khi có mạng |
| **Crash recovery** | Session phase lưu localStorage, tự phục hồi khi reload |
| **Inactivity timeout** | 30 phút không thao tác → tự động chuyển BILL_REVIEW |
| **Real-time sync** | WebSocket cập nhật trạng thái món (đã giao) từ bếp |
| **Thanh kết nối** | Hiển thị trạng thái online/offline ở dưới cùng |

---

## Sơ đồ luồng

```
┌─────────┐    Touch      ┌──────────┐    💳 会計     ┌─────────────┐
│ WELCOME │──────────────▶│ ORDERING │──────────────▶│ BILL_REVIEW │
│  (chờ)  │               │ (đặt món)│◀─── 追加注文 ─┤ (xem bill)  │
└─────────┘               └──────────┘               └──────┬──────┘
     ▲                                                      │
     │               ┌──────────┐          💰 お会計        │
     └─── 3s reset ──│ CLEANING │◀────── POS confirm ──────┘
                      │ (cảm ơn) │
                      └──────────┘
```
