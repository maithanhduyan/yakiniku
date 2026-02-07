# Dashboard Admin — Quy trình quản lý thiết bị & đăng nhập QR Code

**Dành cho quản lý cửa hàng (Manager / Admin) thao tác trên Dashboard để cấp phép thiết bị**

---

## Tổng quan

Dashboard là trung tâm quản lý tất cả thiết bị trong nhà hàng: table-order (iPad đặt món), kitchen (KDS), POS (thu ngân), check-in (kiosk).

Admin sử dụng Dashboard để:
1. **Đăng ký thiết bị mới** — chọn loại, gán bàn, đặt tên
2. **Tạo QR Code** — mã xác thực duy nhất cho mỗi thiết bị
3. **Giám sát trạng thái** — Active / Pending / Inactive / Connected
4. **Quản lý session** — Logout / Regenerate Token / Xóa thiết bị

- **URL**: `http://localhost:5500/dashboard/` → trang **Devices** (`#devices`)
- **Thiết bị**: Desktop / Laptop của quản lý
- **Ngôn ngữ UI**: Tiếng Nhật / Tiếng Anh (toggle JP/EN ở sidebar)

---

## Bố cục màn hình Devices

```
┌─────────┬────────────────────────────────────────────────┐
│ Sidebar │  Device Management              [＋ Register]  │
│         ├────────────────────────────────────────────────┤
│ 📊 Home │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
│ 📅 Book │  │ 🟢 1 │ │ 🟡 0 │ │ 🔴 0 │ │ 📱 1 │         │
│ 🪑 Tabl │  │Active│ │Pend. │ │Inact.│ │Total │         │
│ 👥 Cust │  └──────┘ └──────┘ └──────┘ └──────┘         │
│ 📈 Anal │                                               │
│ 📱 Devi │  🍽️ Table Order                    2 units    │
│         │  ┌──────────────────────────────────────────┐  │
│         │  │ iPad-A1   🔗Connected  │ Active │📲✏️🗑️│  │
│         │  │ Table A1   Last: now   │        │🔓     │  │
│         │  ├──────────────────────────────────────────┤  │
│         │  │ iPad-A2              │Pending│📲✏️🗑️│  │
│         │  │ Table A2   Last: -   │       │       │  │
│         │  └──────────────────────────────────────────┘  │
│         │                                               │
│ [JP/EN] │  👨‍🍳 Kitchen (KDS)                 0 units    │
│ Branch  │  💰 POS                           0 units    │
│ ●接続済み│  📋 Check-in                      0 units    │
└─────────┴────────────────────────────────────────────────┘
```

### Thành phần UI chính

| Thành phần | Mô tả |
|-----------|-------|
| **Stats Cards** | 4 card thống kê: Active (🟢), Pending Auth (🟡), Inactive (🔴), Total (📱) |
| **Device Groups** | Nhóm theo loại: Table Order, Kitchen, POS, Check-in — hiển thị số lượng |
| **Device Row** | Tên thiết bị, badge trạng thái, thông tin bàn, last seen, action buttons |
| **Action Buttons** | 🔓 Logout, 📲 QR Code, ✏️ Edit, 🗑️ Delete |
| **🔗 Connected Badge** | Hiển thị khi thiết bị đã xác thực và có session đang hoạt động |

### Trạng thái thiết bị

| Status | Màu | Ý nghĩa |
|--------|-----|---------|
| **Pending Auth** | 🟡 Vàng | Mới tạo, chưa được scan QR / nhập code |
| **Active** | 🟢 Xanh | Đã xác thực, đang hoạt động |
| **Inactive** | 🔴 Đỏ | Bị vô hiệu hóa bởi admin |

---

## Quy trình 1: Đăng ký thiết bị mới

### Bước 1 — Mở trang Devices

```
1. Truy cập Dashboard: http://localhost:5500/dashboard/
2. Click sidebar menu "📱 Devices"
3. Chọn Branch phù hợp ở dropdown sidebar (ví dụ: 平間本店 = hirama)
4. Xác nhận trang "Device Management" hiển thị
```

### Bước 2 — Mở form đăng ký

```
1. Click nút "＋ Register Device" (góc trên phải)
2. Modal "Register New Device" xuất hiện
```

### Bước 3 — Điền thông tin thiết bị

```
1. Device Type *: Chọn loại thiết bị
   - 🍽️ Table Order  → yêu cầu chọn Table
   - 👨‍🍳 Kitchen (KDS)
   - 💰 POS
   - 📋 Check-in

2. Table * (chỉ hiện khi chọn Table Order):
   Chọn bàn gán cho thiết bị, ví dụ:
   - Table A1 (floor)
   - Table B1 (counter)
   - Table C1 (private)

3. Device Name *: Đặt tên dễ nhận biết
   Quy ước: [Loại]-[Bàn/Vị trí]-[Branch]
   Ví dụ: "iPad-A1-Hirama", "KDS-Kitchen1"

4. Notes: Ghi chú tùy chọn (SN thiết bị, vị trí lắp...)
```

### Bước 4 — Xác nhận đăng ký

```
1. Click "Register"
2. Hệ thống tạo thiết bị với:
   - Token xác thực (64 ký tự hex, unique)
   - Trạng thái: Pending Auth
3. Toast thông báo: "✓ Registered — [tên] has been registered"
4. Modal QR Code tự động hiển thị
```

### Bước 5 — Hiển thị QR Code

```
Modal "📲 QR Code — [Tên thiết bị]" hiển thị:

┌─────────────────────────────────────┐
│  📲 QR Code — iPad-A1-Hirama    ✕  │
├─────────────────────────────────────┤
│         ┌─────────────┐             │
│         │  █▀▀▀█ ▀█▀  │             │
│         │  █ ▄▄ █     │  ← QR Code  │
│         │  ▀▀▀▀▀▀▀▀▀  │     chứa    │
│         └─────────────┘     token    │
│                                     │
│  Device Name    iPad-A1-Hirama      │
│  Type           🍽️ Table Order       │
│  Table          Table A1            │
│  Status         Pending Auth        │
│  Created        Feb 7, 04:07 PM     │
│                                     │
│  [Close]    [🔄 Regenerate Token]   │
└─────────────────────────────────────┘

- QR Code encode token string (64 hex chars)
- Có thể Regenerate Token nếu cần tạo mã mới
- Close để đóng modal
```

---

## Quy trình 2: Đăng nhập thiết bị Table-Order bằng QR Code

### Điều kiện tiên quyết

- Thiết bị (iPad) đã cài / mở ứng dụng table-order
- Thiết bị **chưa được xác thực** (không có session trong localStorage)
- QR Code đã được tạo từ Dashboard (Quy trình 1)

### Bước 1 — Mở ứng dụng Table-Order

```
1. Mở trình duyệt trên iPad
2. Truy cập: http://[server]:5500/table-order/
3. Ứng dụng hiển thị màn hình "端末認証" (Device Auth)
```

### Bước 2 — Màn hình xác thực

```
┌──────────────────────────────────┐
│              🍖                   │
│          端末認証                  │
│  QRコードをスキャンするか、        │
│  認証コードを入力してください       │
│                                  │
│  ┌──────────────────────────┐    │
│  │  📷 QRコードをスキャン    │    │  ← Mở camera scan
│  └──────────────────────────┘    │
│                                  │
│          ── または ──             │
│                                  │
│  認証コード                       │
│  ┌──────────────────────────┐    │
│  │  コードを入力              │    │  ← Nhập token thủ công
│  └──────────────────────────┘    │
│  ┌──────────────────────────┐    │
│  │         認証              │    │  ← Xác thực
│  └──────────────────────────┘    │
│                                  │
│  ※ 管理者がダッシュボードで       │
│  発行したQRコードが必要です        │
└──────────────────────────────────┘

Hai phương thức xác thực:
  A. Scan QR Code bằng camera (khuyến nghị)
  B. Nhập token code thủ công
```

### Phương thức A — Scan QR Code bằng Camera

```
1. Nhấn nút "📷 QRコードをスキャン"
2. Camera mở ra (yêu cầu quyền camera lần đầu)
3. Hướng camera vào QR Code trên Dashboard

   ┌───────────────────────────┐
   │  QRコードをスキャン     ✕  │
   │  ┌─────────────────────┐  │
   │  │                     │  │
   │  │   ┌─────────┐       │  │
   │  │   │ QR Frame │       │  │  ← Khung vàng nhấp nháy
   │  │   └─────────┘       │  │
   │  │   (camera preview)  │  │
   │  └─────────────────────┘  │
   │  カメラをQRコードに         │
   │  向けてください              │
   └───────────────────────────┘

4. Khi QR Code nằm trong khung vàng → tự động decode
5. Token được extract → gửi API xác thực
6. Nếu thành công → camera đóng, auth screen ẩn
```

**QR Scanner hỗ trợ 2 engine:**
- **BarcodeDetector** (native): iPad iOS 15.4+, Chrome 83+ — ưu tiên
- **jsQR** (fallback): Mọi browser có camera — canvas-based decode

### Phương thức B — Nhập Code thủ công

```
1. Copy token từ Dashboard (hoặc đọc từ phiếu in)
2. Paste/nhập vào ô "コードを入力"
3. Nhấn "認証" hoặc Enter
4. Hệ thống gửi token + fingerprint lên server
5. Nếu hợp lệ → xác thực thành công
```

### Bước 3 — Xác thực thành công

```
Khi xác thực thành công:
1. Auth screen tự ẩn
2. Welcome screen hiển thị với thông tin từ device config:
   - Tên nhà hàng: 焼肉ジナン
   - Số bàn: A1 (từ device.table_number)
   - Số khách: 4名様 (từ table.capacity)
3. WebSocket kết nối → 🟢 オンライン接続中
4. Session lưu vào localStorage (thời hạn 1 năm)

Trên Dashboard:
- Trạng thái thiết bị: Pending Auth → Active
- Badge: 🔗 Connected hiển thị
- Last seen: "just now"
- Nút 🔓 Logout xuất hiện
```

### Xử lý lỗi

| Lỗi | Nguyên nhân | Cách xử lý |
|-----|------------|------------|
| `このブラウザはQRスキャンに対応していません` | Browser không hỗ trợ BarcodeDetector lẫn jsQR | Dùng phương thức B (nhập code) |
| `カメラへのアクセスが拒否されました` | User từ chối quyền camera | Cho phép camera trong Settings |
| `Server error: 404` | Token không tồn tại hoặc đã bị xóa | Tạo QR Code mới từ Dashboard |
| `Server error: 403` | Token đã được bind với thiết bị khác | Logout thiết bị cũ trên Dashboard rồi thử lại |
| `Session expired` | Session hết hạn (>1 năm) | Scan QR Code lại để tạo session mới |

---

## Quy trình 3: Quản lý thiết bị đã đăng ký

### Xem QR Code lại

```
1. Tìm thiết bị trong danh sách
2. Click nút 📲 (Show QR)
3. Modal QR Code hiển thị với token hiện tại
```

### Logout thiết bị

```
1. Click nút 🔓 (Logout) trên device row
2. Modal xác nhận: "Logout [tên]? The device will need to re-authenticate."
3. Click "確認" (Confirm)
4. Hệ thống:
   - Xóa session_token và device_fingerprint trên server
   - Trạng thái: Active → Pending Auth
   - Badge 🔗 Connected biến mất
5. Thiết bị table-order khi reload → hiện lại auth screen
```

### Regenerate Token

```
1. Mở QR Code modal (nút 📲)
2. Click "🔄 Regenerate Token"
3. Token cũ bị vô hiệu, token mới được tạo
4. QR Code cập nhật hiển thị token mới
5. Thiết bị đang dùng token cũ sẽ bị invalid khi validate
```

### Xóa thiết bị

```
1. Click nút 🗑️ (Delete) trên device row
2. Modal xác nhận: "Delete [tên]? This action cannot be undone."
3. Click "確認" (Confirm)
4. Thiết bị bị xóa hoàn toàn khỏi hệ thống
5. Toast: "✓ Deleted — [tên] has been deleted"
```

---

## Quy trình 4: Session & Bảo mật

### Cơ chế bảo mật

```
1. Token (device_token):
   - 64 ký tự hex, tạo bằng secrets.token_hex(32)
   - Dùng 1 lần để xác thực → sinh session_token
   - Có thể regenerate từ Dashboard

2. Session Token:
   - 64 ký tự hex, tạo khi xác thực thành công
   - Thời hạn: 365 ngày
   - Lưu trong localStorage + DB (hashed)

3. Device Fingerprint:
   - Hash DJB2 + base64 từ: UserAgent, language, screen size, timezone...
   - Bind 1-1 với session: 1 QR Code chỉ dùng trên 1 thiết bị
   - Nếu fingerprint khác → từ chối xác thực (403)

4. Validate Flow (mỗi lần reload app):
   - Client gửi session_token + fingerprint → Server kiểm tra
   - Hợp lệ → skip auth screen, vào Welcome trực tiếp
   - Không hợp lệ → hiện auth screen, yêu cầu scan lại
   - Offline → trust saved session (fallback)
```

### Lifecycle

```
   Dashboard                    Table-Order iPad
   ─────────                    ────────────────
   [＋ Register Device]
        │
        ▼
   Device Created ──────────── QR Code Generated
   (Pending Auth)                    │
        │                            ▼
        │                   [📷 Scan QR / Input Code]
        │                            │
        │                    POST /api/devices/auth
        │                    {token, fingerprint}
        │                            │
        ▼                            ▼
   Status → Active ◄──────── Session Created (1 year)
   🔗 Connected                  │
        │                        ▼
        │                   Welcome Screen
        │                   Table A1 / 4名様
        │                   🟢 オンライン
        │                        │
        │                  (365 days later...)
        │                        │
        │                   Session Expired
        │                        │
        ▼                        ▼
   [🔓 Logout] ────────────► Auth Screen
   Status → Pending              (scan lại)
```

---

## API Reference

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/devices/` | GET | Danh sách thiết bị (query: `branch_code`) |
| `/api/devices/` | POST | Đăng ký thiết bị mới |
| `/api/devices/{id}` | PUT | Cập nhật thiết bị |
| `/api/devices/{id}` | DELETE | Xóa thiết bị |
| `/api/devices/{id}/regenerate-token` | POST | Tạo token mới |
| `/api/devices/auth` | POST | Xác thực bằng token + fingerprint |
| `/api/devices/session/validate` | POST | Validate session đang lưu |
| `/api/devices/{id}/logout` | POST | Logout thiết bị (xóa session) |

---

## Checklist triển khai

- [ ] Tạo device trên Dashboard cho mỗi iPad table-order
- [ ] Gán đúng branch + table cho mỗi device
- [ ] In QR Code hoặc hiển thị trên màn hình để scan
- [ ] Scan QR trên từng iPad để xác thực
- [ ] Xác nhận Dashboard hiện 🟢 Active + 🔗 Connected cho tất cả thiết bị
- [ ] Test reload iPad → session vẫn còn (không hiện auth screen)
- [ ] Test logout từ Dashboard → iPad hiện auth screen khi reload
