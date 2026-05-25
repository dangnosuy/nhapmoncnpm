# Hướng dẫn sử dụng hệ thống quản lý sổ tiết kiệm

## 1. Mục đích hệ thống

Repo này là hệ thống quản lý sổ tiết kiệm theo mô hình ngân hàng số kết hợp nghiệp vụ tại quầy.

Hệ thống có 3 phân hệ:

- `CUSTOMER`: khách hàng đăng ký, nhận 100.000 VND demo ban đầu, chuyển khoản, gửi yêu cầu mở/gửi thêm/rút/tất toán sổ.
- `STAFF`: nhân viên xử lý hàng đợi giao dịch, duyệt/từ chối yêu cầu, tra cứu khách hàng và sổ.
- `ADMIN`: quản trị người dùng, gói tiết kiệm, tham số hệ thống, duyệt giao dịch và xem báo cáo.

Luồng nghiệp vụ chính là maker-checker:

1. Khách hàng tạo yêu cầu giao dịch.
2. Giao dịch được lưu trạng thái `PENDING`.
3. Staff/Admin duyệt hoặc từ chối bằng hộp xác nhận trong giao diện.
4. Khi duyệt, backend mới cập nhật ví, sổ tiết kiệm, tiền gốc/lãi và trạng thái giao dịch.

## 2. Yêu cầu môi trường

- Python 3.10+.
- Node.js 18+.
- MySQL.
- Trình duyệt không proxy `localhost`. Nếu dùng proxy/VPN/Clash/SwitchyOmega, thêm `localhost`, `127.0.0.1`, `::1` vào bypass/direct.

## 3. Cài đặt backend

Chạy từ thư mục root repo:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Khởi tạo database:

```bash
sudo mysql < smart_savings.sql
```

File SQL sẽ tạo database `modern_savings_db`, tạo user MySQL:

```text
User: smart_savings
Password: SmartSavings@2026!
Database: modern_savings_db
```

Kiểm tra kết nối DB:

```bash
mysql -u smart_savings -p'SmartSavings@2026!' -e "SELECT 1;"
```

## 4. Chạy hệ thống

Terminal 1, chạy backend:

```bash
PYTHONPATH=backend python backend/app.py
```

Backend chạy tại:

```text
http://127.0.0.1:5000
```

Smoke test:

```bash
curl --noproxy '*' http://127.0.0.1:5000/api/ping
```

Terminal 2, chạy frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend chạy tại:

```text
http://127.0.0.1:5173/login
```

Nếu trình duyệt báo lỗi Squid/proxy khi mở `localhost`, dùng:

```text
http://127.0.0.1:5173/login
```

## 5. Luồng đăng nhập và phân quyền

Tất cả người dùng bắt đầu ở:

```text
http://127.0.0.1:5173/login
```

Sau khi đăng nhập, hệ thống tự chuyển theo role:

- `ADMIN` -> `/admin`
- `STAFF` -> `/staff/`
- `CUSTOMER` -> `/client/`

Nếu truy cập sai phân hệ, hệ thống báo `Permission denied` và chuyển về đúng trang của role đó.

## 6. Tài khoản mặc định

Admin:

```text
admin@gmail.com
admin123
```

Staff:

```text
staff@gmail.com
staff123
```

Customer:

- Tạo tài khoản mới ở `/login`.
- Khách hàng mới được tặng `100.000 VND` vào ví.

## 7. Các màn hình chính

Admin:

- Dashboard tổng quan.
- Quản lý nhân sự.
- Duyệt giao dịch.
- Quản lý gói tiết kiệm.
- Quản lý tham số hệ thống.
- Báo cáo BM5.

Staff:

- Tổng quan hàng đợi.
- Duyệt giao dịch.
- Danh sách khách hàng.
- Danh sách sổ tiết kiệm.
- Báo cáo doanh số ngày và mở/đóng sổ tháng.

Customer:

- Tổng quan tài khoản.
- Chuyển khoản.
- Mở sổ tiết kiệm.
- Gửi thêm/rút một phần/tất toán sổ.
- Lịch sử giao dịch.
- Hồ sơ cá nhân.

Client không còn chức năng xin Admin/Staff nạp tiền vào ví. Luồng demo thực tế là khách hàng mới được tặng `100.000 VND`, sau đó dùng số dư ví để mở sổ hoặc chuyển khoản.

Giao diện Client dùng cùng phong cách brutalist với Staff/Admin: sidebar đen trên desktop, thanh điều hướng gọn trên màn nhỏ, từng chức năng là một màn riêng. Khi chọn `Chuyển khoản`, `Tiết kiệm`, `Lịch sử`, hệ thống chuyển panel ngay đầu màn hình thay vì cuộn xuống một section dài.

Ví khách hàng có 3 chỉ số cần phân biệt:

- `wallet_balance`: số dư ví thực tế trong database.
- `pending_reserved_amount`: số tiền đang được giữ cho yêu cầu mở sổ/gửi thêm vào sổ chờ duyệt.
- `available_wallet_balance`: số tiền còn được phép dùng để chuyển khoản hoặc tạo yêu cầu mới.

Ví dụ: khách có `100.000 VND`, tạo yêu cầu mở sổ `80.000 VND` thì trong lúc `PENDING`, `wallet_balance` vẫn là `100.000 VND` nhưng `available_wallet_balance` chỉ còn `20.000 VND`. Khi Staff duyệt, ví thực tế giảm còn `20.000 VND` và tiền gốc trong sổ tăng `80.000 VND`.

## 8. Quy định nghiệp vụ đang cấu hình

Các tham số nằm trong bảng `system_configs` và có thể sửa trong Admin:

- `MIN_OPEN_AMOUNT`: số tiền tối thiểu khi mở sổ, mặc định `50.000 VND`.
- `MIN_SAVINGS_DEPOSIT_AMOUNT`: số tiền tối thiểu khi gửi thêm vào sổ, mặc định `50.000 VND` để demo được với ví 100.000 VND ban đầu.
- `NON_TERM_MIN_DAYS`: số ngày tối thiểu để rút sổ không kỳ hạn.

Các gói tiết kiệm mặc định:

- Không kỳ hạn.
- Tiết kiệm 3 phút.
- Tiết kiệm 6 phút.

Lưu ý demo: cột backend vẫn tên `term_months` để tránh đổi schema, nhưng các giá trị kỳ hạn dương đang được hiểu là số phút demo. Quy đổi demo là `1 tháng = 1 phút`, nên `12 phút = 1 năm`. Ví dụ sổ 3 phút nhận lãi tương đương 3 tháng, sổ 6 phút nhận lãi tương đương 6 tháng nếu tất toán đúng kỳ.

Với quy định theo ngày, backend cũng dùng cùng thang demo: `30 ngày quy định = 1 phút`. Vì vậy sổ không kỳ hạn có `NON_TERM_MIN_DAYS = 15` sẽ được rút/tất toán sau khoảng `0.5 phút` trong môi trường demo.

## 9. API chính

Auth:

```text
POST /api/auth/login
POST /api/auth/register
POST /api/auth/forgot-password
```

Customer:

```text
GET  /api/client/me
GET  /api/client/dashboard
GET  /api/client/savings-products
GET  /api/client/savings-accounts
GET  /api/client/transactions
POST /api/client/transfers
POST /api/client/open-savings
POST /api/client/close-savings/:account_id
```

`POST /api/client/deposit-requests` và `POST /api/client/withdraw-requests` đã bị tắt ở backend để tránh mô hình "khách xin/rút tiền ví rồi admin duyệt tiền tự tăng/giảm". Dữ liệu test nên đi qua bonus đăng ký, chuyển khoản, mở sổ và tất toán.

Staff/Admin:

```text
GET   /api/transactions
PATCH /api/transactions/:transaction_id
GET   /api/users
GET   /api/savings-accounts
GET   /api/reports/daily-activity
GET   /api/reports/monthly-open-close
```

Admin:

```text
GET   /api/admin/dashboard
GET   /api/admin/users
POST  /api/admin/users
PATCH /api/admin/users/:user_id
GET   /api/admin/savings-products
POST  /api/admin/savings-products
PATCH /api/admin/savings-products/:product_id
GET   /api/admin/configs
POST  /api/admin/configs
PATCH /api/admin/configs/:config_key
DELETE /api/admin/configs/:config_key
```

## 10. Ghi chú phát triển

- Không commit `node_modules/`, `frontend/dist/`, `__pycache__/`.
- Khi đổi schema, kiểm tra kỹ `smart_savings.sql` vì file này drop và tạo lại database.
- Khi test UI, nên dọn dữ liệu test sau khi chạy để không còn gói/user rác.
- Giao diện web dùng toast/modal nội bộ, không dùng `alert`, `prompt`, `confirm` của trình duyệt.
