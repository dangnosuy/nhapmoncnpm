# BÁO CÁO ĐỒ ÁN: SMART SAVINGS — HỆ THỐNG QUẢN LÝ TIẾT KIỆM

**Nhóm 13 — Nhập môn Công nghệ Phần mềm (SE104)**

---

## Mục lục

1. [Giới thiệu đề tài](#1-giới-thiệu-đề-tài)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Cơ sở dữ liệu](#3-cơ-sở-dữ-liệu)
4. [Backend API](#4-backend-api)
5. [Frontend](#5-frontend)
6. [Business Logic & Quy tắc nghiệp vụ](#6-business-logic--quy-tắc-nghiệp-vụ)
7. [Test Cases](#7-test-cases)
8. [Đánh giá & Hạn chế](#8-đánh-giá--hạn-chế)

---

## 1. Giới thiệu đề tài

**Smart Savings** là hệ thống quản lý tiết kiệm ngân hàng với 3 vai trò người dùng:

| Vai trò | Chức năng chính |
|---------|-----------------|
| **CUSTOMER** | Mở sổ tiết kiệm, gửi/rút tiền, chuyển khoản, xem báo cáo cá nhân |
| **STAFF** | Duyệt/từ chối giao dịch, quản lý vận hành, xem báo cáo hệ thống |
| **ADMIN** | Quản lý người dùng, sản phẩm tiết kiệm, cấu hình hệ thống, báo cáo tổng quan |

**Công nghệ sử dụng:**
- **Backend:** Python 3, Flask (REST API), MySQL (mysql-connector-python), JWT authentication, Server-Sent Events (SSE)
- **Frontend:** React + Vite (Admin SPA), HTML/CSS/JS thuần (Client SPA & Staff SPA)
- **Testing:** Python integration tests, Playwright E2E

---

## 2. Kiến trúc hệ thống

### 2.1 Tổng quan kiến trúc

```
┌──────────────────────────────────────────────────────┐
│                    Frontend                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  Admin SPA  │  │  Client SPA  │  │  Staff SPA  │  │
│  │ (React+Vite)│  │(Single HTML) │  │(Single HTML)│  │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘  │
│         │                │                  │         │
│         └────────────────┼──────────────────┘         │
│                          │ REST API + SSE              │
└──────────────────────────┼───────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────┐
│                    Backend (Flask)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Admin   │  │  Client  │  │  Staff   │           │
│  │ Blueprint│  │ Blueprint│  │ Blueprint│           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       └──────────────┼─────────────┘                  │
│              ┌───────┴────────┐                       │
│              │  Common Layer  │                       │
│              │ auth, db, SSE  │                       │
│              └───────┬────────┘                       │
└──────────────────────┼───────────────────────────────┘
                       │
                ┌──────┴──────┐
                │   MySQL DB  │
                │modern_savings│
                └─────────────┘
```

### 2.2 Cấu trúc thư mục

```
nhapmoncnpm/
├── backend/
│   ├── app.py                  # App factory, blueprint registration, auto-migration
│   ├── common/
│   │   ├── db.py               # MySQL connection (thread-local, lazy init)
│   │   ├── auth.py             # JWT auth: login, register, forgot-password
│   │   ├── events.py           # SSE pub/sub real-time events
│   │   ├── requireRole.py      # Role-check decorator (@require_role)
│   │   └── savings_rules.py    # Business rules: lãi suất, kỳ hạn, auto-rollover
│   ├── admin/admin.py          # Admin endpoints (users, products, configs)
│   ├── staff/staff.py          # Staff endpoints (approve/reject, reports)
│   └── client/client.py        # Customer endpoints (savings, wallet, transfers)
├── frontend/
│   ├── index.html              # Admin SPA entry point
│   ├── src/                    # Admin React source
│   │   ├── App.jsx             # Router, ProtectedRoute, role-based redirects
│   │   ├── api/axios.js        # Axios instance, JWT interceptor
│   │   ├── layouts/AdminLayout.jsx
│   │   └── pages/admin/        # Dashboard, Users, Products, Configs, Reports
│   ├── client/index.html       # Customer SPA (standalone ~3476 lines)
│   └── staff/index.html        # Staff SPA (standalone ~920 lines)
├── smart_savings.sql           # DB schema + seed data
├── test_flow.py                # Python integration test (happy path)
├── run_api_tests.py            # Comprehensive API test suite
└── requirements.txt
```

### 2.3 Multi-Entry Vite Build

Hệ thống sử dụng **3 SPA riêng biệt** cho 3 vai trò:

| App | Entry | Công nghệ | Đặc điểm |
|-----|-------|-----------|----------|
| Admin | `frontend/index.html` | React + Vite | Build qua Vite, hot-reload dev |
| Client | `frontend/client/index.html` | HTML/CSS/JS thuần | Single-file, không cần build |
| Staff | `frontend/staff/index.html` | HTML/CSS/JS thuần | Single-file, không cần build |

**Vite dev server:**
- Proxy `/api/*` → `http://localhost:5000`
- Redirect `/client` → `/client/`, `/staff` → `/staff/`

**Routing dựa trên role:** Sau khi login, `App.jsx` dùng `ExternalRoleRoute` để redirect STAFF → `/staff/` và CUSTOMER → `/client/` qua `window.location.replace`.

---

## 3. Cơ sở dữ liệu

### 3.1 Database: `modern_savings_db`

### 3.2 Sơ đồ quan hệ (ER Diagram mô tả)

```
users (1) ──────< (N) savings_accounts
users (1) ──────< (N) transactions
savings_products (1) ─< (N) savings_accounts
savings_products (1) ─< (N) transactions (target_product_id)
users (1) ──────< (N) transactions (processed_by)
```

### 3.3 Chi tiết các bảng

#### Bảng `users`
| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|-----|-------------|-----------|--------|
| `user_id` | INT | PK, AUTO_INCREMENT | ID người dùng |
| `email` | VARCHAR(100) | NOT NULL, UNIQUE | Email đăng nhập |
| `password_hash` | VARCHAR(255) | NOT NULL | Mật khẩu hash (pbkdf2:sha256) |
| `full_name` | VARCHAR(100) | NOT NULL | Họ tên |
| `identity_card` | VARCHAR(20) | UNIQUE | CMND/CCCD |
| `account_number` | VARCHAR(20) | UNIQUE | Số tài khoản 10 chữ số |
| `address` | VARCHAR(255) | nullable | Địa chỉ |
| `role` | ENUM('CUSTOMER','STAFF','ADMIN') | DEFAULT 'CUSTOMER' | Vai trò |
| `wallet_balance` | DECIMAL(15,2) | DEFAULT 0.00 | Số dư ví |
| `status` | ENUM('ACTIVE','LOCKED') | DEFAULT 'ACTIVE' | Trạng thái tài khoản |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |

#### Bảng `savings_products`
| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|-----|-------------|-----------|--------|
| `product_id` | INT | PK, AUTO_INCREMENT | ID sản phẩm |
| `name` | VARCHAR(100) | NOT NULL | Tên sản phẩm |
| `term_months` | INT | NOT NULL, DEFAULT 0 | Kỳ hạn (tháng), 0 = không kỳ hạn |
| `interest_rate` | DECIMAL(5,2) | NOT NULL | Lãi suất năm (%) |
| `min_days_hold` | INT | DEFAULT 0 | Số ngày giữ tối thiểu |
| `is_active` | BOOLEAN | DEFAULT TRUE | Đang hoạt động |
| `description` | TEXT | nullable | Mô tả sản phẩm |

#### Bảng `savings_accounts`
| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|-----|-------------|-----------|--------|
| `account_id` | INT | PK, AUTO_INCREMENT | ID sổ tiết kiệm |
| `user_id` | INT | NOT NULL, FK → users | Chủ sở hữu |
| `product_id` | INT | NOT NULL, FK → savings_products | Loại sản phẩm |
| `principal_balance` | DECIMAL(15,2) | NOT NULL, CHECK >= 0 | Số dư gốc |
| `opened_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày mở |
| `status` | ENUM('ACTIVE','CLOSED') | DEFAULT 'ACTIVE' | Trạng thái |

#### Bảng `transactions`
| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|-----|-------------|-----------|--------|
| `transaction_id` | INT | PK, AUTO_INCREMENT | ID giao dịch |
| `user_id` | INT | NOT NULL, FK → users | Người tạo |
| `account_id` | INT | nullable, FK → savings_accounts | Sổ tiết kiệm liên quan |
| `target_product_id` | INT | nullable, FK → savings_products | Sản phẩm đích (khi OPEN) |
| `amount` | DECIMAL(15,2) | NOT NULL, CHECK > 0 | Số tiền |
| `transaction_type` | ENUM (9 loại) | NOT NULL | Loại giao dịch |
| `status` | ENUM('PENDING','APPROVED','REJECTED') | DEFAULT 'PENDING' | Trạng thái duyệt |
| `interest_amount` | DECIMAL(15,2) | DEFAULT 0.00 | Tiền lãi |
| `processed_by` | INT | nullable, FK → users | Nhân viên xử lý |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |

**9 loại giao dịch:**
`DEPOSIT_TO_WALLET`, `WITHDRAW_FROM_WALLET`, `OPEN_SAVINGS`, `DEPOSIT_TO_SAVINGS`, `WITHDRAW_FROM_SAVINGS`, `CLOSE_SAVINGS`, `TRANSFER_OUT`, `TRANSFER_IN`, `AUTO_ROLLOVER`

#### Bảng `system_configs`
| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|-----|-------------|-----------|--------|
| `config_key` | VARCHAR(50) | PK | Tên tham số |
| `config_value` | VARCHAR(255) | NOT NULL | Giá trị |
| `description` | VARCHAR(255) | nullable | Mô tả |

### 3.4 Dữ liệu mặc định

- **system_configs:** `MIN_OPEN_AMOUNT=1000000`, `MIN_SAVINGS_DEPOSIT_AMOUNT=100000`, `NON_TERM_MIN_DAYS=15`
- **Tài khoản mặc định:** Admin (`admin@gmail.com/admin123`), Staff (`staff@gmail.com/staff123`) — tạo tự động khi khởi động server
- **Sản phẩm mặc định:** Không kỳ hạn (0.5%/năm), 3 tháng (5.0%/năm), 6 tháng (5.5%/năm)
- **Khách hàng đăng ký mới:** Nhận thưởng chào mừng 10,000,000 VND vào ví

---

## 4. Backend API

### 4.1 Authentication

| Endpoint | Method | Mô tả |
|----------|--------|--------|
| `POST /api/auth/register` | Public | Đăng ký khách hàng mới. Tạo số tài khoản 10 chữ số, thưởng 10M VND |
| `POST /api/auth/login` | Public | Đăng nhập. Trả JWT (2h expiry) chứa `user_id` và `role`. Kiểm tra LOCKED |
| `POST /api/auth/forgot-password` | Public | Đặt lại mật khẩu bằng email + CMND. Tối thiểu 6 ký tự |

**JWT:** Ký HS256, payload `{user_id, role, exp}`, thời hạn 2 giờ.

### 4.2 Admin API (yêu cầu role ADMIN)

| Endpoint | Method | Mô tả |
|----------|--------|--------|
| `GET /api/admin/dashboard` | GET | Thống kê tổng quan: số khách hàng, nhân viên, sổ tiết kiệm, tiền gửi, giao dịch chờ |
| `GET /api/admin/users` | GET | Danh sách users (filter theo role, status, search) |
| `GET /api/admin/users/<id>` | GET | Chi tiết user + danh sách sổ tiết kiệm |
| `POST /api/admin/users` | POST | Tạo user mới (STAFF/ADMIN/CUSTOMER) |
| `PUT /api/admin/users/<id>/role` | PUT | Đổi vai trò user (chặn tự đổi role mình) |
| `PUT /api/admin/users/<id>/status` | PUT | Khóa/mở khóa user (chặn tự khóa mình) |
| `GET /api/admin/savings-products` | GET | Danh sách tất cả sản phẩm (cả inactive) |
| `POST /api/admin/savings-products` | POST | Tạo sản phẩm mới |
| `PATCH /api/admin/savings-products/<id>` | PATCH/PUT | Cập nhật sản phẩm |
| `PUT /api/admin/savings-products/<id>/toggle` | PUT | Bật/tắt sản phẩm |
| `GET /api/admin/configs` | GET | Danh sách cấu hình hệ thống |
| `PATCH /api/admin/configs/<key>` | PATCH/PUT | Cập nhật cấu hình |
| `POST /api/admin/configs` | POST | Tạo cấu hình mới |
| `DELETE /api/admin/configs/<key>` | DELETE | Xóa cấu hình |

### 4.3 Staff API (yêu cầu role STAFF hoặc ADMIN)

| Endpoint | Method | Mô tả |
|----------|--------|--------|
| `GET /api/transactions` | GET | Danh sách giao dịch (filter theo status, type) |
| `PUT /api/transactions/<id>/approve` | PUT | Duyệt giao dịch PENDING → thực thi nghiệp vụ |
| `PUT /api/transactions/<id>/reject` | PUT | Từ chối giao dịch PENDING |
| `GET /api/savings-accounts` | GET | Tất cả sổ tiết kiệm (BM4), trigger auto-rollover |
| `GET /api/reports/daily-activity` | GET | Báo cáo hoạt động theo ngày (BM5.1) |
| `GET /api/reports/monthly-open-close` | GET | Báo cáo mở/đóng theo tháng (BM5.2) |
| `GET /api/staff/analytics` | GET | Phân tích xu hướng: biểu đồ gửi/rút/mở mới theo ngày |

### 4.4 Client API (yêu cầu role CUSTOMER)

| Endpoint | Method | Mô tả |
|----------|--------|--------|
| `GET /api/client/me` | GET | Thông tin cá nhân (kèm wallet_balance) |
| `PATCH /api/client/me` | PATCH | Cập nhật địa chỉ |
| `GET /api/client/dashboard` | GET | Dashboard: ví, số dư khả dụng, lãi ước tính, sổ gần đây |
| `GET /api/client/savings-products` | GET | Danh sách sản phẩm đang hoạt động |
| `GET /api/client/savings-accounts` | GET | Sổ tiết kiệm của user (kèm auto-rollover) |
| `GET /api/client/savings-accounts/<id>` | GET | Chi tiết sổ + ước tính lãi |
| `POST /api/client/open-savings` | POST | Tạo yêu cầu mở sổ (PENDING) |
| `POST /api/client/savings-accounts/<id>/deposit-requests` | POST | Tạo yêu cầu gửi thêm (PENDING) |
| `POST /api/client/savings-accounts/<id>/withdraw-requests` | POST | Tạo yêu cầu rút một phần (PENDING, chỉ không kỳ hạn) |
| `POST /api/client/close-savings/<id>` | POST | Tạo yêu cầu tất toán (PENDING) |
| `POST /api/client/transfers` | POST | Chuyển khoản (thực thi ngay, không qua duyệt) |
| `GET /api/client/transactions` | GET | Lịch sử giao dịch cá nhân |

### 4.5 Real-time Events (SSE)

| Endpoint | Method | Mô tả |
|----------|--------|--------|
| `GET /api/events?token=<jwt>` | GET | Kết nối SSE, nhận thông báo real-time |

**Đặc điểm:**
- Pub/sub: `publish_event(event_type, message, roles, user_ids, payload)`
- Lọc theo role và user_id
- Keepalive mỗi 25 giây
- Hàng đợi tối đa 50 sự kiện/subscriber

---

## 5. Frontend

### 5.1 Admin SPA

**Công nghệ:** React 18 + Vite + React Router v7 + Axios + Chart.js

**Các trang:**

| Trang | Route | Chức năng |
|-------|-------|-----------|
| Login | `/login` | Đăng nhập/Đăng ký (tab switch), tự redirect theo role |
| Dashboard | `/admin` | 8 thẻ thống kê (khách hàng, nhân viên, sổ tiết kiệm, tiền gửi, giao dịch chờ, sản phẩm, tài khoản khóa). Auto-refresh qua SSE |
| User Management | `/admin/users` | Bảng users: filter role/status, search, tạo user mới, modal chi tiết (kèm sổ tiết kiệm), đổi role inline, khóa/mở khóa |
| Savings Products | `/admin/savings-products` | CRUD sản phẩm: tạo, sửa inline, bật/tắt hoạt động |
| System Configs | `/admin/configs` | CRUD cấu hình: tạo, sửa, xóa (có xác nhận) |
| Reports | `/admin/reports` | BM5.1 (hoạt động ngày) + BM5.2 (mở/đóng tháng) song song, filter ngày/tháng. Auto-refresh 12s + SSE |

**Component nổi bật:**
- `ProtectedRoute`: Kiểm tra JWT hợp lệ + role, redirect khi hết hạn
- `AdminLayout`: Sidebar 5 mục, kết nối SSE, toast notification
- Axios interceptor: Tự gắn JWT từ localStorage, redirect login khi nhận 401

### 5.2 Client SPA (Customer)

**Công nghệ:** HTML/CSS/JS thuần, single-file (~3476 dòng), Chart.js cho biểu đồ

**Các trang (tab navigation):**

| Trang | Chức năng |
|-------|-----------|
| **Home (Dashboard)** | Hiển thị số dư ví, số dư khả dụng, tiền đang chờ duyệt, số sổ hoạt động. Quick actions: chuyển khoản, mở sổ, refresh. Preview 2 sổ gần đây, 4 giao dịch gần đây |
| **Savings** | Danh sách sản phẩm, form mở sổ (chọn sản phẩm + nhập số tiền), danh sách sổ tiết kiệm kèm nút hành động (gửi thêm, rút, tất toán). Mỗi sổ có biểu đồ tăng trưởng SVG |
| **Transfer** | Form chuyển khoản: nhập số tài khoản người nhận, số tiền, ghi chú |
| **Transactions** | Lịch sử giao dịch đầy đủ kèm badge trạng thái (PENDING/APPROVED/REJECTED) |
| **Profile** | Thông tin cá nhân: tên, email, số tài khoản, CMND, ví, lãi ước tính, tổng giá trị tiết kiệm |
| **Simulator** | Mô phỏng tiết kiệm với Chart.js: điều chỉnh vốn, kỳ hạn, lãi suất, số năm, tùy chọn rollover. Hiển thị bảng chi tiết từng kỳ và biểu đồ tăng trưởng |

**Tính năng nổi bật:**
- Real-time SSE với hiệu ứng chuông thông báo
- Panel thông báo (6 giao dịch gần nhất, badge PENDING)
- Ẩn/hiện số dư (toggle balance visibility)
- Bảo vệ XSS qua hàm `escapeHtml()`
- Kiểm tra JWT hết hạn khi load trang

### 5.3 Staff SPA

**Công nghệ:** HTML/CSS/JS thuần, single-file (~920 dòng), Chart.js

**Giao diện:** Neo-brutalist style (viền đen dày, box-shadow, grid background)

**Các trang:**

| Trang | Chức năng |
|-------|-----------|
| **Dashboard** | 4 thẻ tổng quan (giao dịch chờ, khách hàng, sổ tiết kiệm, tổng tiền gửi). Bảng 8 giao dịch PENDING mới nhất kèm nút duyệt/từ chối |
| **Transactions** | Danh sách đầy đủ, filter theo status và type. Duyệt/từ chối có modal xác nhận |
| **Customers** | Bảng khách hàng: ID, tên, email, CMND, địa chỉ, trạng thái, ngày tạo |
| **Accounts (BM4)** | Tất cả sổ tiết kiệm kèm ngày đáo hạn và thời gian đã gửi |
| **Reports (BM5)** | BM5.1 + BM5.2 song song, filter ngày. Auto-poll mỗi 12s |
| **Analytics** | Dashboard xu hướng với Chart.js. Chọn tháng, 4 thẻ tổng (tổng gửi, rút, dòng ròng, sổ mới). 4 biểu đồ: gửi theo ngày, rút theo ngày, sổ mới theo ngày, tăng trưởng khách hàng theo ngày |

---

## 6. Business Logic & Quy tắc nghiệp vụ

### 6.1 Quy tắc hệ thống

| Mã | Quy tắc | Giá trị mặc định | Mô tả |
|----|---------|-----------------|--------|
| QD1 | `MIN_OPEN_AMOUNT` | 1,000,000 VND | Số tiền tối thiểu để mở sổ tiết kiệm |
| QD2 | `MIN_SAVINGS_DEPOSIT_AMOUNT` | 100,000 VND | Số tiền tối thiểu cho mỗi lần gửi thêm |
| QD3 | `NON_TERM_MIN_DAYS` | 15 ngày | Số ngày giữ tối thiểu cho sổ không kỳ hạn |

### 6.2 Công thức tính lãi

```
Tiền lãi = Số dư gốc × Lãi suất năm (%) / 100 × (Số ngày giữ / 365)
```

- Sử dụng ngày thực tế (365 ngày = 1 năm)
- 1 tháng = 30 ngày cho tính toán kỳ hạn

### 6.3 Quy tắc rút trước hạn

| Loại sổ | Điều kiện | Lãi suất áp dụng |
|---------|-----------|-----------------|
| Có kỳ hạn | Rút trước ngày đáo hạn | Lãi suất không kỳ hạn (0.5%/năm) |
| Có kỳ hạn | Rút đúng/sau ngày đáo hạn | Lãi suất sản phẩm (5.0% hoặc 5.5%) |
| Không kỳ hạn | Luôn luôn | Lãi suất sản phẩm (0.5%/năm) |

### 6.4 Quy tắc gửi thêm (QD2)

- **Sổ có kỳ hạn:** Chỉ được gửi thêm tại **ranh giới kỳ hạn** (khi `số ngày giữ >= số ngày kỳ hạn`)
- **Sổ không kỳ hạn:** Được gửi thêm bất cứ lúc nào

### 6.5 Quy tắc rút tiền

- **Sổ có kỳ hạn:** Phải tất toán toàn bộ (`CLOSE_SAVINGS`), không rút một phần
- **Sổ không kỳ hạn:** Được rút một phần, phải giữ tối thiểu `NON_TERM_MIN_DAYS` ngày

### 6.6 Auto-Rollover (Tự động tái tục)

- **Lazy evaluation:** Trigger khi xem chi tiết sổ hoặc danh sách sổ
- Khi sổ có kỳ hạn đáo hạn: lãi được cộng dồn vào gốc, `opened_at` reset về ngày tái tục
- Xử lý nhiều kỳ liên tiếp trong một lần kiểm tra (loop với giới hạn 100 vòng)
- Ghi nhận giao dịch `AUTO_ROLLOVER` với tổng lãi

### 6.7 Quy trình Maker/Checker (Duyệt giao dịch)

```
CUSTOMER tạo yêu cầu → Transaction PENDING
         │
         ▼
STAFF xem hàng đợi → Approve hoặc Reject
         │
    ┌────┴────┐
    │         │
APPROVED   REJECTED
    │
    ▼
Thực thi nghiệp vụ → Publish SSE events
    │
    ▼
CUSTOMER nhận thông báo real-time
```

**Ngoại lệ:**
- Chuyển khoản (`TRANSFER_OUT`/`TRANSFER_IN`): Thực thi ngay, không qua duyệt
- Nạp/rút ví: Đã tắt trong demo (trả về 410), thay bằng thưởng chào mừng

### 6.8 Số dư khả dụng (Available Balance)

```
Số dư khả dụng = wallet_balance - Σ(PENDING OPEN_SAVINGS + PENDING DEPOSIT_TO_SAVINGS)
```

Hệ thống trừ số tiền đang chờ duyệt khỏi số dư hiển thị, ngăn khách hàng chi tiêu kép (double-spending) số tiền đã cam kết cho yêu cầu đang chờ.

### 6.9 Phân quyền chi tiết

| Tính năng | CUSTOMER | STAFF | ADMIN |
|-----------|----------|-------|-------|
| Xem thông tin cá nhân | ✅ (của mình) | ❌ | ❌ |
| Xem wallet_balance | ✅ | ❌ | ❌ |
| Mở/Gửi/Rút/Tất toán sổ | ✅ (tạo request) | ✅ (duyệt) | ✅ (duyệt) |
| Chuyển khoản | ✅ (ngay lập tức) | ❌ | ❌ |
| Duyệt giao dịch | ❌ | ✅ | ✅ |
| Xem báo cáo BM5 | ❌ | ✅ | ✅ |
| Xem Analytics | ❌ | ✅ | ✅ |
| Quản lý users | ❌ | ❌ | ✅ |
| Quản lý sản phẩm | ❌ | ❌ | ✅ |
| Quản lý cấu hình | ❌ | ❌ | ✅ |
| Dashboard tổng quan | ❌ | ❌ | ✅ |

---

## 7. Test Cases

### 7.1 Integration Test (`test_flow.py`)

Luồng end-to-end tuyến tính:

| Step | Hành động | Kiểm tra |
|------|-----------|----------|
| 1 | Đăng ký khách hàng mới | Thành công |
| 2 | Đăng nhập | Nhận JWT |
| 3 | Kiểm tra ví | Số dư = 10,000,000 VND (welcome bonus) |
| 4 | Xem sản phẩm tiết kiệm | Tìm sản phẩm có kỳ hạn |
| 5 | Mở sổ tiết kiệm (2M) | Tạo giao dịch PENDING |
| 6 | Staff duyệt giao dịch | Status → APPROVED |
| 7 | Kiểm tra ví | Số dư = 8,000,000 VND |
| 8 | Ước tính lãi | Hiển thị lãi rút trước hạn |
| 9 | Tất toán sổ, Staff duyệt | Sổ CLOSED |
| 10 | Kiểm tra ví | Số dư = 8M + gốc 2M + lãi |

### 7.2 Comprehensive API Tests (`run_api_tests.py`)

#### Phase 1: Authentication & RBAC
| Test Case | Mô tả | Kết quả mong đợi |
|-----------|--------|-----------------|
| Đăng ký + Đăng nhập | Flow auth cơ bản | JWT trả về hợp lệ |
| Customer → Admin endpoint | Truy cập `/api/admin/dashboard` | 403 Forbidden |
| Customer → Staff endpoint | Truy cập `/api/transactions` | 403 Forbidden |
| Staff → Admin endpoint | Truy cập `/api/admin/users` | 403 Forbidden |

#### Phase 2: Chuyển khoản
| Test Case | Mô tả | Kết quả mong đợi |
|-----------|--------|-----------------|
| Chuyển khoản thường | Chuyển hợp lệ | Thành công, ví trừ đúng |
| Tự chuyển khoản | Chuyển cho chính mình | 400 Bad Request |
| Số tiền âm | amount < 0 | 400 Bad Request |
| Số tiền = 0 | amount = 0 | 400 Bad Request |
| Vượt số dư | amount > wallet_balance | 400 Bad Request |

#### Phase 5: Quy tắc nghiệp vụ
| Test Case | Mô tả | Kết quả mong đợi |
|-----------|--------|-----------------|
| QD1: Số tiền < MIN_OPEN_AMOUNT | Mở sổ với 500,000 VND | 400 Bad Request |
| QD2: Gửi thêm sổ có kỳ hạn | Gửi khi chưa đến ranh giới kỳ hạn | 400 Bad Request |
| QD3: Rút một phần sổ có kỳ hạn | Withdraw từ sổ có kỳ hạn | 400 Bad Request |
| Rút trước hạn | Tất toán sổ không kỳ hạn < 15 ngày | 400 Bad Request |
| Tất toán sớm + phạt lãi | Close sổ có kỳ hạn trước đáo hạn | Áp dụng lãi suất không kỳ hạn |

#### Phase 7: Race Condition
| Test Case | Mô tả | Kết quả mong đợi |
|-----------|--------|-----------------|
| Double transfer đồng thời | 2 thread chuyển khoản cùng lúc | Chỉ 1 giao dịch thành công |

### 7.3 Playwright E2E Test (`frontend/tests/role-flow.spec.js`)

Single test case (timeout 90s):

| Step | Hành động | Kiểm tra |
|------|-----------|----------|
| 1 | Đăng ký khách hàng qua UI | Redirect thành công |
| 2 | Login customer | Redirect tới `/client/` |
| 3 | Mở sổ tiết kiệm | Transaction PENDING xuất hiện |
| 4 | Logout, login staff | Redirect tới `/staff/` |
| 5 | Duyệt giao dịch PENDING | Status thay đổi |
| 6 | Logout, login customer | Sổ hiện trong danh sách |
| 7 | Logout, login admin | Dashboard hiện, navigate được |
| 8 | Assert | Không có JS error, không có network request lỗi |

### 7.4 Các trường hợp CHƯA được test

| Nhóm | Chi tiết |
|------|----------|
| Unit tests | Hàm tính lãi, auto-rollover, kiểm tra đáo hạn trong `savings_rules.py` |
| SSE | Real-time events, keepalive, reconnect |
| Auth | Forgot-password flow |
| Admin | CRUD user, đổi role, khóa/mở khóa, CRUD sản phẩm, CRUD cấu hình |
| Báo cáo | BM5 với filter ngày/tháng, analytics endpoint |
| Frontend | Simulator, profile update, JWT hết hạn trên UI |
| Logic | Available balance reservation, auto-rollover behavior |

---

## 8. Đánh giá & Hạn chế

### 8.1 Điểm mạnh

| Điểm | Chi tiết |
|------|----------|
| **Kiến trúc rõ ràng** | Tách biệt 3 blueprint (admin/staff/client), common layer dùng chung |
| **Maker/Checker pattern** | Quy trình duyệt giao dịch 2 bước, đảm bảo an toàn |
| **Real-time** | SSE cho thông báo tức thì, auto-refresh dashboard |
| **Config-driven** | Business rules lưu trong DB, admin thay đổi được qua API |
| **Auto-migration** | Tự động thêm cột thiếu khi khởi động, không cần migration script |
| **Security** | JWT auth, parameterized SQL, XSS protection (escapeHtml), wallet_balance không lộ cho staff/admin |
| **UX** | 3 giao diện riêng biệt phù hợp từng vai trò, simulator tiết kiệm hữu ích |

### 8.2 Hạn chế & Đề xuất cải thiện

| Vấn đề | Chi tiết | Đề xuất |
|--------|----------|---------|
| **Single-threaded Flask** | Dev server đơn luồng, race condition test không chính xác | Dùng Gunicorn/uWSGI cho production |
| **Client/Staff SPA đơn file** | ~3476 và ~920 dòng HTML inline, khó maintain | Tách thành component, dùng bundler |
| **Không có unit test** | Chỉ có integration/E2E, thiếu unit test cho business logic | Thêm pytest cho `savings_rules.py`, `auth.py` |
| **DB connection per request** | Client module tạo connection riêng mỗi request | Dùng connection pool hoặc shared proxy như các module khác |
| **JWT hardcoded secret** | `SECRET_KEY` mặc định là chuỗi tiếng Việt hardcode | Bắt buộc env var, refuse start nếu thiếu |
| **Không có pagination** | API trả toàn bộ data, không phân trang | Thêm `limit`/`offset` cho list endpoints |
| **Không có rate limiting** | Không giới hạn request | Thêm Flask-Limiter |
| **Auto-rollover lazy** | Chỉ trigger khi có người xem, không có background job | Thêm cron job hoặc scheduler |

---

*Report generated: 2026-05-31*
