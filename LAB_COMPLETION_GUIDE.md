# Smart Savings - Hoàn thiện lab quản lý sổ tiết kiệm

## 1. Nội dung đã hoàn thiện

Hệ thống đã được chỉnh lại theo trọng tâm đề tài quản lý sổ tiết kiệm:

- Bổ sung quy định mở sổ tối thiểu `MIN_OPEN_AMOUNT = 1.000.000`.
- Bổ sung quy định gửi thêm tối thiểu `MIN_SAVINGS_DEPOSIT_AMOUNT = 100.000`.
- Bổ sung quy định sổ không kỳ hạn phải giữ tối thiểu `NON_TERM_MIN_DAYS = 15`.
- Chuyển luồng mở sổ sang dạng yêu cầu `PENDING`; Staff/Admin duyệt thì sổ mới được tạo.
- Thêm giao dịch `DEPOSIT_TO_SAVINGS` để gửi thêm tiền vào sổ.
- Thêm giao dịch `WITHDRAW_FROM_SAVINGS` để rút một phần từ sổ không kỳ hạn.
- Sửa tất toán sổ để tính lãi, cộng gốc + lãi vào ví và đóng sổ.
- Thêm báo cáo BM5.1 doanh số hoạt động ngày.
- Thêm báo cáo BM5.2 mở/đóng sổ tháng.
- Cập nhật Admin UI để duyệt các loại giao dịch mới và xem báo cáo.
- Thêm giao diện Staff độc lập tại `frontend/staff/index.html`.
- Cập nhật giao diện khách hàng HTML để gửi thêm, rút một phần và tất toán sổ.
- Tái cấu trúc giao diện theo design system Brutalism: chữ lớn, viền rõ, focus state rõ, màu token thống nhất và bố cục dashboard chuyên nghiệp hơn.

## 2. Quy trình nghiệp vụ hiện tại

Hệ thống đi theo mô hình maker-checker:

1. Khách hàng tạo yêu cầu giao dịch.
2. Giao dịch được lưu ở trạng thái `PENDING`.
3. Staff hoặc Admin kiểm tra và bấm duyệt/từ chối.
4. Khi duyệt, hệ thống mới cập nhật ví, sổ tiết kiệm, tiền gốc, tiền lãi và trạng thái giao dịch.

Các giao dịch đang hỗ trợ:

- `DEPOSIT_TO_WALLET`: nạp tiền vào ví, cần duyệt.
- `WITHDRAW_FROM_WALLET`: rút tiền khỏi ví, cần duyệt.
- `OPEN_SAVINGS`: mở sổ tiết kiệm, cần duyệt.
- `DEPOSIT_TO_SAVINGS`: gửi thêm vào sổ tiết kiệm, cần duyệt.
- `WITHDRAW_FROM_SAVINGS`: rút một phần từ sổ không kỳ hạn, cần duyệt.
- `CLOSE_SAVINGS`: tất toán sổ, cần duyệt.

## 3. Hướng dẫn Admin

Đăng nhập bằng tài khoản mặc định nếu chưa cấu hình khác:

- Email: `admin@gmail.com`
- Mật khẩu: `admin123`

Admin có thể:

- Xem dashboard tổng quan.
- Tạo tài khoản Staff/Admin/Customer.
- Khóa hoặc mở khóa tài khoản.
- Đổi role người dùng.
- Thêm, sửa, bật/tắt gói tiết kiệm.
- Cấu hình tham số hệ thống ở mục `Tham số Hệ thống`.
- Duyệt giao dịch ở mục `Duyệt giao dịch`.
- Xem báo cáo BM5 ở mục `Báo cáo BM5`.

Các tham số quan trọng:

- `MIN_OPEN_AMOUNT`: số tiền tối thiểu khi mở sổ.
- `MIN_SAVINGS_DEPOSIT_AMOUNT`: số tiền tối thiểu khi gửi thêm vào sổ.
- `NON_TERM_MIN_DAYS`: số ngày tối thiểu để rút sổ không kỳ hạn.

## 4. Hướng dẫn Staff

Staff dùng giao diện riêng tại `frontend/staff/index.html` để xử lý nghiệp vụ tại quầy.

Tài khoản Staff mặc định:

- Email: `staff@gmail.com`
- Mật khẩu: `staff123`

Staff có thể:

- Xem danh sách giao dịch chờ duyệt.
- Duyệt nạp/rút ví.
- Duyệt mở sổ.
- Duyệt gửi thêm vào sổ.
- Duyệt rút một phần từ sổ không kỳ hạn.
- Duyệt tất toán sổ.
- Xem danh sách khách hàng và sổ tiết kiệm.
- Xem báo cáo doanh số ngày và báo cáo mở/đóng sổ tháng.

Khi duyệt, hệ thống tự kiểm tra lại quy định để tránh yêu cầu đã cũ hoặc không còn hợp lệ.

## 5. Hướng dẫn Customer

Khách hàng có thể dùng giao diện `frontend/client/index.html` hoặc API:

- Đăng ký tài khoản.
- Đăng nhập.
- Xem thông tin cá nhân, số tài khoản và số dư ví.
- Tạo yêu cầu nạp tiền vào ví.
- Tạo yêu cầu rút tiền khỏi ví.
- Chuyển khoản sang khách hàng khác.
- Tạo yêu cầu mở sổ tiết kiệm.
- Gửi thêm vào sổ nếu đủ điều kiện.
- Rút một phần từ sổ không kỳ hạn nếu đã giữ đủ số ngày tối thiểu.
- Tất toán sổ khi đủ điều kiện.
- Xem lịch sử giao dịch và trạng thái duyệt.

## 6. Cách chạy hệ thống

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mysql -u root -p < smart_savings.sql
PYTHONPATH=backend python backend/app.py
```

Frontend Admin:

```bash
cd frontend
npm ci
npm run dev
```

Frontend Staff:

```bash
cd frontend/staff
python -m http.server 8010 --bind 127.0.0.1
```

Frontend Customer:

```bash
cd frontend/client
python -m http.server 8000 --bind 127.0.0.1
```

Mở:

- Backend: `http://localhost:5000/api/ping`
- Admin React: `http://localhost:5173`
- Staff Console: `http://localhost:8010`
- Customer App: `http://localhost:8000`

## 7. Ghi chú còn lại

Đây là bản hoàn thiện theo mục tiêu lab. Các phần có thể nâng cấp thêm nếu còn thời gian:

- Thêm test tự động cho backend.
- Thêm màn hình Staff riêng thay vì dùng chung màn hình Admin.
- Chuyển toàn bộ client HTML sang React để thống nhất frontend.
- Nâng cấp bảo mật quên mật khẩu bằng OTP/email thật.
- Tách migration database ra file riêng thay vì tự chỉnh schema khi app khởi động.
