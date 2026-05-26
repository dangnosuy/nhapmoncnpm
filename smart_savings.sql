DROP DATABASE IF EXISTS modern_savings_db;
CREATE DATABASE modern_savings_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'smart_savings'@'localhost' IDENTIFIED BY 'SmartSavings@2026!';
ALTER USER 'smart_savings'@'localhost' IDENTIFIED BY 'SmartSavings@2026!';
GRANT ALL PRIVILEGES ON modern_savings_db.* TO 'smart_savings'@'localhost';
FLUSH PRIVILEGES;

USE modern_savings_db;

-- ==========================================
-- 1. BẢNG CẤU HÌNH HỆ THỐNG (Tham số động)
-- ==========================================
CREATE TABLE system_configs (
    config_key VARCHAR(50) PRIMARY KEY,
    config_value VARCHAR(255) NOT NULL,
    description VARCHAR(255)
);

-- ==========================================
-- 2. BẢNG NGƯỜI DÙNG (Khách + Nhân Viên)
-- ==========================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    identity_card VARCHAR(20) UNIQUE, -- CMND/CCCD
    account_number VARCHAR(20) UNIQUE, -- Số tài khoản ngân hàng duy nhất
    address VARCHAR(255), -- Địa chỉ (BM1)
    role ENUM('CUSTOMER', 'STAFF', 'ADMIN') DEFAULT 'CUSTOMER',
    wallet_balance DECIMAL(15, 2) DEFAULT 0.00, -- "Tiền nhàn rỗi" trong ví app (chỉ Client thấy)
    status ENUM('ACTIVE', 'LOCKED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 3. BẢNG GÓI TIẾT KIỆM (Loại Sổ)
-- ==========================================
CREATE TABLE savings_products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- Tên gói (VD: Không kỳ hạn, 3 tháng...)
    term_months INT NOT NULL DEFAULT 0, -- 0 là Không kỳ hạn
    interest_rate DECIMAL(5, 2) NOT NULL, -- Mức lãi suất (%/năm)
    min_days_hold INT DEFAULT 0, -- Ràng buộc: Số ngày tối thiểu phải giữ tiền
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT
);

-- ==========================================
-- 4. BẢNG SỔ TIẾT KIỆM ĐIỆN TỬ
-- ==========================================
CREATE TABLE savings_accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL, -- Cuốn sổ này của ai?
    product_id INT NOT NULL, -- Thuộc loại kỳ hạn nào?
    principal_balance DECIMAL(15, 2) NOT NULL CHECK (principal_balance >= 0), -- Gốc, chặn số âm
    opened_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- Ngày mở sổ
    status ENUM('ACTIVE', 'CLOSED') DEFAULT 'ACTIVE', -- Sổ đang hoạt động hay đã tất toán
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES savings_products(product_id)
);

-- ==========================================
-- 5. BẢNG LỊCH SỬ GIAO DỊCH (Sổ Cái - Maker/Checker)
-- ==========================================
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL, -- Ai tạo phiếu này?
    account_id INT NULL, -- Sổ nào? (NULL nếu sổ chưa được duyệt tạo)
    target_product_id INT NULL, -- Gói tiết kiệm nhắm tới (Dùng khi chờ Staff duyệt)
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0), -- Số tiền GD, chặn số âm
    
    transaction_type ENUM(
        'DEPOSIT_TO_WALLET', 'WITHDRAW_FROM_WALLET',
        'OPEN_SAVINGS', 'DEPOSIT_TO_SAVINGS',
        'WITHDRAW_FROM_SAVINGS', 'CLOSE_SAVINGS',
        'TRANSFER_OUT', 'TRANSFER_IN',
        'AUTO_ROLLOVER'
    ) NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING', -- Trạng thái duyệt
    interest_amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Tiền lãi phát sinh khi rút/tất toán
    
    processed_by INT NULL, -- Staff nào duyệt?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 

    -- Khóa ngoại kết nối chặt chẽ dữ liệu
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (account_id) REFERENCES savings_accounts(account_id),
    FOREIGN KEY (target_product_id) REFERENCES savings_products(product_id),
    FOREIGN KEY (processed_by) REFERENCES users(user_id)
);

-- ==========================================
-- 6. DỮ LIỆU KHỞI TẠO
-- ==========================================
INSERT INTO system_configs (config_key, config_value, description) VALUES
('MIN_OPEN_AMOUNT', '1000000', 'So tien toi thieu khi mo so tiet kiem (QD1: 1.000.000d)'),
('MIN_SAVINGS_DEPOSIT_AMOUNT', '100000', 'So tien toi thieu khi gui them vao so (QD2: 100.000d)'),
('NON_TERM_MIN_DAYS', '15', 'So ngay toi thieu de rut so khong ky han (QD3: 15 ngay)');
