# **TÀI LIỆU ĐẶC TẢ NGHIỆP VỤ & QUY TRÌNH HỆ THỐNG QUẢN LÝ SỔ TIẾT KIỆM (SMART SAVINGS)**

**Phiên bản:** 1.0

**Mục tiêu:** Xây dựng hệ thống quản lý gửi tiết kiệm ngân hàng, kết hợp giữa quy trình nghiệp vụ tại quầy (theo yêu cầu Đề tài 1.9) và quy trình số hóa hiện đại (Online Request).

## **1\. TỔNG QUAN KIẾN TRÚC (HIGH-LEVEL ARCHITECTURE)**

Hệ thống hoạt động theo mô hình **Maker-Checker** (Người tạo yêu cầu \- Người duyệt) kết hợp với **Phân quyền 3 lớp** (3-Tier Roles).

### **Các Role (Vai trò) trong hệ thống:**

1. **User (Khách hàng):** Người dùng cuối. Có thể xem thông tin cá nhân và **gửi yêu cầu (Request)** giao dịch. Không có quyền ghi trực tiếp vào dữ liệu tài chính.  
2. **Staff (Nhân viên Ngân hàng):** Người vận hành chính. Có quyền **xử lý hàng đợi yêu cầu** từ User hoặc **nhập liệu trực tiếp** cho khách vãng lai. Chịu trách nhiệm về tính chính xác của giao dịch.  
3. **Admin (Quản trị viên):** Người quản lý hệ thống. Chịu trách nhiệm quản lý nhân sự và **Cấu hình tham số quy định (QĐ6)**.

## **2\. QUY TRÌNH NGHIỆP VỤ CHI TIẾT (WORKFLOWS)**

Hệ thống hỗ trợ 2 luồng quy trình song song:

### **LUỒNG A: Quy trình Online (User gửi yêu cầu \- Staff duyệt)**

*Đây là luồng chính giúp giảm tải nhập liệu và tăng trải nghiệm người dùng.*

1. **Khởi tạo (User):** User đăng nhập, chọn sổ tiết kiệm và chọn hành động (Gửi thêm/Rút tiền). User nhập số tiền mong muốn ![][image1] Bấm "Gửi yêu cầu".  
2. **Hàng đợi (System):** Hệ thống ghi nhận trạng thái PENDING. Yêu cầu này xuất hiện trên Dashboard của Staff.  
3. **Tiếp nhận (Staff):** Staff xem danh sách chờ, chọn yêu cầu của User.  
4. **Kiểm tra & Duyệt (Staff \+ System):**  
   * Hệ thống tự động điền thông tin từ yêu cầu vào biểu mẫu (Form).  
   * Hệ thống chạy validation (Kiểm tra quy định rút, kiểm tra kỳ hạn...).  
   * Staff đối chiếu thực tế (nếu có nộp tiền mặt) ![][image1] Bấm **"Xác nhận" (Approve)**.  
5. **Hoàn tất:** Hệ thống trừ/cộng tiền trong Database ![][image1] Trạng thái yêu cầu chuyển thành COMPLETED ![][image1] Thông báo cho User.

### **LUỒNG B: Quy trình Tại quầy (Staff nhập thủ công)**

*Đây là luồng bắt buộc để đáp ứng yêu cầu "Lập phiếu" của đề tài môn học.*

1. **Tiếp nhận:** Khách hàng đến quầy, đưa CMND và Sổ (nếu có).  
2. **Tra cứu:** Staff nhập CMND hoặc Mã sổ để tìm thông tin khách hàng.  
3. **Nhập liệu:** Staff chọn chức năng "Lập phiếu Gửi/Rút" ![][image1] Nhập số tiền và các thông tin cần thiết bằng tay.  
4. **Xác nhận:** Staff bấm "Lưu". Hệ thống kiểm tra quy định và ghi xuống Database.

## **3\. CHI TIẾT TÍNH NĂNG THEO ROLE (FEATURE SPECS)**

### **3.1. Phân hệ USER (Khách hàng)**

* **Dashboard:** Hiển thị tổng tài sản, danh sách các Sổ tiết kiệm đang sở hữu.  
* **Chi tiết Sổ:** Xem Mã sổ, Loại kỳ hạn, Lãi suất áp dụng, Số dư hiện tại, Ngày đáo hạn, Ngày mở sổ.  
* **Gửi yêu cầu (Transaction Request):**  
  * Đăng ký Mở sổ mới (Nhập số tiền dự kiến, chọn kỳ hạn).  
  * Đăng ký Gửi thêm tiền (Chọn sổ, nhập số tiền).  
  * Đăng ký Rút tiền (Chọn sổ, nhập số tiền hoặc chọn Tất toán).  
* **Tiện ích:**  
  * **Lịch sử giao dịch:** Xem lại các lần gửi/rút trước đó.  
  * **Tính lãi dự tính:** Nhập ngày dự kiến rút ![][image1] Hệ thống tính ra số tiền lãi (Dựa trên công thức lãi suất hiện tại). *Lưu ý: Chỉ hiển thị, không lưu DB.*

### **3.2. Phân hệ STAFF (Nhân viên \- Core Logic)**

Đây là nơi thực hiện các Biểu mẫu (BM) của đề tài.

* **Quản lý Hàng đợi (Request Queue):** Xem list các yêu cầu PENDING. Duyệt (Approve) hoặc Từ chối (Reject).  
* **Quản lý Sổ tiết kiệm (BM1):** Mở sổ cho khách mới. Hệ thống tự tạo mã sổ độc nhất.  
* **Lập Phiếu Gửi tiền (BM2):**  
  * Input: Mã sổ, Số tiền.  
  * Logic: Update SoDu \= SoDu \+ SoTien. Insert vào bảng PHIEU\_GUI.  
  * *Rule:* Chỉ cho gửi thêm nếu loại tiết kiệm cho phép.  
* **Lập Phiếu Rút tiền (BM3):**  
  * Input: Mã sổ, Số tiền rút.  
  * Logic: Tự động tính lãi suất dựa trên ngày rút so với ngày đáo hạn.  
  * *Rule:* Kiểm tra số dư tối thiểu sau khi rút (nếu rút 1 phần). Kiểm tra quy định thời gian gửi (ví dụ: phải gửi \> 15 ngày mới được rút).  
* **Tra cứu & Báo cáo (BM4, BM5):**  
  * Tra cứu sổ theo CMND, Mã sổ, Loại tiết kiệm.  
  * Xuất báo cáo Doanh số ngày (Tổng thu \- Tổng chi).  
  * Xuất báo cáo Đóng/Mở sổ tháng.

### **3.3. Phân hệ ADMIN (Quản trị & Cấu hình \- QĐ6)**

* **Quản lý Nhân sự:** Tạo tài khoản Staff, Khóa tài khoản, nâng quyền User thường lên Staff/Admin.  
* **Thay đổi Quy định (Dynamic Configuration):** Đây là tính năng QĐ6. Admin có thể sửa các giá trị trong bảng tham số:  
  * *Danh sách loại tiết kiệm:* Thêm kỳ hạn mới (ví dụ: 12 tháng, 24 tháng), sửa lãi suất (%/năm).  
  * *Tham số chung:* Sửa số tiền gửi tối thiểu (ví dụ: từ 1tr lên 2tr), số dư tối thiểu phải duy trì.  
  * *Tác động:* Việc sửa đổi này phải áp dụng ngay lập tức cho các giao dịch phát sinh sau đó.

## **4\. CƠ CHẾ TÍNH TOÁN & LOGIC NGẦM (BACKEND LOGIC)**

Team Dev cần chú ý đặc biệt các logic sau:

### **4.1. Cơ chế tính lãi (Interest Calculation)**

Công thức lãi suất cần được cài đặt linh hoạt:

* **Đúng hạn/Quá hạn:** ![][image2].  
* **Rút trước hạn:** Quy về lãi suất không kỳ hạn (thấp hơn, ví dụ 0.5%).  
* **Tự động đáo hạn (Auto-rollover):** Nếu đến ngày đáo hạn mà khách không rút, hệ thống (qua Cronjob hoặc khi truy vấn) sẽ tự động cộng lãi vào gốc và tái tục kỳ hạn mới.

### **4.2. Quản lý Tham số (QĐ6 implementation)**

Tuyệt đối **KHÔNG hard-code** (gán cứng) các con số trong code.

* *Sai:* if (amount \< 100000\) return error;  
* *Đúng:*  
  const minAmount \= await db.Settings.get('MIN\_DEPOSIT\_AMOUNT');  
  if (amount \< minAmount) return error;

- Thiết kế DB để định hình chung tránh sai lệch về đơn vị  
- Trường: User  
- Đức: Admin  
- Tao, Chou : Staff

\=\> Phần cơ bản theo đề tài

- Nâng cao: Cô đòi nó giống MB   
- Nhờ AI để tư vấn nộp vào thời điểm nào, rút lúc nào? Để sinh lời nhiều nhất\!\!\!\!\!

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAXCAYAAADpwXTaAAABZklEQVR4XrVUMVLEMAxMBlp6isN2UtxVVDQUfIIn0MAMX+ATfIEZHkBDRXH/okKSV5Fk+7pDMxtLWmnli52bJrZZntWdKywRluCJy/WW0ewpU87J0TRGTdX8xs7N3E4aTSIwMO53uuyMCzuTunbkf4iJe0JHWkDW8rZw9rvxBGIg1mjkCTMdhwhFvnDQxMl1Xfe73c0tQ3NhbcJhpFZKuc45fTJabvLXosbtBvVHWDal9A48CCfU1ulPQ3OtWc3+cLhikNgX4S42n0uMSi5zyt+U/Mk5O7g4xTgB5B8Jv+S/YRNuG2FHNi6uZnQYTyT2StxFx6v49q1JchZCLzYvtNNHRlmWl61MH/YH4O+5eeqqYCnLB2Pw5Vimvbs6wCeXUu7p/T4zUOA6YmDmeM9KhJbQ1ctYNJAX0x7l64rorGKhTd4oIGl/ruqBQ3o7BNR3BUYGB53+xJ2YBJ2KmRVimEUIsVs8/gA/gibr+3YDSwAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,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>