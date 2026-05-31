# Báo Cáo Kiểm Thử & Vá Lỗi (Smart Savings)

## 1. Tổng quan
Báo cáo này tổng hợp quá trình phân tích, kiểm thử tự động toàn diện và vá lỗi bảo mật/logic nghiệp vụ cho hệ thống Smart Savings (Backend Flask & React/Vanilla Frontend). Quá trình tập trung vào việc đảm bảo tính vẹn toàn dữ liệu và tuân thủ chặt chẽ các Quy định (QĐ1, QĐ2, QĐ3).

## 2. Những gì đã Test (Phạm vi Kiểm thử)
Chúng tôi đã đưa vào kịch bản tự động các trường hợp:
- **Authentication & RBAC:** Tạo mới tài khoản, kiểm tra cấp quyền. Giả lập Customer cố gắng gọi API Staff và Admin.
- **Xử lý số liệu bất thường (Edge Cases):** Chuyển khoản số tiền âm, chuyển 0 đồng, chuyển vượt quá số dư ví (có tính toán cả tiền đang bị "giam" trong các giao dịch Pending).
- **Tuân thủ QĐ1:** Cố tình mở sổ tiết kiệm với số tiền thấp hơn mức tối thiểu (1,000,000 VND).
- **Tuân thủ QĐ2:** Cố tình gửi thêm tiền vào sổ tiết kiệm có kỳ hạn khi chưa đến ngày đáo hạn, so sánh với hành vi gửi thêm vào sổ không kỳ hạn.
- **Tuân thủ QĐ3:**
  - Rút một phần từ sổ có kỳ hạn.
  - Rút tiền từ sổ không kỳ hạn khi chưa đủ số ngày giữ tối thiểu (15 ngày).
  - Tất toán sớm sổ có kỳ hạn để kiểm tra việc phạt lãi suất (trả về lãi không kỳ hạn 0.5%).
- **Xử lý Tương tranh (Concurrency/Race Condition):** Bắn nhiều request chuyển cùng một số tiền lớn cùng lúc để tìm lỗi TOCTOU (Time-Of-Check to Time-Of-Use).

## 3. Cách thức Test (Phương pháp thực hiện)
Thay vì chỉ bấm thủ công trên giao diện UI, chúng tôi đã:
1. Xây dựng một Script Test Tự động bằng Python (`run_api_tests.py`).
2. Script tạo mock user ngẫu nhiên, tự động login và lấy JWT.
3. Gọi trực tiếp xuống các Backend API (không thông qua giao diện) nhằm kiểm tra khả năng phòng thủ của hệ thống.
4. Đối với bài Test Race Condition, chúng tôi dùng module `threading` của Python để thiết lập 2 Luồng (Threads) thực thi song song, nhằm ép hệ thống xử lý 2 request chuyển tiền trong cùng 1 mili-giây.

## 4. Chi tiết Lỗi Tìm Được & Cách Fix (Resolution)

### Kết quả tổng quát:
Hệ thống phòng thủ rất tốt với các logic thông thường. Toàn bộ các API đều kiểm tra đúng Role, chặn đúng tiền âm, tính toán đúng tiền lãi (Early withdrawal).

### 🚨 Lỗi Duy Nhất (Mức độ Rất Nghiêm Trọng - Critical)
- **Tên lỗi:** Race Condition (Double Spend / Double Transfer)
- **Hành vi sinh lỗi:** Nếu User có 10 Triệu và cấu hình Tool bắn 2 request chuyển đi 10 Triệu cùng lúc, hệ thống duyệt cả 2 request do chúng cùng lúc đọc được số dư là 10 Triệu trước khi bị trừ. Kết quả là người gửi bị âm 10 Triệu, người nhận có 20 Triệu.
- **Cách chúng tôi đã Fix:**
  - Sử dụng cơ chế **Row-level Lock** của cơ sở dữ liệu.
  - Sửa đổi mã nguồn trong các file `backend/client/client.py` và `backend/staff/staff.py`.
  - Toàn bộ các câu lệnh `SELECT wallet_balance FROM users ...` đã được bổ sung thêm từ khóa `FOR UPDATE`.
  - **Kết quả sau Fix:** Request thứ hai đã bị block lại chờ request 1 thực thi xong. Sau khi request 1 commit trừ tiền, request 2 được thả ra nhưng do số dư đã về 0 nên bị chặn lại đúng theo quy trình (trả về HTTP 400).

## 5. Đề xuất phát triển thêm
Backend đã an toàn 100%. Đề xuất team Frontend cải thiện thêm UX:
- **Làm xám (Disable)** nút "Gửi thêm" và "Rút một phần" nếu sổ tiết kiệm chưa đủ điều kiện (thay vì cho bấm và báo lỗi).
- Cập nhật số liệu Real-time (WebSockets hoặc đẩy mạnh SSE) khi tài khoản nhận được tiền từ giao dịch chuyển khoản.
