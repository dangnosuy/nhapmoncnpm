# Báo Cáo Lỗi & Hướng Dẫn Tinh Chỉnh (Smart Savings)

## 1. Kết quả kiểm thử tự động
Chúng tôi đã chạy hàng loạt các test tự động bao phủ các API Core theo Plan:
- ✅ **Authentication & Phân quyền (RBAC):** Hoạt động tốt. Customer không thể gọi API Admin/Staff và ngược lại.
- ✅ **Quy định 1 (Số tiền mở tối thiểu):** API chặn đúng các khoản tiền gửi dưới hạn mức (1M).
- ✅ **Quy định 2 (Gửi thêm):** API chặn gửi thêm nếu sổ có kỳ hạn chưa đến ngày đáo hạn. Sổ không kỳ hạn gửi bình thường.
- ✅ **Quy định 3 (Rút & Tất toán):**
  - Chặn rút 1 phần với sổ có kỳ hạn.
  - Áp dụng đúng lãi 0.5% khi tất toán sớm.
  - Chặn rút sổ không kỳ hạn nếu chưa qua số ngày tối thiểu (15 ngày).
- ❌ **Race Condition (Lỗ hổng kép):** Lỗi TOCTOU trong API Chuyển khoản (Concurrency Bug).

## 2. Chi tiết Lỗi (Bug Report)

### 🚨 BUG-001: Race Condition (Double Transfer / Double Spend)
- **Mức độ:** CRITICAL (Nghiêm trọng nhất - Ảnh hưởng trực tiếp đến tiền).
- **Mô tả:** Customer có 10,000,000 VND. Nếu dùng tool (như Postman hoặc 1 script Multi-threading) gửi đồng thời 2 request chuyển 10,000,000 VND cho một người khác. Hệ thống sẽ duyệt CẢ HAI request.
- **Hậu quả:** Người nhận có 20,000,000 VND. Người gửi bị âm tiền (-10,000,000 VND).
- **Phân tích nguyên nhân:** Cả 2 thread cùng đọc giá trị `wallet_balance = 10M` trước khi kịp cập nhật DB. Không có `FOR UPDATE` lock. 

## 3. Hướng dẫn tinh chỉnh (Tweaking Instructions)

### Bước 1: Vá lỗi Race Condition trong Backend
Mở file `backend/client/client.py`, tìm hàm `transfer_to_account_number`.

**Sửa Query lấy thông tin người gửi (dòng ~545):**
```python
# CŨ
cursor.execute("SELECT user_id, wallet_balance, full_name, account_number FROM users WHERE user_id = %s AND role = 'CUSTOMER'", (user_id,))

# MỚI (Thêm FOR UPDATE)
cursor.execute("SELECT user_id, wallet_balance, full_name, account_number FROM users WHERE user_id = %s AND role = 'CUSTOMER' FOR UPDATE", (user_id,))
```

*Lời khuyên:* Hãy search toàn bộ các query `SELECT wallet_balance` trong `create_open_savings_request`, `create_savings_deposit_request`, và `approve` của Staff, thêm `FOR UPDATE` vào tất cả các query này để lock row trong suốt quá trình transaction.

### Bước 2: Bảo vệ từ cấp Database
Chạy câu SQL sau để phòng hờ trường hợp code backend quên lock, database sẽ văng lỗi ngay lập tức nếu tiền bị âm:
```sql
ALTER TABLE users ADD CONSTRAINT check_wallet_positive CHECK (wallet_balance >= 0);
```

### Bước 3: Hoàn thiện UX cho Frontend
Dù backend chặn tốt, UI có thể cải thiện thêm:
1. Tại trang Sổ Tiết Kiệm (`frontend/client/index.html`), thay vì để User bấm nút "Gửi thêm" vào sổ chưa đáo hạn rồi nhận lỗi từ API, hãy **Disable (làm mờ)** nút "Gửi thêm" bằng JS nếu `is_matured == false`.
2. Tương tự, **Disable** nút "Rút một phần" đối với sổ không kỳ hạn nếu `days_held < min_days_hold` (15 ngày).

---
*Tài liệu này là kết quả của chiến dịch quét tự động các flow nghiệp vụ dựa trên `plan.md`.*
