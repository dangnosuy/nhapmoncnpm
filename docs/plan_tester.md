# Test Plan — Smart Savings Web Application

## Mục lục

1. [Tổng quan chiến lược](#1-tổng-quan-chiến-lược)
2. [Môi trường & chuẩn bị](#2-môi-trường--chuẩn-bị)
3. [Phase 1 — Authentication & Authorization](#3-phase-1--authentication--authorization)
4. [Phase 2 — Customer Flows](#4-phase-2--customer-flows)
5. [Phase 3 — Staff Flows](#5-phase-3--staff-flows)
6. [Phase 4 — Admin Flows](#6-phase-4--admin-flows)
7. [Phase 5 — Business Rules (QD1, QD2, QD3)](#7-phase-5--business-rules-qd1-qd2-qd3)
8. [Phase 6 — Cross-role Integration](#8-phase-6--cross-role-integration)
9. [Phase 7 — Edge Cases & Security](#9-phase-7--edge-cases--security)
10. [Phase 8 — UI/UX & Responsive](#10-phase-8--uiux--responsive)
11. [Tại sao plan này được thiết kế như vậy](#11-tại-sao-plan-này-được-thiết-kế-như-vậy)

---

## 1. Tổng quan chiến lược

### Tại sao cần plan này?

Hệ thống hiện tại có **3 SPA riêng biệt** (Admin React, Staff vanilla JS, Customer vanilla JS) cùng chia sẻ **1 backend Flask** với **~40 API endpoints**. Test hiện tại chỉ cover:

- ✅ Đăng ký + đăng nhập Customer
- ✅ Mở sổ tiết kiệm (1 loại, 1 lần)
- ✅ Staff duyệt 1 giao dịch
- ✅ Admin điều hướng qua các trang

**Chưa được test (20+ flows quan trọng):**

- ❌ Chuyển khoản giữa customers
- ❌ Gửi thêm tiền vào sổ tiết kiệm
- ❌ Rút một phần (non-term)
- ❌ Tất toán sổ (term + non-term)
- ❌ Staff từ chối giao dịch
- ❌ Auto-rollover khi sổ đáo hạn
- ❌ Admin CRUD users / products / configs
- ❌ Báo cáo BM5.1, BM5.2
- ❌ Kiểm tra business rules (số tiền tối thiểu, ngày giữ tối thiểu, lãi suất)
- ❌ Bảo mật (JWT, RBAC bypass, SQL injection, XSS)
- ❌ Race conditions (double-submit, concurrent approval)

### Phương pháp test

```
Phase 1-4: Test từng role riêng lẻ (đơn vị)
Phase 5:   Test business rules (logic nghiệp vụ)
Phase 6:   Test luồng xuyên suốt giữa các role (tích hợp)
Phase 7:   Test edge cases & bảo mật
Phase 8:   Test UI/UX
```

Lý do sắp xếp theo thứ tự này: **Phải đảm bảo từng role hoạt động đúng trước**, rồi mới test tương tác giữa các role. Nếu test tích hợp fail, ta cần biết lỗi ở role nào — không thể biết nếu chưa test riêng lẻ.

---

## 2. Môi trường & chuẩn bị

### 2.1 Khởi động hệ thống

```bash
# Terminal 1 — Database
mysql -u root -p < smart_savings.sql
mysql -u root -p modern_savings_db < seed_mock_data.sql   # (optional, cho dữ liệu mẫu)

# Terminal 2 — Backend
cd backend && source ../.venv/bin/activate && python app.py
# Verify: curl http://localhost:5000/api/ping → "pong 🏓"

# Terminal 3 — Frontend
cd frontend && npm run dev
# Verify: mở http://localhost:5173/login
```

### 2.2 Tài khoản test mặc định

| Role | Email | Password | Ghi chú |
|------|-------|----------|---------|
| ADMIN | admin@gmail.com | admin123 | Auto-created mỗi lần server start |
| STAFF | staff@gmail.com | staff123 | Auto-created mỗi lần server start |
| CUSTOMER | (đăng ký mới) | — | Wallet = 10,000,000 VND khi đăng ký |

### 2.3 Quy ước ghi kết quả

Mỗi test case sẽ ghi:
- **[PASS]** — Hoạt động đúng
- **[FAIL]** — Lỗi, kèm mô tả bug
- **[SKIP]** — Không test được (ghi lý do)

---

## 3. Phase 1 — Authentication & Authorization

> **Mục tiêu:** Đảm bảo hệ thống xác thực và phân quyền hoạt động chính xác. Đây là nền tảng — nếu auth sai, mọi test sau đều vô nghĩa.

### TC-1.1: Đăng ký tài khoản Customer

**Tại sao test này quan trọng:** Đây là entry point duy nhất cho customer mới. Nếu đăng ký lỗi, không ai dùng được hệ thống.

| # | Bước | Hành động | Kết quả mong đợi |
|---|------|-----------|-------------------|
| a | Happy path | Đăng ký với email mới, đầy đủ thông tin (full_name, identity_card, email, password, confirm_password) | 201, nhận account_number 10 chữ số, wallet_balance = 10,000,000 |
| b | Email trùng | Đăng ký lại cùng email | 400, thông báo lỗi email đã tồn tại |
| c | CMND trùng | Đăng ký email mới nhưng cùng identity_card | 400, thông báo lỗi CMND đã tồn tại |
| d | Thiếu trường bắt buộc | Bỏ trống email hoặc password hoặc full_name | 400, thông báo thiếu thông tin |
| e | Password không khớp | Nhập confirm_password khác password | Toast lỗi phía client (không gọi API) |
| f | Email format sai | Nhập "abc" vào trường email | HTML validation chặn hoặc API trả 400 |

### TC-1.2: Đăng nhập

| # | Bước | Hành động | Kết quả mong đợi |
|---|------|-----------|-------------------|
| a | Customer login | Đăng nhập bằng tài khoản vừa đăng ký | Redirect đến /client/, thấy trang chủ |
| b | Staff login | Đăng nhập staff@gmail.com / staff123 | Redirect đến /staff/, thấy dashboard |
| c | Admin login | Đăng nhập admin@gmail.com / admin123 | Redirect đến /admin, thấy dashboard |
| d | Sai password | Đăng nhập đúng email, sai password | 401, thông báo lỗi |
| e | Email không tồn tại | Đăng nhập email chưa đăng ký | 404, thông báo không tìm thấy |
| f | Tài khoản bị khóa | Đăng nhập tài khoản có status=LOCKED | 403, thông báo bị khóa |

### TC-1.3: Quên mật khẩu

| # | Bước | Hành động | Kết quả mong đợi |
|---|------|-----------|-------------------|
| a | Happy path | Nhập đúng email + identity_card + new_password (≥6 ký tự) | 200, đổi mật khẩu thành công |
| b | CMND sai | Đúng email, sai identity_card | 404, không tìm thấy |
| c | Mật khẩu quá ngắn | new_password < 6 ký tự | 400, mật khẩu quá ngắn |
| d | Đăng nhập lại | Sau khi đổi, đăng nhập bằng mật khẩu mới | Đăng nhập thành công |

### TC-1.4: Phân quyền route (RBAC)

**Tại sao test này quan trọng:** Nếu Customer truy cập được /admin hoặc /staff, đó là lỗ hổng bảo mật nghiêm trọng.

| # | Bước | Hành động | Kết quả mong đợi |
|---|------|-----------|-------------------|
| a | Customer → /admin | Đăng nhập Customer, gõ URL /admin | Redirect về /client/ hoặc /login |
| b | Customer → /staff | Đăng nhập Customer, gõ URL /staff/ | Redirect về /client/ hoặc /login |
| c | Staff → /admin | Đăng nhập Staff, gõ URL /admin | Redirect về /staff/ hoặc /login |
| d | Staff → /client | Đăng nhập Staff, gõ URL /client/ | Redirect về /staff/ hoặc /login |
| e | Admin → /client | Đăng nhập Admin, gõ URL /client/ | Redirect về /admin hoặc /login |
| f | Không token → /admin | Xóa localStorage, truy cập /admin | Redirect về /login |
| g | Token hết hạn | Dùng token expired | Redirect về /login, xóa localStorage |

### TC-1.5: API Authorization

| # | Bước | Hành động | Kết quả mong đợi |
|---|------|-----------|-------------------|
| a | No token | GET /api/admin/dashboard (không header) | 401 |
| b | Customer token → Admin API | GET /api/admin/dashboard với token Customer | 403 |
| c | Customer token → Staff API | PATCH /api/transactions/1 với token Customer | 403 |
| d | Staff token → Admin API | POST /api/admin/users với token Staff | 403 |
| e | Staff token → Client API | GET /api/client/me với token Staff | 403 |

---

## 4. Phase 2 — Customer Flows

> **Mục tiêu:** Test tất cả tính năng Customer có thể sử dụng. Customer là role chính — 80% giá trị business nằm ở đây.

### TC-2.1: Xem thông tin cá nhân (Profile)

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Vào trang Profile | Thấy: email, full_name, identity_card, account_number, wallet_balance |
| b | Cập nhật địa chỉ | PATCH /api/client/me → địa chỉ mới hiện đúng |
| c | Wallet balance hiển thị | Số tiền hiện đúng 10,000,000 cho tài khoản mới |

### TC-2.2: Dashboard

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Xem dashboard | Thấy: wallet_balance, tổng tiền tiết kiệm, tổng tài sản, pending transactions |
| b | Toggle ẩn/hiện số dư | Click nút mắt → hiện "*** *** VND", click lại → hiện số thật |
| c | Quick actions | Thấy 3 nút: Chuyển khoản, Mở sổ, Làm mới |

### TC-2.3: Chuyển khoản (Transfer)

**Tại sao test kỹ:** Transfer là thao tác tức thì (không cần staff duyệt), nên bug ở đây = mất tiền ngay lập tức.

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Chuyển khoản hợp lệ | Nhập account_number người nhận + amount > 0 | 201, 2 transactions (TRANSFER_OUT + TRANSFER_IN) tạo ngay với status APPROVED |
| b | Kiểm tra số dư sau chuyển | Sender: wallet giảm đúng amount. Receiver: wallet tăng đúng amount |
| c | Chuyển cho chính mình | Nhập account_number của chính mình | 400 |
| d | Chuyển vượt số dư | amount > wallet_balance | Lỗi không đủ tiền |
| e | Chuyển vượt available balance | Có pending OPEN_SAVINGS 5M, wallet = 10M, chuyển 6M | Lỗi (available = 10M - 5M = 5M) |
| f | Account number không tồn tại | Nhập số tài khoản bịa | 404 |
| g | Chuyển cho Staff/Admin | Nhập account_number của Staff | 400 (phải là CUSTOMER) |
| h | Amount = 0 | Nhập amount = 0 | Lỗi client-side hoặc 400 |
| i | Amount âm | Nhập amount = -1000 | Lỗi |
| j | SSE notification | Sau khi chuyển, receiver có nhận SSE event không? | Receiver nhận toast notification |

### TC-2.4: Mở sổ tiết kiệm (Open Savings)

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Mở sổ không kỳ hạn | Chọn "Không kỳ hạn" + amount = 1,000,000 | 201, transaction PENDING |
| b | Mở sổ 3 tháng | Chọn "3 tháng" + amount = 2,000,000 | 201, transaction PENDING |
| c | Amount < MIN_OPEN_AMOUNT | Mở sổ với 500,000 (< 1,000,000 mặc định) | 400, thông báo số tiền tối thiểu |
| d | Amount đúng bằng MIN | Mở sổ với đúng 1,000,000 | 201, thành công |
| e | Không đủ wallet balance | Wallet = 2M, mở sổ 3M | Lỗi không đủ tiền |
| f | Không đủ available balance | Wallet = 10M, đã có pending 9M, mở thêm 2M | Lỗi (available = 1M) |
| g | Product không active | Nếu Admin deactivate product, Customer mở sổ | 400, product không available |
| h | Chọn product rồi kiểm tra thông tin | Chọn product → hiển thị lãi suất, kỳ hạn | Thông tin đúng với DB |
| i | SSE event đến Staff | Sau khi mở sổ, Staff nhận SSE notification? | Staff thấy toast + pending queue update |

### TC-2.5: Gửi thêm tiền vào sổ (Deposit to Savings)

**Tại sao test kỹ:** QD2 quy định chỉ được gửi thêm khi sổ term đã đáo hạn. Logic này dễ sai.

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Gửi thêm vào sổ không kỳ hạn (ACTIVE) | Nhập amount ≥ 100,000 | 201, PENDING transaction |
| b | Amount < MIN_SAVINGS_DEPOSIT_AMOUNT | Gửi thêm 50,000 (< 100,000 mặc định) | 400 |
| c | Gửi thêm vào sổ term chưa đáo hạn | Sổ 3 tháng mới mở, gửi thêm | 400, phải đợi đáo hạn |
| d | Gửi thêm vào sổ term đã đáo hạn | Sổ 3 tháng đã đáo hạn, gửi thêm | 201 |
| e | Sổ đã CLOSED | Gửi thêm vào sổ đã tất toán | 400 |
| f | Sổ có pending transaction khác | Đã có 1 pending DEPOSIT, gửi thêm 1 cái nữa | 400, block vì đã có pending |
| g | Không đủ available wallet | Gửi thêm vượt available balance | Lỗi |

### TC-2.6: Rút một phần (Withdraw from Savings — chỉ non-term)

**Tại sao test kỹ:** Chỉ non-term mới được rút một phần, term phải tất toán. Logic lãi suất cũng phức tạp.

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Rút từ sổ không kỳ hạn | amount ≤ principal, đã giữ ≥ min_days | 201, PENDING, kèm interest_amount |
| b | Rút từ sổ term | Cố rút một phần từ sổ 3 tháng | 400, phải dùng tất toán |
| c | Rút > principal_balance | amount vượt số dư sổ | 400 |
| d | Rút khi chưa đủ ngày giữ | Sổ mới mở (< 15 ngày), rút | 400, chưa đủ ngày giữ tối thiểu |
| e | Rút hết = principal | Rút toàn bộ principal_balance | 201, PENDING, sổ sẽ CLOSED khi approved |
| f | Có pending transaction trên sổ | Đã có pending, rút tiếp | 400 |
| g | UI: nút "Rút một phần" | Nút chỉ hiện cho sổ non-term ACTIVE | Đúng, không hiện cho term accounts |

### TC-2.7: Tất toán sổ tiết kiệm (Close Savings)

**Tại sao test kỹ:** Tất toán liên quan đến QD3 — lãi suất phụ thuộc đáo hạn hay chưa. Bug ở đây = tính sai tiền lãi.

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Tất toán sổ non-term (đủ ngày giữ) | Sổ non-term, held ≥ 15 ngày | 201, PENDING, interest = principal × rate × days/365 |
| b | Tất toán sổ non-term (chưa đủ ngày giữ) | Sổ non-term, held < 15 ngày | 400 |
| c | Tất toán sổ term ĐÃ đáo hạn | Sổ 3 tháng, held ≥ 90 ngày | 201, lãi suất = rate gốc (ví dụ 5%) |
| d | Tất toán sổ term CHƯA đáo hạn | Sổ 3 tháng, held < 90 ngày | 201, lãi suất = non-term rate (0.5%), is_early_withdrawal = true |
| e | Hiển thị early withdrawal warning | Tất toán sớm → UI có cảnh báo? | Có thông báo "rút trước hạn" + lãi suất giảm |
| f | Đã có pending CLOSE | Tất toán lần 2 trên cùng sổ | 400 |
| g | Đã có pending operation khác | Có pending DEPOSIT, tất toán | 400 |
| h | Sổ đã CLOSED | Tất toán sổ đã closed | 400 |

### TC-2.8: Xem sổ tiết kiệm

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Danh sách sổ tiết kiệm | Vào tab "Sổ tiết kiệm" | Thấy tất cả sổ ACTIVE + CLOSED |
| b | Chi tiết 1 sổ | Click vào 1 sổ | Thấy: principal, rate, opened_at, maturity_date, interest estimate |
| c | Ước tính lãi | GET estimate-interest | Trả về applicable_rate, interest_amount, total_receive |
| d | Filter theo status | Lọc ACTIVE / CLOSED | Kết quả đúng |
| e | Auto-rollover display | Sổ term đáo hạn → principal cập nhật? | Khi GET, backend tự compound interest |

### TC-2.9: Xem lịch sử giao dịch

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Danh sách giao dịch | Vào tab "Giao dịch" | Thấy tất cả giao dịch của customer (trừ DEPOSIT/WITHDRAW_WALLET) |
| b | Filter theo status | PENDING / APPROVED / REJECTED | Đúng |
| c | Filter theo type | OPEN_SAVINGS / TRANSFER_OUT / ... | Đúng |
| d | Thứ tự | Giao dịch mới nhất trên đầu | Đúng (ORDER BY created_at DESC) |

### TC-2.10: Xem gói tiết kiệm

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Danh sách gói | Vào tab "Gói tiết kiệm" | Chỉ thấy gói is_active = TRUE |
| b | Thông tin gói | Mỗi gói hiển thị: tên, kỳ hạn, lãi suất, min_days_hold | Đúng |

### TC-2.11: Mô phỏng lãi suất (Simulator)

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Nhập số tiền + chọn gói | 5,000,000 VND, 12 tháng, 6% | Chart + bảng hiển thị lãi ước tính |
| b | Thay đổi slider | Kéo slider kỳ hạn, lãi suất | Chart cập nhật real-time |
| c | Compound vs Simple | Toggle rollover = true/false | Kết quả khác nhau |
| d | Chọn product từ dropdown | Chọn gói có sẵn | Auto-fill term + rate |
| e | Chọn "manual" | Chọn nhập tay | Slider mở khóa |

### TC-2.12: Notifications (SSE)

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Kết nối SSE | Đăng nhập → /api/events?token=... | SSE stream mở, nhận event "ready" |
| b | Nhận notification khi giao dịch approved | Staff approve → Customer nhận toast | Toast hiện + bell pulse |
| c | Nhận notification khi giao dịch rejected | Staff reject → Customer nhận toast | Toast hiện |
| d | Nhận notification khi nhận chuyển khoản | Người khác chuyển tiền đến → nhận toast | Toast hiện |
| e | Badge count | Có pending transaction → badge hiện số | Đúng |
| f | Notification panel | Click bell → dropdown hiện 6 giao dịch gần nhất | Đúng |

---

## 5. Phase 3 — Staff Flows

> **Mục tiêu:** Staff là "checker" trong mô hình Maker/Checker. Test đảm bảo staff duyệt/từ chối đúng logic.

### TC-3.1: Dashboard Staff

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Xem dashboard | Thấy: pending count, tổng tiền tiết kiệm, summary metrics |
| b | Pending queue | Danh sách giao dịch chờ duyệt hiện đúng | Đúng |
| c | Auto-refresh | Sau 12 giây, dữ liệu tự reload | Đúng |

### TC-3.2: Duyệt giao dịch (Approve)

**Tại sao test từng loại:** Mỗi transaction_type có logic approve riêng — OPEN_SAVINGS tạo sổ mới, DEPOSIT_TO_SAVINGS cộng tiền vào sổ, WITHDRAW phải tính lãi, v.v.

| # | Loại giao dịch | Hành động | Kết quả mong đợi |
|---|----------------|-----------|-------------------|
| a | OPEN_SAVINGS | Duyệt mở sổ | Sổ tiết kiệm được tạo, wallet trừ tiền, status = APPROVED |
| b | DEPOSIT_TO_SAVINGS | Duyệt gửi thêm | principal_balance tăng, wallet trừ tiền |
| c | WITHDRAW_FROM_SAVINGS | Duyệt rút một phần | principal giảm, wallet nhận amount + interest |
| d | CLOSE_SAVINGS | Duyệt tất toán | Sổ → CLOSED, wallet nhận principal + interest |
| e | TRANSFER_OUT/IN | Chuyển khoản | Không cần duyệt (auto-approved), không hiện trong queue |
| f | Double approve | Duyệt giao dịch đã APPROVED | 400, đã xử lý |
| g | Approve REJECTED | Duyệt giao dịch đã REJECTED | 400, đã xử lý |

### TC-3.3: Từ chối giao dịch (Reject)

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Từ chối OPEN_SAVINGS | Reject pending mở sổ | Status → REJECTED, sổ KHÔNG được tạo, wallet KHÔNG thay đổi |
| b | Từ chối DEPOSIT_TO_SAVINGS | Reject gửi thêm | principal KHÔNG đổi, wallet KHÔNG thay đổi |
| c | Từ chối CLOSE_SAVINGS | Reject tất toán | Sổ vẫn ACTIVE, wallet KHÔNG đổi |
| d | Customer nhận thông báo | Sau reject | Customer nhận SSE "TRANSACTION_REJECTED" |

### TC-3.4: Lọc và xem giao dịch

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Filter status = PENDING | Chỉ hiện pending | Đúng |
| b | Filter status = APPROVED | Chỉ hiện approved | Đúng |
| c | Filter status = REJECTED | Chỉ hiện rejected | Đúng |
| d | Filter type = OPEN_SAVINGS | Chỉ hiện mở sổ | Đúng |
| e | Không hiện DEPOSIT/WITHDRAW_WALLET | 2 loại này bị exclude | Không thấy trong danh sách |

### TC-3.5: Xem danh sách khách hàng

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Xem danh sách | GET /api/users → danh sách customers | Chỉ hiện CUSTOMER role, không hiện STAFF/ADMIN |
| b | Thông tin hiển thị | Mỗi customer có: name, email, CMND, address, status | Đúng (KHÔNG hiện wallet_balance) |

### TC-3.6: Xem sổ tiết kiệm (tất cả)

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Danh sách sổ | Hiện tất cả sổ của tất cả customers | Đúng, kèm thông tin customer |
| b | Chi tiết sổ | Click 1 sổ → xem chi tiết | principal_balance, product info, maturity info |
| c | Auto-rollover trigger | Truy cập sổ term đã đáo hạn | Backend tự rollover, principal cập nhật |

### TC-3.7: Báo cáo BM5

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | BM5.1 — Báo cáo ngày | Chọn ngày → xem doanh thu | total_in (gửi), total_out (rút), difference |
| b | BM5.1 — Ngày không có giao dịch | Chọn ngày trống | Hiện 0 hoặc empty state |
| c | BM5.2 — Báo cáo tháng | Chọn tháng → xem mở/đóng sổ | opened_count, closed_count per product per day |
| d | BM5.2 — Filter product | Lọc theo product_id | Chỉ hiện product đó |

### TC-3.8: Analytics (Thống kê xu hướng)

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Xem tháng hiện tại | Chọn tháng hiện tại | Charts hiện: deposits, withdrawals, net flow, customer growth |
| b | Thay đổi tháng | Chọn tháng khác | Charts auto-reload |
| c | Tháng không có dữ liệu | Chọn tháng tương lai | Hiện "Không có dữ liệu" hoặc chart trống |
| d | Tháng ngoài range | Year < 2020 hoặc > 2030 | 400 hoặc empty state |

---

## 6. Phase 4 — Admin Flows

> **Mục tiêu:** Admin quản lý hệ thống. Sai ở đây ảnh hưởng toàn bộ business rules.

### TC-4.1: Dashboard Admin

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Xem dashboard | Thấy: total_customers, total_staff, total_admins, active_savings, total_savings_amount, pending_transactions, active_products, locked_accounts |
| b | Dữ liệu chính xác | So sánh với DB trực tiếp (COUNT queries) | Số liệu khớp |

### TC-4.2: Quản lý người dùng (User Management)

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Xem danh sách | GET /api/admin/users → tất cả users | Hiện full_name, email, role, status, created_at |
| b | Filter role | Lọc CUSTOMER / STAFF / ADMIN | Đúng |
| c | Filter status | Lọc ACTIVE / LOCKED | Đúng |
| d | Search | Tìm theo tên / email / CMND | Đúng (LIKE search) |
| e | Tạo user mới (STAFF) | Điền form → submit | 201, user mới có account_number |
| f | Tạo user mới (ADMIN) | Chọn role = ADMIN | 201 |
| g | Tạo user trùng email | Trùng email | 400 |
| h | Đổi role user | CUSTOMER → STAFF | 200, role thay đổi |
| i | Đổi role chính mình | Admin đổi role chính mình | 400, không được phép |
| j | Khóa tài khoản | Toggle status → LOCKED | User đó không thể đăng nhập |
| k | Khóa chính mình | Admin khóa chính mình | 400, không được phép |
| l | Mở khóa tài khoản | Toggle status → ACTIVE | User đó đăng nhập lại được |
| m | Xem chi tiết user | Click "Chi tiết" | Modal hiện: info + danh sách savings accounts |

### TC-4.3: Quản lý gói tiết kiệm (Savings Products)

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Xem danh sách | Tất cả gói (active + inactive) | Hiện đầy đủ thông tin |
| b | Tạo gói mới | name, term_months=12, rate=7.0, min_days_hold=0 | 201 |
| c | Tạo gói non-term | term_months=0, rate=1.0, min_days_hold=30 | 201 |
| d | Sửa gói | Edit interest_rate | 200, thay đổi lưu DB |
| e | Vô hiệu hóa gói | Toggle is_active → false | Gói không hiện cho Customer khi mở sổ |
| f | Kích hoạt lại gói | Toggle is_active → true | Gói hiện lại |
| g | Sửa gói đang có sổ active | Đổi rate gói đang có người dùng | 200 (sổ cũ vẫn giữ rate cũ? Hay cập nhật?) — **CẦN KIỂM TRA** |
| h | term_months < 0 | Nhập -1 | 400 hoặc validation |
| i | interest_rate < 0 | Nhập -0.5 | 400 hoặc validation |

### TC-4.4: Quản lý tham số hệ thống (System Configs)

**Tại sao test kỹ:** Configs quyết định business rules. Đổi MIN_OPEN_AMOUNT từ 1M thành 500K → ảnh hưởng tất cả customer.

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | Xem configs | 3 config mặc định: MIN_OPEN_AMOUNT, MIN_SAVINGS_DEPOSIT_AMOUNT, NON_TERM_MIN_DAYS | Đúng |
| b | Sửa MIN_OPEN_AMOUNT | Đổi từ 1000000 → 500000 | Customer có thể mở sổ 500K |
| c | Sửa NON_TERM_MIN_DAYS | Đổi từ 15 → 7 | Customer có thể rút sau 7 ngày |
| d | Tạo config mới | Thêm key mới | 201 |
| e | Xóa config | Xóa config tự tạo | 200 |
| f | Xóa config hệ thống | Xóa MIN_OPEN_AMOUNT | 200 (nhưng backend fallback = 1,000,000) — **CẦN KIỂM TRA hệ thống có crash không** |
| g | Config value = 0 | Đặt MIN_OPEN_AMOUNT = 0 | Customer mở sổ 0 VND? — **CẦN KIỂM TRA** |
| h | Config value âm | Đặt MIN_OPEN_AMOUNT = -1 | Hành vi không xác định — **CẦN KIỂM TRA** |
| i | Config value không phải số | Đặt MIN_OPEN_AMOUNT = "abc" | Backend parse thành int sẽ crash? — **CẦN KIỂM TRA** |

### TC-4.5: Báo cáo Admin

| # | Hành động | Kết quả mong đợi |
|---|-----------|-------------------|
| a | BM5.1 | Giống TC-3.7a-b | Đúng |
| b | BM5.2 | Giống TC-3.7c-d | Đúng |
| c | Dữ liệu khớp Staff | Admin và Staff xem cùng ngày/tháng → kết quả giống nhau | Đúng |

---

## 7. Phase 5 — Business Rules (QD1, QD2, QD3)

> **Mục tiêu:** Kiểm chứng business rules chính xác theo spec. Đây là phần quan trọng nhất vì sai logic = sai tiền.

### QD1 — Số tiền gửi tối thiểu khi mở sổ

**Rule:** `amount >= system_configs['MIN_OPEN_AMOUNT']` (default 1,000,000)

| # | Test case | Input | Expected |
|---|-----------|-------|----------|
| a | Đúng bằng min | amount = 1,000,000 | PASS → tạo pending |
| b | Dưới min | amount = 999,999 | REJECT 400 |
| c | Trên min | amount = 2,000,000 | PASS |
| d | Admin đổi min thành 500K | Sửa config → mở sổ 500K | PASS (config mới có hiệu lực) |
| e | Admin đổi min thành 2M | Sửa config → mở sổ 1.5M | REJECT 400 |

### QD2 — Gửi thêm tiền vào sổ

**Rule:** `amount >= MIN_SAVINGS_DEPOSIT_AMOUNT` (default 100,000) VÀ sổ term phải đã đáo hạn.

| # | Test case | Input | Expected |
|---|-----------|-------|----------|
| a | Non-term, amount = 100K | Gửi thêm vào sổ không kỳ hạn | PASS |
| b | Non-term, amount = 50K | Dưới min | REJECT 400 |
| c | Term 3 tháng, chưa đáo hạn | Gửi thêm vào sổ 3 tháng mới mở 1 ngày | REJECT 400 |
| d | Term 3 tháng, đã đáo hạn | Gửi thêm vào sổ đã qua 90 ngày | PASS |

### QD3 — Lãi suất khi rút/tất toán

**Rule:** Rút trước hạn → áp dụng lãi suất không kỳ hạn (0.5%). Rút đúng/sau hạn → áp dụng lãi suất gốc.

| # | Test case | Setup | Expected |
|---|-----------|-------|----------|
| a | Non-term, rút sau 15 ngày | Sổ non-term 0.5%, held = 20 ngày | interest = principal × 0.005 × 20/365 |
| b | Term 3T, rút đúng 90 ngày | Sổ 3 tháng 5%, held = 90 ngày | interest = principal × 0.05 × 90/365 |
| c | Term 3T, rút sớm (30 ngày) | Sổ 3 tháng 5%, held = 30 ngày | interest = principal × 0.005 × 30/365 (non-term rate!) |
| d | Term 6T, rút đúng hạn | Sổ 6 tháng 5.5%, held = 180 ngày | interest = principal × 0.055 × 180/365 |
| e | Non-term, rút trước min_days | Sổ non-term, held = 10 ngày (< 15) | REJECT 400, chưa đủ ngày giữ |
| f | Kiểm tra số tiền nhận | total_receive = amount + interest (withdraw) hoặc principal + interest (close) | Số tiền wallet tăng đúng |

### Auto-rollover

**Rule:** Sổ term khi đáo hạn tự compound: principal += interest, opened_at += term_months.

| # | Test case | Setup | Expected |
|---|-----------|-------|----------|
| a | Sổ 3T đáo hạn 1 lần | Sổ mở cách đây 100 ngày, term = 3 tháng | Principal += interest(90 days), opened_at += 3 months |
| b | Sổ 3T đáo hạn 2 lần | Sổ mở cách đây 200 ngày | 2 lần compound, 2 transactions AUTO_ROLLOVER |
| c | Trigger khi nào | GET savings-accounts hoặc GET detail | Rollover trigger khi đọc data |
| d | Rollover chỉ 1 lần | Gọi GET 2 lần liên tiếp | Lần 2 không rollover thêm |

---

## 8. Phase 6 — Cross-role Integration

> **Mục tiêu:** Test toàn bộ luồng end-to-end, từ Customer tạo request → Staff xử lý → kết quả phản ánh đúng.

### TC-6.1: Full Open Savings Flow

```
Customer đăng ký → đăng nhập → mở sổ 3T (2,000,000 VND) → PENDING
  → Staff đăng nhập → thấy pending → Approve
  → Customer: wallet giảm 2M, sổ mới xuất hiện, status=ACTIVE
  → Admin: dashboard cập nhật (active_savings_accounts +1, total_savings_amount +2M)
```

| Checkpoint | Verify |
|------------|--------|
| Customer wallet trước | 10,000,000 |
| Pending transaction hiện | Đúng, amount = 2,000,000 |
| Staff thấy pending | Đúng, trong queue |
| Sau approve — Customer wallet | 8,000,000 |
| Sau approve — Sổ mới | ACTIVE, principal = 2,000,000 |
| Admin dashboard | active_savings +1 |

### TC-6.2: Full Close Savings Flow (Early Withdrawal)

```
Customer tất toán sổ 3T mới mở → PENDING (is_early_withdrawal = true)
  → Staff approve
  → Customer wallet += principal + interest(0.5% × days/365)
  → Sổ status = CLOSED
```

### TC-6.3: Full Close Savings Flow (Matured)

```
Customer tất toán sổ 3T đã đáo hạn → PENDING
  → Staff approve
  → Customer wallet += principal + interest(5% × days/365)
  → Sổ status = CLOSED
```

### TC-6.4: Reject Flow

```
Customer mở sổ → PENDING
  → Staff reject
  → Customer: wallet KHÔNG đổi, transaction status = REJECTED
  → Customer nhận SSE notification "rejected"
```

### TC-6.5: Transfer Flow

```
Customer A chuyển 500,000 → Customer B
  → A wallet -500K, B wallet +500K (tức thì, không qua Staff)
  → 2 transactions: TRANSFER_OUT (A), TRANSFER_IN (B), cả hai APPROVED
  → B nhận SSE notification
```

### TC-6.6: Admin Config Change → Customer Impact

```
Admin đổi MIN_OPEN_AMOUNT = 500,000
  → Customer mở sổ 600K → thành công (trước đó phải 1M)
Admin đổi MIN_OPEN_AMOUNT = 5,000,000
  → Customer mở sổ 2M → bị từ chối
```

### TC-6.7: Admin Deactivate Product → Customer Impact

```
Admin deactivate "Tiết kiệm 3 tháng"
  → Customer không thấy gói này trong dropdown
  → Customer cố gửi API trực tiếp → 400 "product không active"
  → Sổ cũ đã mở vẫn hoạt động bình thường
```

### TC-6.8: Admin Lock User → Login Impact

```
Admin lock Customer A
  → Customer A đăng nhập → 403 "tài khoản bị khóa"
  → Sổ tiết kiệm của A vẫn tồn tại, chỉ không truy cập được
Admin unlock → Customer A đăng nhập lại bình thường
```

---

## 9. Phase 7 — Edge Cases & Security

> **Mục tiêu:** Tìm bugs ẩn, lỗ hổng bảo mật, race conditions.

### TC-7.1: Race Conditions

| # | Scenario | Hành động | Expected |
|---|----------|-----------|----------|
| a | Double submit | Customer click "Mở sổ" 2 lần nhanh | Chỉ tạo 1 transaction (hoặc cả 2 nhưng available balance check chặn cái thứ 2) |
| b | 2 Staff approve cùng lúc | 2 staff approve cùng 1 pending | Chỉ 1 thành công, 1 nhận 400 "đã xử lý" |
| c | Transfer + Open savings cùng lúc | Wallet = 10M, transfer 6M + open 6M song song | Ít nhất 1 bị reject (tổng > 10M) |
| d | Approve sau khi user bị lock | Customer bị lock → Staff approve pending | Nên thành công (transaction đã tạo trước khi lock) — **CẦN KIỂM TRA** |

### TC-7.2: Boundary Values

| # | Scenario | Input | Expected |
|---|----------|-------|----------|
| a | Amount = 0 | Mở sổ, chuyển khoản | 400 |
| b | Amount cực lớn | 999,999,999,999.99 | Xử lý đúng (DECIMAL(15,2)) |
| c | Amount = 0.01 | Chuyển khoản 0.01 VND | Thành công (amount > 0) |
| d | String thay vì number | amount = "abc" | 400 hoặc 500 |
| e | Negative amount | amount = -1000 | 400 |
| f | Very long email | 100+ chars | DB truncate hoặc 400 |
| g | Special chars in name | full_name = "<script>alert(1)</script>" | Lưu DB đúng, render không XSS |

### TC-7.3: Security Testing

| # | Test | Hành động | Expected |
|---|------|-----------|----------|
| a | SQL Injection | email = "' OR 1=1 --" | Không bị inject (parameterized queries) |
| b | XSS stored | full_name = "<img onerror=alert(1) src=x>" | HTML escaped khi render |
| c | JWT manipulation | Sửa payload JWT (đổi role) | 401 (signature invalid) |
| d | JWT reuse after password change | Đổi password → dùng token cũ | Vẫn valid (token không bị revoke) — **KNOWN LIMITATION** |
| e | IDOR — xem sổ người khác | GET /api/client/savings-accounts/999 (của user khác) | 404 (ownership check) |
| f | IDOR — đóng sổ người khác | POST /api/client/close-savings/999 (của user khác) | 404 (ownership check) |
| g | Rate limiting | 100 login requests/giây | Không có rate limit — **KNOWN LIMITATION** |
| h | CORS | Request từ domain khác | Phụ thuộc Flask CORS config — **CẦN KIỂM TRA** |
| i | Secret key hardcoded | SECRET_KEY default | Nếu không set env → token predictable — **KNOWN RISK** |

### TC-7.4: Error Handling

| # | Scenario | Expected |
|---|----------|----------|
| a | DB connection lost | 500 + error message (không leak DB info) |
| b | Invalid JSON body | 400 + meaningful error |
| c | Missing Content-Type | 400 hoặc 415 |
| d | Very large request body | 413 hoặc timeout |
| e | Concurrent DB writes | No deadlock, data consistent |

### TC-7.5: Data Consistency

| # | Scenario | Verify |
|---|----------|--------|
| a | Sau approve mở sổ | SUM(wallet) + SUM(principal) = total money in system |
| b | Sau transfer | Sender wallet + Receiver wallet = tổng trước transfer |
| c | Sau close savings | principal → 0, wallet += principal + interest |
| d | Pending reservation | available_wallet = wallet - SUM(pending amounts) |
| e | Reject → no side effect | Reject không thay đổi bất kỳ số dư nào |

---

## 10. Phase 8 — UI/UX & Responsive

> **Mục tiêu:** Đảm bảo giao diện hoạt động đúng trên các trình duyệt và kích thước màn hình.

### TC-8.1: Cross-browser

| Browser | Test |
|---------|------|
| Chrome (latest) | Full flow |
| Firefox (latest) | Full flow |
| Safari (latest) | Full flow |
| Mobile Chrome | Basic flow |

### TC-8.2: UI Elements

| # | Page | Check |
|---|------|-------|
| a | Login | Form validation messages hiện đúng vị trí |
| b | Customer dashboard | Cards responsive, số liệu format VND đúng (1.000.000) |
| c | Customer tables | Bảng scroll ngang trên mobile |
| d | Staff transaction table | Nút Duyệt/Từ chối hiện đúng, disabled khi đang xử lý |
| e | Admin sidebar | Collapse trên mobile |
| f | Modals | Đóng khi click backdrop / nhấn Escape |
| g | Toast notifications | Hiện đúng vị trí, tự mất sau vài giây |
| h | Loading states | Hiện "Đang tải..." khi fetch data |
| i | Empty states | Hiện message khi không có data |
| j | Number formatting | VND format đúng: 1.000.000 (dấu chấm ngăn cách hàng nghìn) |
| k | Date formatting | YYYY-MM-DD hoặc DD/MM/YYYY nhất quán |

### TC-8.3: Navigation

| # | Check | Expected |
|---|-------|----------|
| a | Sidebar active state | Link đang ở trang nào highlight đúng |
| b | Browser back button | Quay lại trang trước đúng (Admin SPA) |
| c | Refresh page | Không bị logout, data reload đúng |
| d | Direct URL access | Gõ /admin/users trực tiếp → đúng trang (nếu đã login) |
| e | Logout → Back button | Sau logout, nhấn Back → redirect /login (không quay lại trang cũ) |

---

## 11. Tại sao plan này được thiết kế như vậy

### Triết lý thiết kế

**1. Test theo role trước, test tích hợp sau (Phase 1-4 → Phase 6)**

Lý do: Khi test tích hợp fail, ta cần biết lỗi ở đâu. Nếu Customer mở sổ + Staff duyệt fail, bug có thể ở:
- API mở sổ (Customer)
- API duyệt (Staff)
- Logic tính tiền (Business rule)
- SSE notification

Bằng cách test riêng từng role trước, ta thu hẹp phạm vi debug. Phase 6 chỉ test "sự tương tác" giữa các role — không test lại logic đã verify ở Phase 1-4.

**2. Business rules tách riêng (Phase 5)**

Lý do: QD1, QD2, QD3 là core logic quyết định đúng/sai của hệ thống. Nếu trộn vào Phase 2-4, ta dễ bỏ sót edge cases (ví dụ: đổi config → rule thay đổi, hoặc rút sớm → lãi suất giảm). Phase 5 focus hoàn toàn vào logic, dùng API trực tiếp, không phụ thuộc UI.

**3. Security & Edge cases cuối cùng (Phase 7)**

Lý do: Phải đảm bảo happy path hoạt động trước. Nếu mở sổ còn fail ở happy path, thì test SQL injection trên endpoint đó vô nghĩa. Phase 7 giả định các flow cơ bản đã pass.

**4. Mỗi test case đều có "Tại sao test này quan trọng"**

Lý do: Khi agent test, nó cần hiểu context để:
- Biết test nào ưu tiên cao (tiền, lãi suất → critical)
- Biết test nào có thể skip tạm (UI cosmetic → low priority)
- Biết cách report bug (nếu hiểu tại sao test → report rõ impact)

**5. Đánh dấu "CẦN KIỂM TRA" cho behavior chưa rõ**

Lý do: Có những trường hợp spec không nói rõ (ví dụ: xóa config hệ thống → backend crash hay fallback?). Đánh dấu này để agent test proactively thay vì assume.

### Ưu tiên test

Nếu thời gian hạn chế, ưu tiên theo thứ tự:

1. **P0 (Critical):** TC-1.1→1.4, TC-2.3, TC-2.4, TC-2.7, TC-3.2, TC-3.3, TC-6.1→6.4
   - Lý do: Đây là core flows. Nếu fail → hệ thống không dùng được.

2. **P1 (High):** TC-2.5, TC-2.6, TC-5 (QD1-3), TC-4.2, TC-4.4, TC-7.3 (security), TC-7.5 (data consistency)
   - Lý do: Ảnh hưởng tiền và bảo mật.

3. **P2 (Medium):** TC-2.8→2.12, TC-3.4→3.8, TC-4.1, TC-4.3, TC-4.5, TC-6.5→6.8
   - Lý do: Tính năng phụ trợ, UX.

4. **P3 (Low):** TC-7.1 (race conditions), TC-7.2 (boundary), TC-7.4 (error handling), TC-8 (UI/UX)
   - Lý do: Edge cases, hiếm xảy ra trong demo.

### Cách agent nên chạy test

```
1. Đọc plan.md để hiểu scope
2. Start backend + frontend
3. Chạy Phase 1-4 (role-by-role), ghi kết quả
4. Chạy Phase 5 (business rules), verify bằng API trực tiếp
5. Chạy Phase 6 (integration), dùng Playwright hoặc manual
6. Chạy Phase 7 (security), dùng curl/httpie/Playwright
7. Chạy Phase 8 (UI), dùng Playwright screenshots
8. Tổng hợp: file BUGS.md với format:
   - Bug ID
   - Severity (Critical / High / Medium / Low)
   - Phase + TC number
   - Steps to reproduce
   - Expected vs Actual
   - Suggested fix
```

---

## Phụ lục: API Endpoint Reference

### Public (No auth)
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/ping | Health check |
| POST | /api/auth/register | Đăng ký Customer |
| POST | /api/auth/login | Đăng nhập |
| POST | /api/auth/forgot-password | Quên mật khẩu |

### Customer (CUSTOMER role)
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/client/me | Profile |
| PATCH | /api/client/me | Update address |
| GET | /api/client/dashboard | Dashboard data |
| GET | /api/client/savings-products | Active products |
| GET | /api/client/savings-accounts | Danh sách sổ |
| GET | /api/client/savings-accounts/:id | Chi tiết sổ |
| GET | /api/client/savings-accounts/:id/estimate-interest | Ước tính lãi |
| POST | /api/client/open-savings | Mở sổ mới |
| POST | /api/client/savings-accounts/:id/deposit-requests | Gửi thêm |
| POST | /api/client/savings-accounts/:id/withdraw-requests | Rút một phần |
| POST | /api/client/close-savings/:id | Tất toán |
| POST | /api/client/transfers | Chuyển khoản |
| GET | /api/client/transactions | Lịch sử GD |

### Staff (STAFF role)
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/transactions | Danh sách GD |
| PUT | /api/transactions/:id/approve | Duyệt |
| PUT | /api/transactions/:id/reject | Từ chối |
| PATCH | /api/transactions/:id | Duyệt/từ chối |
| GET | /api/users | Danh sách customers |
| GET | /api/savings-accounts | Tất cả sổ TK |
| GET | /api/savings-accounts/:id | Chi tiết sổ |
| GET | /api/balance-system | Tổng tiền hệ thống |
| GET | /api/reports/daily-activity | BM5.1 |
| GET | /api/reports/monthly-open-close | BM5.2 |
| GET | /api/staff/analytics | Thống kê xu hướng |

### Admin (ADMIN role)
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/admin/dashboard | Dashboard |
| GET | /api/admin/users | Danh sách users |
| GET | /api/admin/users/:id | Chi tiết user |
| POST | /api/admin/users | Tạo user |
| PUT | /api/admin/users/:id/role | Đổi role |
| PUT | /api/admin/users/:id/status | Đổi status |
| PATCH | /api/admin/users/:id | Update user |
| GET | /api/admin/savings-products | Danh sách gói |
| POST | /api/admin/savings-products | Tạo gói |
| PATCH | /api/admin/savings-products/:id | Sửa gói |
| PUT | /api/admin/savings-products/:id/toggle | Toggle active |
| GET | /api/admin/configs | Danh sách configs |
| POST | /api/admin/configs | Tạo config |
| PATCH | /api/admin/configs/:key | Sửa config |
| DELETE | /api/admin/configs/:key | Xóa config |

### SSE
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/events?token=JWT | Server-Sent Events stream |
