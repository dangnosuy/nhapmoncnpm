# BÁO CÁO ĐỒ ÁN: SMART SAVINGS - HỆ THỐNG QUẢN LÝ SỔ TIẾT KIỆM

**Môn học:** Nhập môn Công nghệ Phần mềm  
**Đề tài:** Hệ thống quản lý sổ tiết kiệm ngân hàng  
**Nhóm:** Nhóm 13  
**Ngày cập nhật:** 31/05/2026

---

## 1. Giới thiệu đề tài

Smart Savings là hệ thống quản lý gửi tiết kiệm ngân hàng theo mô hình phân quyền 3 vai trò: khách hàng, nhân viên ngân hàng và quản trị viên. Hệ thống mô phỏng quy trình nghiệp vụ gửi tiết kiệm tại ngân hàng, kết hợp quy trình số hóa trong đó khách hàng tạo yêu cầu giao dịch online và nhân viên duyệt trước khi dữ liệu tài chính được cập nhật.

Mục tiêu chính của hệ thống:

- Quản lý tài khoản khách hàng, nhân viên và quản trị viên.
- Quản lý sản phẩm tiết kiệm, kỳ hạn, lãi suất và tham số nghiệp vụ.
- Cho phép khách hàng mở sổ, gửi thêm, rút tiền, tất toán và chuyển khoản.
- Áp dụng mô hình Maker-Checker: khách hàng tạo yêu cầu, nhân viên kiểm tra và duyệt.
- Cung cấp báo cáo BM5 và thống kê xu hướng cho nhân viên/quản trị viên.
- Đảm bảo phân quyền dữ liệu: chỉ khách hàng được xem số dư ví cá nhân; Staff/Admin không xem số dư ví và không xem số dư từng sổ của khách hàng trong các màn tra cứu.

---

## 2. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3, Flask, Flask-CORS |
| Database | MySQL, `mysql-connector-python` |
| Authentication | JWT (`PyJWT`), password hash `werkzeug.security` |
| Frontend Admin | React, Vite, React Router, Axios |
| Frontend Client | HTML/CSS/JavaScript thuần, SVG chart |
| Frontend Staff | HTML/CSS/JavaScript thuần, Chart.js qua CDN cho thống kê xu hướng |
| Realtime | Server-Sent Events (SSE) |
| Test | Python integration test, Playwright E2E |

---

## 3. Kiến trúc hệ thống

### 3.1 Tổng quan

```text
Người dùng
  |-- Admin SPA  (React + Vite)
  |-- Client SPA (HTML/CSS/JS)
  |-- Staff SPA  (HTML/CSS/JS)
        |
        | REST API + SSE
        v
Flask Backend
  |-- common: auth, db, requireRole, events, savings_rules
  |-- admin: quản lý người dùng, sản phẩm, cấu hình
  |-- client: hồ sơ, sổ tiết kiệm, chuyển khoản, request giao dịch
  |-- staff: duyệt giao dịch, tra cứu, báo cáo, analytics
        |
        v
MySQL Database: modern_savings_db
```

### 3.2 Cấu trúc thư mục chính

```text
nmcnpm/
├── backend/
│   ├── app.py
│   ├── common/
│   │   ├── auth.py
│   │   ├── db.py
│   │   ├── events.py
│   │   ├── requireRole.py
│   │   └── savings_rules.py
│   ├── admin/admin.py
│   ├── client/client.py
│   └── staff/staff.py
├── frontend/
│   ├── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/axios.js
│   │   ├── layouts/AdminLayout.jsx
│   │   └── pages/admin/
│   ├── client/index.html
│   ├── staff/index.html
│   └── tests/role-flow.spec.js
├── smart_savings.sql
├── seed_mock_data.py
├── seed_mock_data.sql
├── test_flow.py
├── requirements.txt
└── report.md
```

---

## 4. Cơ sở dữ liệu

### 4.1 Database

Tên database: `modern_savings_db`

File schema: `smart_savings.sql`

### 4.2 Các bảng chính

#### `users`

Lưu thông tin tài khoản đăng nhập và phân quyền.

| Cột | Ý nghĩa |
|---|---|
| `user_id` | Khóa chính |
| `email` | Email đăng nhập, duy nhất |
| `password_hash` | Mật khẩu đã hash |
| `full_name` | Họ tên |
| `identity_card` | CMND/CCCD, duy nhất |
| `account_number` | Số tài khoản 10 chữ số |
| `address` | Địa chỉ |
| `role` | `CUSTOMER`, `STAFF`, `ADMIN` |
| `wallet_balance` | Số dư ví, chỉ Client được xem |
| `status` | `ACTIVE` hoặc `LOCKED` |
| `created_at` | Thời điểm tạo |

#### `savings_products`

Lưu danh sách sản phẩm tiết kiệm.

| Cột | Ý nghĩa |
|---|---|
| `product_id` | Khóa chính |
| `name` | Tên sản phẩm |
| `term_months` | Kỳ hạn theo tháng, `0` là không kỳ hạn |
| `interest_rate` | Lãi suất năm (%) |
| `min_days_hold` | Số ngày giữ tối thiểu |
| `is_active` | Sản phẩm còn hoạt động hay không |
| `description` | Mô tả |

Hệ thống hiện chỉ dùng 3 gói tiết kiệm chính:

| Mã gói | Tên gói | Kỳ hạn | Lãi suất năm | Giữ tối thiểu |
|---:|---|---:|---:|---:|
| 10 | Không kỳ hạn | 0 tháng | 0.50% | 15 ngày |
| 11 | 3 tháng kỳ hạn | 3 tháng | 4.50% | 0 ngày |
| 12 | 6 tháng kỳ hạn | 6 tháng | 5.20% | 0 ngày |

#### `savings_accounts`

Lưu sổ tiết kiệm của khách hàng.

| Cột | Ý nghĩa |
|---|---|
| `account_id` | Mã sổ |
| `user_id` | Chủ sở hữu |
| `product_id` | Loại sản phẩm |
| `principal_balance` | Số tiền gốc |
| `opened_at` | Ngày mở hoặc ngày tái tục gần nhất |
| `status` | `ACTIVE` hoặc `CLOSED` |

#### `transactions`

Lưu lịch sử giao dịch và hàng đợi duyệt.

| Cột | Ý nghĩa |
|---|---|
| `transaction_id` | Mã giao dịch |
| `user_id` | Người tạo giao dịch |
| `account_id` | Sổ liên quan, có thể null khi đang chờ mở sổ |
| `target_product_id` | Sản phẩm đích khi mở sổ |
| `amount` | Số tiền giao dịch |
| `transaction_type` | Loại giao dịch |
| `status` | `PENDING`, `APPROVED`, `REJECTED` |
| `interest_amount` | Tiền lãi phát sinh khi rút/tất toán |
| `processed_by` | Nhân viên xử lý |
| `created_at` | Ngày tạo |

Các loại giao dịch:

- `DEPOSIT_TO_WALLET`
- `WITHDRAW_FROM_WALLET`
- `OPEN_SAVINGS`
- `DEPOSIT_TO_SAVINGS`
- `WITHDRAW_FROM_SAVINGS`
- `CLOSE_SAVINGS`
- `TRANSFER_OUT`
- `TRANSFER_IN`
- `AUTO_ROLLOVER`

#### `system_configs`

Lưu tham số nghiệp vụ để Admin có thể thay đổi.

| Cấu hình | Mặc định | Ý nghĩa |
|---|---:|---|
| `MIN_OPEN_AMOUNT` | 1,000,000 | Số tiền tối thiểu khi mở sổ |
| `MIN_SAVINGS_DEPOSIT_AMOUNT` | 100,000 | Số tiền tối thiểu khi gửi thêm |
| `NON_TERM_MIN_DAYS` | 15 | Số ngày giữ tối thiểu với sổ không kỳ hạn |

### 4.3 Quan hệ dữ liệu

```text
users 1 --- N savings_accounts
users 1 --- N transactions
savings_products 1 --- N savings_accounts
savings_products 1 --- N transactions (target_product_id)
users 1 --- N transactions (processed_by)
```

---

## 5. Phân quyền

### 5.1 CUSTOMER

Khách hàng là người dùng cuối. Khách hàng được:

- Xem hồ sơ cá nhân và số tài khoản.
- Xem số dư ví cá nhân, ví khả dụng, tổng tài sản hiện tại.
- Xem danh sách sổ tiết kiệm của mình.
- Tạo yêu cầu mở sổ, gửi thêm, rút tiền và tất toán.
- Chuyển khoản cho khách hàng khác trong hệ thống.
- Xem lịch sử giao dịch.
- Xem biểu đồ tăng trưởng từng sổ và mô phỏng tiết kiệm.

Khách hàng không được:

- Duyệt giao dịch.
- Truy cập dữ liệu của khách hàng khác.
- Quản lý sản phẩm, cấu hình hoặc nhân sự.

### 5.2 STAFF

Nhân viên là người vận hành nghiệp vụ. Staff được:

- Xem hàng đợi giao dịch `PENDING`.
- Duyệt hoặc từ chối yêu cầu của khách hàng.
- Xem danh sách khách hàng ở mức thông tin định danh, không xem số dư ví.
- Tra cứu danh sách sổ tiết kiệm ở mức thông tin nghiệp vụ, không xem số dư gốc từng sổ trên UI tra cứu.
- Xem báo cáo BM5 và thống kê xu hướng.

Staff không được:

- Quản lý tài khoản nhân sự.
- Sửa sản phẩm tiết kiệm hoặc tham số hệ thống.
- Xem số dư ví cá nhân của khách hàng.

### 5.3 ADMIN

Admin là người quản trị hệ thống. Admin được:

- Xem dashboard tổng quan.
- Quản lý người dùng: tạo tài khoản, đổi role, khóa/mở khóa.
- Quản lý sản phẩm tiết kiệm: thêm, sửa, bật/tắt.
- Quản lý tham số hệ thống QĐ6.
- Xem báo cáo BM5.

Admin không được:

- Duyệt giao dịch của khách hàng. Chức năng duyệt chỉ thuộc Staff.
- Xem số dư ví của khách hàng.
- Xem số dư gốc từng sổ trong modal chi tiết người dùng.

---

## 6. Backend API chính

### 6.1 Authentication

| Endpoint | Method | Role | Mô tả |
|---|---|---|---|
| `/api/auth/register` | POST | Public | Đăng ký khách hàng mới, tạo số tài khoản và thưởng 10,000,000 VND |
| `/api/auth/login` | POST | Public | Đăng nhập, trả JWT có `user_id`, `role`, `exp` |
| `/api/auth/forgot-password` | POST | Public | Đặt lại mật khẩu bằng email và CMND/CCCD |
| `/api/ping` | GET | Public | Smoke test backend |

### 6.2 Client API

| Endpoint | Method | Mô tả |
|---|---|---|
| `/api/client/me` | GET | Thông tin cá nhân khách hàng |
| `/api/client/me` | PATCH | Cập nhật địa chỉ |
| `/api/client/dashboard` | GET | Tổng quan ví, sổ, lãi dự tính và tổng tài sản hiện tại |
| `/api/client/savings-products` | GET | Danh sách sản phẩm đang hoạt động |
| `/api/client/savings-accounts` | GET | Danh sách sổ của khách hàng |
| `/api/client/savings-accounts/<account_id>` | GET | Chi tiết sổ |
| `/api/client/savings-accounts/<account_id>/estimate-interest` | GET | Ước tính lãi |
| `/api/client/open-savings` | POST | Tạo yêu cầu mở sổ |
| `/api/client/savings-accounts/<account_id>/deposit-requests` | POST | Tạo yêu cầu gửi thêm |
| `/api/client/savings-accounts/<account_id>/withdraw-requests` | POST | Tạo yêu cầu rút một phần |
| `/api/client/close-savings/<account_id>` | POST | Tạo yêu cầu tất toán |
| `/api/client/transfers` | POST | Chuyển khoản nội bộ |
| `/api/client/transactions` | GET | Lịch sử giao dịch |

### 6.3 Staff API

| Endpoint | Method | Role | Mô tả |
|---|---|---|---|
| `/api/transactions` | GET | STAFF, ADMIN | Xem danh sách giao dịch |
| `/api/transactions/<id>/approve` | PUT | STAFF | Duyệt giao dịch |
| `/api/transactions/<id>/reject` | PUT | STAFF | Từ chối giao dịch |
| `/api/transactions/<id>` | PATCH | STAFF | Cập nhật trạng thái duyệt |
| `/api/users` | GET | STAFF, ADMIN | Danh sách khách hàng, không trả số dư ví |
| `/api/savings-accounts` | GET | STAFF, ADMIN | Danh sách sổ, không trả số dư gốc |
| `/api/savings-accounts/<id>` | GET | STAFF, ADMIN | Chi tiết sổ, không trả số dư gốc |
| `/api/balance-system` | GET | STAFF, ADMIN | Tổng tiền gốc tiết kiệm toàn hệ thống |
| `/api/reports/daily-activity` | GET | STAFF, ADMIN | BM5.1, có thể lấy toàn bộ hoặc lọc theo ngày |
| `/api/reports/monthly-open-close` | GET | STAFF, ADMIN | BM5.2, có thể lấy toàn bộ hoặc lọc theo tháng |
| `/api/staff/analytics` | GET | STAFF, ADMIN | Thống kê xu hướng theo tháng |

### 6.4 Admin API

| Endpoint | Method | Mô tả |
|---|---|---|
| `/api/admin/dashboard` | GET | Dashboard tổng quan |
| `/api/admin/users` | GET | Danh sách người dùng |
| `/api/admin/users/<id>` | GET | Chi tiết người dùng, không lộ số dư |
| `/api/admin/users` | POST | Tạo tài khoản |
| `/api/admin/users/<id>/role` | PUT | Đổi role |
| `/api/admin/users/<id>/status` | PUT | Khóa/mở khóa tài khoản |
| `/api/admin/users/<id>` | PATCH | Cập nhật role/status |
| `/api/admin/savings-products` | GET | Danh sách sản phẩm |
| `/api/admin/savings-products` | POST | Tạo sản phẩm |
| `/api/admin/savings-products/<id>` | PATCH/PUT | Cập nhật sản phẩm |
| `/api/admin/savings-products/<id>/toggle` | PUT | Bật/tắt sản phẩm |
| `/api/admin/configs` | GET | Danh sách tham số |
| `/api/admin/configs` | POST | Tạo tham số |
| `/api/admin/configs/<key>` | PATCH/PUT | Cập nhật tham số |
| `/api/admin/configs/<key>` | DELETE | Xóa tham số |

### 6.5 SSE realtime

| Endpoint | Method | Mô tả |
|---|---|---|
| `/api/events?token=<jwt>` | GET | Kết nối Server-Sent Events |

SSE dùng để thông báo khi có giao dịch mới, giao dịch được duyệt/từ chối hoặc hàng đợi thay đổi.

---

## 7. Frontend theo vai trò

### 7.1 Trang Login

Route: `/login`

Chức năng:

- Đăng nhập bằng email và mật khẩu.
- Đăng ký khách hàng mới.
- Sau khi đăng nhập, tự chuyển hướng theo role:
  - `ADMIN` -> `/admin`
  - `STAFF` -> `/staff/`
  - `CUSTOMER` -> `/client/`

### 7.2 Client SPA

File: `frontend/client/index.html`

Các tab chính:

| Tab | Chức năng |
|---|---|
| Trang chủ | Tổng tài sản, ví khả dụng, sổ đang mở, giao dịch gần đây |
| Chuyển khoản | Chuyển tiền qua số tài khoản khách hàng khác |
| Tiết kiệm của tôi | Xem sổ, sản phẩm, mở sổ, gửi thêm, rút, tất toán |
| Lịch sử giao dịch | Xem toàn bộ giao dịch của khách hàng |
| Thông tin cá nhân | Xem hồ sơ, số tài khoản, ví, lãi dự tính |
| Biểu đồ tăng trưởng | Biểu đồ chi tiết từng sổ, có trục, lãi dự tính, tỷ lệ sinh lời và tiến độ |
| Mô phỏng tiết kiệm | Mô phỏng vốn, kỳ hạn, lãi suất, số năm và tái tục |

Điểm nổi bật:

- Tổng tài sản hiện tại = ví khả dụng + gốc tiết kiệm + lãi dự tính.
- Biểu đồ tăng trưởng dùng SVG, tính theo lãi suất/kỳ hạn từ dữ liệu sản phẩm thực tế.
- Mô phỏng tiết kiệm cho phép chọn sản phẩm đang hoạt động hoặc tự chỉnh tham số.
- Chống XSS ở dữ liệu render bằng `escapeHtml`.
- Nhận thông báo realtime qua SSE.

### 7.3 Staff SPA

File: `frontend/staff/index.html`

Các tab chính:

| Tab | Chức năng |
|---|---|
| Tổng quan | Số giao dịch chờ, khách hàng, sổ, tổng tiền gửi; hiển thị giao dịch mới |
| Duyệt giao dịch | Duyệt/từ chối giao dịch PENDING, lọc theo trạng thái và loại |
| Khách hàng | Tra cứu thông tin định danh, không hiển thị số dư ví |
| Sổ tiết kiệm | Tra cứu sổ, không hiển thị số dư gốc từng sổ |
| Báo cáo BM5 | BM5.1 và BM5.2, tự load toàn bộ, có filter ngày/tháng |
| Thống kê xu hướng | Biểu đồ tiền gửi, tiền rút, sổ mới và khách hàng mới theo ngày |

Giao diện Staff dùng phong cách neo-brutalist với viền đen, shadow rõ, bảng dữ liệu dày và dễ thao tác.

### 7.4 Admin SPA

File chính: `frontend/src/App.jsx`, `frontend/src/layouts/AdminLayout.jsx`

Các trang:

| Route | Chức năng |
|---|---|
| `/admin` | Dashboard tổng quan |
| `/admin/users` | Quản lý người dùng, role, khóa/mở khóa |
| `/admin/savings-products` | Quản lý sản phẩm tiết kiệm |
| `/admin/configs` | Quản lý tham số QĐ6 |
| `/admin/reports` | Báo cáo BM5, tự load và polling |

Admin không có trang duyệt giao dịch. Chức năng duyệt thuộc Staff.

---

## 8. Quy tắc nghiệp vụ

Phần này mô tả cách hệ thống xử lý tiền. Trong các ví dụ bên dưới, giả sử khách hàng mới có ví ban đầu `10,000,000 VND`.

### 8.1 Mở sổ

- Khách hàng chọn sản phẩm và nhập số tiền.
- Số tiền phải >= `MIN_OPEN_AMOUNT`.
- Hệ thống tạo giao dịch `OPEN_SAVINGS` với trạng thái `PENDING`.
- Staff duyệt thì hệ thống trừ ví và tạo bản ghi `savings_accounts`.

Ví dụ:

```text
Ví khách hàng ban đầu:        10,000,000 VND
Khách hàng mở sổ:              2,000,000 VND
Trạng thái ban đầu:            PENDING

Sau khi Staff duyệt:
Ví còn lại:                    8,000,000 VND
Gốc sổ tiết kiệm mới:          2,000,000 VND
```

Nếu Staff từ chối, ví không bị trừ và sổ không được tạo.

### 8.2 Gửi thêm

- Số tiền phải >= `MIN_SAVINGS_DEPOSIT_AMOUNT`.
- Với sổ có kỳ hạn, chỉ cho gửi thêm khi đã đến kỳ hạn tính lãi.
- Giao dịch được tạo ở trạng thái `PENDING`.
- Staff duyệt thì hệ thống trừ ví và cộng vào gốc sổ.

Ví dụ:

```text
Ví hiện tại:                   8,000,000 VND
Gốc sổ hiện tại:               2,000,000 VND
Khách hàng gửi thêm:             500,000 VND

Sau khi Staff duyệt:
Ví còn lại:                    7,500,000 VND
Gốc sổ mới:                    2,500,000 VND
```

Lưu ý: tiền gửi thêm chưa được cộng ngay khi khách hàng bấm yêu cầu. Tiền chỉ thay đổi sau khi Staff duyệt.

### 8.3 Rút tiền

- Sổ không kỳ hạn có thể rút một phần.
- Sổ có kỳ hạn không rút một phần, phải tất toán toàn bộ.
- Sổ không kỳ hạn phải giữ tối thiểu `NON_TERM_MIN_DAYS`.
- Lãi được tính và cộng về ví khi Staff duyệt.

Ví dụ với sổ không kỳ hạn:

```text
Gốc sổ không kỳ hạn:           2,000,000 VND
Lãi suất không kỳ hạn:                 0.5%/năm
Thời gian đã gửi:                     20 ngày
Khách hàng rút:                 500,000 VND
```

Cách tính lãi cho phần tiền rút:

```text
Tiền lãi = 500,000 × 0.5 / 100 × 20 / 365
         ≈ 136.99 VND
```

Sau khi Staff duyệt:

```text
Tiền cộng về ví:                 500,136.99 VND
Gốc còn lại trong sổ:          1,500,000 VND
```

Nếu sổ không kỳ hạn chưa gửi đủ số ngày tối thiểu, hệ thống không cho tạo yêu cầu rút.

### 8.4 Tất toán

- Khách hàng tạo yêu cầu tất toán.
- Nếu tất toán trước hạn với sổ có kỳ hạn, hệ thống áp dụng lãi suất không kỳ hạn.
- Staff duyệt thì sổ chuyển `CLOSED`, gốc và lãi được cộng về ví.

Ví dụ 1: tất toán đúng hạn.

```text
Gốc sổ:                       2,000,000 VND
Kỳ hạn:                              3 tháng
Lãi suất sản phẩm:                    4.5%/năm
Thời gian đủ hạn:                    90 ngày
```

Cách tính:

```text
Tiền lãi = 2,000,000 × 4.5 / 100 × 90 / 365
         ≈ 22,191.78 VND

Tổng tiền nhận về ví = 2,000,000 + 22,191.78
                     ≈ 2,022,191.78 VND
```

Ví dụ 2: tất toán trước hạn.

```text
Gốc sổ:                       2,000,000 VND
Kỳ hạn gốc:                          3 tháng
Lãi suất sản phẩm:                    4.5%/năm
Khách hàng tất toán sau:             30 ngày
Lãi suất áp dụng:                     0.5%/năm
```

Vì khách hàng rút trước hạn, hệ thống không dùng lãi suất `4.5%/năm`, mà dùng lãi suất không kỳ hạn:

```text
Tiền lãi = 2,000,000 × 0.5 / 100 × 30 / 365
         ≈ 821.92 VND

Tổng tiền nhận về ví = 2,000,000 + 821.92
                     ≈ 2,000,821.92 VND
```

### 8.5 Chuyển khoản

- Khách hàng nhập số tài khoản nhận và số tiền.
- Giao dịch chuyển khoản thực thi ngay, không qua Staff.
- Hệ thống tạo 2 giao dịch: `TRANSFER_OUT` cho người gửi và `TRANSFER_IN` cho người nhận.

Ví dụ:

```text
Ví người gửi trước chuyển:     8,000,000 VND
Ví người nhận trước chuyển:    1,000,000 VND
Số tiền chuyển:                  500,000 VND

Sau chuyển khoản:
Ví người gửi:                  7,500,000 VND
Ví người nhận:                 1,500,000 VND
```

Khác với mở sổ/gửi thêm/rút/tất toán, chuyển khoản không cần Staff duyệt.

### 8.6 Auto-rollover

- Với sổ có kỳ hạn, khi đến hạn hệ thống có thể tự tái tục khi người dùng/staff truy vấn.
- Lãi được cộng vào gốc.
- `opened_at` được cập nhật sang kỳ mới.
- Ghi nhận giao dịch `AUTO_ROLLOVER`.

Ví dụ:

```text
Gốc ban đầu:                   2,000,000 VND
Kỳ hạn:                              3 tháng
Lãi suất:                             4.5%/năm
Một kỳ được tính là:                  90 ngày
```

Sau khi đủ 1 kỳ:

```text
Lãi kỳ 1 = 2,000,000 × 4.5 / 100 × 90 / 365
         ≈ 22,191.78 VND

Gốc mới sau tái tục = 2,000,000 + 22,191.78
                    ≈ 2,022,191.78 VND
```

Nếu tiếp tục đủ thêm 1 kỳ nữa, hệ thống tính lãi trên gốc mới `2,022,191.78 VND`, không phải gốc cũ `2,000,000 VND`. Đây là cơ chế lãi nhập gốc.

### 8.7 Tính lãi

Hệ thống dùng các hàm trong `backend/common/savings_rules.py`.

Công thức tổng quát:

```text
Tiền lãi = Gốc × Lãi suất năm / 100 × Thời gian quy đổi theo năm
```

Trong code hiện tại, thời gian được tính theo ngày thực tế:

```text
Thời gian quy đổi theo năm = Số ngày gửi / 365
```

Vì vậy công thức có thể viết rõ hơn là:

```text
Tiền lãi = Gốc × Lãi suất năm / 100 × Số ngày gửi / 365
```

Ví dụ tổng quát:

```text
Gốc:                           1,000,000 VND
Lãi suất:                              6%/năm
Số ngày gửi:                         180 ngày

Tiền lãi = 1,000,000 × 6 / 100 × 180 / 365
         ≈ 29,589.04 VND
```

Các điểm cần nhớ:

- Lãi suất trong database là lãi suất theo năm.
- Kỳ hạn 1 tháng được quy đổi gần đúng là 30 ngày khi kiểm tra đủ hạn.
- Nếu sổ có kỳ hạn bị tất toán trước hạn, hệ thống dùng lãi suất không kỳ hạn.
- Với sổ không kỳ hạn, hệ thống luôn dùng lãi suất không kỳ hạn.
- Với auto-rollover, lãi được cộng vào gốc rồi mới bắt đầu kỳ tiếp theo.

---

## 9. Bảo mật và kiểm soát quyền

Các điểm bảo mật chính:

- Mật khẩu được hash bằng `pbkdf2:sha256`.
- JWT có thời hạn 2 giờ.
- Backend kiểm tra role bằng decorator `@require_role`.
- SQL dùng parameterized query với `%s`, hạn chế SQL injection.
- Client/Staff render dữ liệu qua hàm escape HTML để giảm rủi ro XSS.
- Staff/Admin không được xem `wallet_balance` của khách hàng.
- Staff/Admin không xem số dư gốc từng sổ trong các màn tra cứu cá nhân.
- Admin không có quyền duyệt giao dịch; API duyệt trả `403` với role Admin.

---

## 10. Hướng dẫn cài đặt và chạy

### 10.1 Cài backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 10.2 Khởi tạo database

```bash
mysql -u root -p < smart_savings.sql
```

Backend mặc định dùng:

```text
DB_HOST=localhost
DB_USER=smart_savings
DB_PASSWORD=SmartSavings@2026!
DB_NAME=modern_savings_db
```

Có thể override qua biến môi trường.

### 10.3 Chạy backend

```bash
cd backend
python app.py
```

Backend chạy tại:

```text
http://localhost:5000
```

Smoke test:

```bash
curl http://localhost:5000/api/ping
```

### 10.4 Chạy frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend chạy tại:

```text
http://localhost:5173
```

Các đường dẫn:

- Login: `http://localhost:5173/login`
- Client: `http://localhost:5173/client/`
- Staff: `http://localhost:5173/staff/`
- Admin: `http://localhost:5173/admin`

### 10.5 Tài khoản mặc định

Các tài khoản này được tạo/cập nhật tự động khi backend khởi động:

| Role | Email | Password |
|---|---|---|
| ADMIN | `admin@gmail.com` | `admin123` |
| STAFF | `staff@gmail.com` | `staff123` |

Khách hàng có thể đăng ký trực tiếp ở trang Login. Khách hàng mới được thưởng 10,000,000 VND để demo.

### 10.6 Dữ liệu mock tùy chọn

Repo có `seed_mock_data.py` và `seed_mock_data.sql` để tạo dữ liệu lịch sử phục vụ biểu đồ/thống kê. Chỉ chạy khi database và product/user ID phù hợp với dữ liệu seed.

---

## 11. Hướng dẫn sử dụng theo vai trò

### 11.1 Khách hàng

1. Vào `/login`, chọn đăng ký khách hàng.
2. Đăng nhập bằng tài khoản vừa tạo.
3. Ở Trang chủ, xem ví khả dụng, tổng tài sản và giao dịch gần đây.
4. Vào “Tiết kiệm của tôi”.
5. Chọn sản phẩm tiết kiệm và nhập số tiền mở sổ.
6. Bấm “Mở sổ tiết kiệm”.
7. Chờ Staff duyệt.
8. Sau khi duyệt, sổ xuất hiện trong danh sách.
9. Có thể gửi thêm, rút một phần với sổ không kỳ hạn, hoặc tất toán.
10. Vào “Biểu đồ tăng trưởng” để xem trực quan từng sổ.
11. Vào “Mô phỏng tiết kiệm” để thử các kịch bản vốn/kỳ hạn/lãi suất/tái tục.

### 11.2 Nhân viên

1. Đăng nhập bằng tài khoản Staff.
2. Vào `/staff/`.
3. Màn Tổng quan hiển thị giao dịch đang chờ.
4. Vào “Duyệt giao dịch”.
5. Chọn giao dịch và bấm Duyệt hoặc Từ chối.
6. Kiểm tra lại báo cáo BM5 hoặc thống kê xu hướng.
7. Có thể tra cứu khách hàng và sổ tiết kiệm, nhưng không xem số dư ví hoặc số dư gốc từng sổ.

### 11.3 Quản trị viên

1. Đăng nhập bằng tài khoản Admin.
2. Vào dashboard `/admin`.
3. Quản lý tài khoản ở “Nhân sự”.
4. Thêm/sửa/bật/tắt sản phẩm ở “Gói tiết kiệm”.
5. Cập nhật quy định nghiệp vụ ở “Tham số”.
6. Xem báo cáo BM5 ở “Báo cáo BM5”.
7. Admin không duyệt giao dịch; việc duyệt thuộc Staff.

---

## 12. Kiểm thử

### 12.1 Python integration test

File: `test_flow.py`

Luồng kiểm thử:

1. Đăng ký khách hàng.
2. Đăng nhập khách hàng.
3. Kiểm tra welcome bonus 10,000,000 VND.
4. Tạo tài khoản Staff test.
5. Mở sổ tiết kiệm.
6. Staff duyệt giao dịch mở sổ.
7. Kiểm tra ví bị trừ đúng.
8. Ước tính lãi.
9. Tất toán sổ.
10. Staff duyệt tất toán.
11. Kiểm tra ví nhận lại gốc và lãi.

Chạy:

```bash
python test_flow.py
```

### 12.2 Playwright E2E

File: `frontend/tests/role-flow.spec.js`

Luồng kiểm thử:

1. Đăng ký khách hàng qua UI.
2. Login khách hàng.
3. Mở sổ tiết kiệm và thấy giao dịch `PENDING`.
4. Login Staff.
5. Staff duyệt giao dịch.
6. Login lại khách hàng và thấy sổ mới.
7. Login Admin và kiểm tra Admin không có menu duyệt giao dịch.
8. Kiểm tra không có JS error và request lỗi.

Chạy:

```bash
cd frontend
npx playwright test tests/role-flow.spec.js --reporter=line
```

### 12.3 Build frontend

```bash
cd frontend
npm run build
```

### 12.4 Compile backend

```bash
python -m py_compile backend/app.py backend/common/auth.py backend/common/db.py backend/common/events.py backend/common/requireRole.py backend/common/savings_rules.py backend/client/client.py backend/staff/staff.py backend/admin/admin.py
```

---

## 13. Đánh giá

### 13.1 Điểm đạt được

- Đáp ứng mô hình 3 role: Customer, Staff, Admin.
- Có quy trình Maker-Checker rõ ràng.
- Có database MySQL đầy đủ bảng người dùng, sản phẩm, sổ, giao dịch, cấu hình.
- Có tham số QĐ6 để Admin thay đổi quy định nghiệp vụ.
- Có tính lãi, rút trước hạn, giữ tối thiểu, auto-rollover.
- Có báo cáo BM5.1 và BM5.2.
- Có thống kê xu hướng bằng biểu đồ.
- Có realtime notification bằng SSE.
- Có test integration và E2E browser.

### 13.2 Hạn chế

- Client và Staff là single-file HTML lớn, khó bảo trì nếu phát triển lâu dài.
- Backend chưa có migration framework chính thức như Alembic.
- Chưa có unit test riêng cho từng hàm tính lãi/auto-rollover.
- JWT secret có giá trị mặc định trong code, khi triển khai thật cần bắt buộc dùng biến môi trường.
- Chưa có pagination cho các danh sách lớn.
- Chưa có rate limiting cho login/API.
- Auto-rollover đang xử lý lazy khi truy vấn, chưa có background scheduler.

### 13.3 Hướng phát triển

- Tách Client/Staff sang React component hoặc framework frontend thống nhất.
- Thêm unit test cho `savings_rules.py`.
- Thêm phân trang, tìm kiếm nâng cao và export báo cáo.
- Bổ sung logging/audit trail cho hành động duyệt giao dịch.
- Bổ sung AI advisor để gợi ý thời điểm gửi/rút tối ưu theo sản phẩm và mục tiêu tiết kiệm.
- Triển khai production với Gunicorn/uWSGI, reverse proxy và secret qua environment.

---

## 14. Kết luận

Smart Savings mô phỏng đầy đủ các chức năng cốt lõi của hệ thống quản lý sổ tiết kiệm: quản lý người dùng, sản phẩm tiết kiệm, mở/gửi/rút/tất toán sổ, duyệt giao dịch theo Maker-Checker, báo cáo và phân quyền dữ liệu. Hệ thống có thể dùng để demo quy trình nghiệp vụ ngân hàng trong phạm vi môn Nhập môn Công nghệ Phần mềm, đồng thời có nền tảng để mở rộng thêm các chức năng nâng cao như tư vấn tiết kiệm và phân tích tài chính cá nhân.
