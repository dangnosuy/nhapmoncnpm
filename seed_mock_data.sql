-- ==========================================
-- MOCK DATA — Smart Savings System (v2)
-- Maps to existing users (36-55) and products (10-15)
-- ==========================================

USE modern_savings_db;

-- Product ID mapping:
-- 10 = Không kỳ hạn, 11 = 3 tháng, 12 = 6 tháng, 13 = 9 tháng, 14 = 12 tháng, 15 = 24 tháng

-- User ID mapping (customers):
-- 36=An, 37=Bình, 38=Cường, 39=Dung, 40=Em, 41=Giang, 42=Hải, 43=Hương
-- 44=Khánh, 45=Lan, 46=Minh, 47=Nga, 48=Phúc, 49=Quỳnh, 50=Sơn, 51=Thảo
-- 52=Thanh, 53=Uyên, 54=Việt, 55=Xuân

-- Staff: user_id 2 (staff@gmail.com), 34 (staff2@gmail.com)

-- ==========================================
-- 1. SAVINGS ACCOUNTS (30+ active + 5 closed)
-- ==========================================

-- User 36 (An) — 3 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(36, 10, 5000000.00, '2025-01-20 09:00:00', 'ACTIVE'),
(36, 12, 20000000.00, '2025-02-01 10:00:00', 'ACTIVE'),
(36, 14, 50000000.00, '2025-03-15 11:00:00', 'ACTIVE');

-- User 37 (Bình) — 2 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(37, 11, 10000000.00, '2025-01-25 14:00:00', 'ACTIVE'),
(37, 10, 3000000.00, '2025-03-10 09:00:00', 'ACTIVE');

-- User 38 (Cường) — 3 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(38, 14, 100000000.00, '2025-02-05 10:00:00', 'ACTIVE'),
(38, 13, 30000000.00, '2025-03-01 11:00:00', 'ACTIVE'),
(38, 15, 50000000.00, '2025-04-01 08:00:00', 'ACTIVE');

-- User 39 (Dung) — 1 account
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(39, 10, 8000000.00, '2025-02-15 15:00:00', 'ACTIVE');

-- User 40 (Em) — 2 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(40, 12, 40000000.00, '2025-02-20 09:00:00', 'ACTIVE'),
(40, 14, 80000000.00, '2025-03-01 10:00:00', 'ACTIVE');

-- User 41 (Giang) — 2 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(41, 11, 15000000.00, '2025-03-05 14:00:00', 'ACTIVE'),
(41, 10, 5000000.00, '2025-04-01 09:00:00', 'ACTIVE');

-- User 42 (Hải) — 3 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(42, 14, 150000000.00, '2025-03-10 08:00:00', 'ACTIVE'),
(42, 15, 100000000.00, '2025-04-01 09:00:00', 'ACTIVE'),
(42, 12, 50000000.00, '2025-05-01 10:00:00', 'ACTIVE');

-- User 43 (Hương) — 1 account
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(43, 11, 10000000.00, '2025-03-15 11:00:00', 'ACTIVE');

-- User 44 (Khánh) — 2 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(44, 13, 25000000.00, '2025-03-25 13:00:00', 'ACTIVE'),
(44, 10, 10000000.00, '2025-04-10 09:00:00', 'ACTIVE');

-- User 45 (Lan) — 2 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(45, 12, 20000000.00, '2025-04-05 08:00:00', 'ACTIVE'),
(45, 14, 30000000.00, '2025-05-01 10:00:00', 'ACTIVE');

-- User 46 (Minh) — 3 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(46, 14, 200000000.00, '2025-04-15 09:00:00', 'ACTIVE'),
(46, 15, 100000000.00, '2025-05-01 10:00:00', 'ACTIVE'),
(46, 11, 50000000.00, '2025-06-01 11:00:00', 'ACTIVE');

-- User 47 (Nga) — 1 account
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(47, 10, 5000000.00, '2025-04-20 14:00:00', 'ACTIVE');

-- User 48 (Phúc) — 2 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(48, 12, 30000000.00, '2025-04-25 09:00:00', 'ACTIVE'),
(48, 14, 50000000.00, '2025-05-15 10:00:00', 'ACTIVE');

-- User 49 (Quỳnh) — 1 account
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(49, 11, 15000000.00, '2025-05-05 08:30:00', 'ACTIVE');

-- User 50 (Sơn) — 2 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(50, 14, 80000000.00, '2025-05-10 10:00:00', 'ACTIVE'),
(50, 13, 40000000.00, '2025-06-01 11:00:00', 'ACTIVE');

-- User 51 (Thảo) — 1 account
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(51, 10, 8000000.00, '2025-05-15 09:30:00', 'ACTIVE');

-- User 52 (Thanh) — 2 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(52, 14, 100000000.00, '2025-05-20 11:00:00', 'ACTIVE'),
(52, 12, 30000000.00, '2025-06-01 08:00:00', 'ACTIVE');

-- User 53 (Uyên) — 1 account
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(53, 13, 25000000.00, '2025-05-25 13:00:00', 'ACTIVE');

-- User 54 (Việt) — 1 account
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(54, 12, 20000000.00, '2025-06-05 08:00:00', 'ACTIVE');

-- User 55 (Xuân) — 2 accounts
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(55, 14, 60000000.00, '2025-06-10 09:00:00', 'ACTIVE'),
(55, 10, 10000000.00, '2025-06-15 10:00:00', 'ACTIVE');

-- CLOSED accounts (historical)
INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES
(37, 12, 0.00, '2025-01-10 09:00:00', 'CLOSED'),
(39, 11, 0.00, '2025-01-20 10:00:00', 'CLOSED'),
(43, 14, 0.00, '2025-02-01 11:00:00', 'CLOSED'),
(47, 12, 0.00, '2025-02-15 14:00:00', 'CLOSED'),
(51, 11, 0.00, '2025-03-01 08:00:00', 'CLOSED');

-- ==========================================
-- 2. TRANSACTIONS
-- ==========================================
-- Account IDs will be auto-assigned. We need to get them.
-- The accounts we just inserted start from (SELECT MAX(account_id) - 35 + 1)
-- Let's use a variable approach.

-- Get the first account_id of our newly inserted accounts
SET @first_acct = (SELECT MIN(account_id) FROM savings_accounts WHERE user_id >= 36 AND status IN ('ACTIVE','CLOSED'));

-- Account mapping relative to @first_acct:
-- @first_acct+0  = 36/10 (An, KKH)
-- @first_acct+1  = 36/12 (An, 6th)
-- @first_acct+2  = 36/14 (An, 12th)
-- @first_acct+3  = 37/11 (Bình, 3th)
-- @first_acct+4  = 37/10 (Bình, KKH)
-- @first_acct+5  = 38/14 (Cường, 12th)
-- @first_acct+6  = 38/13 (Cường, 9th)
-- @first_acct+7  = 38/15 (Cường, 24th)
-- @first_acct+8  = 39/10 (Dung, KKH)
-- @first_acct+9  = 40/12 (Em, 6th)
-- @first_acct+10 = 40/14 (Em, 12th)
-- @first_acct+11 = 41/11 (Giang, 3th)
-- @first_acct+12 = 41/10 (Giang, KKH)
-- @first_acct+13 = 42/14 (Hải, 12th)
-- @first_acct+14 = 42/15 (Hải, 24th)
-- @first_acct+15 = 42/12 (Hải, 6th)
-- @first_acct+16 = 43/11 (Hương, 3th)
-- @first_acct+17 = 44/13 (Khánh, 9th)
-- @first_acct+18 = 44/10 (Khánh, KKH)
-- @first_acct+19 = 45/12 (Lan, 6th)
-- @first_acct+20 = 45/14 (Lan, 12th)
-- @first_acct+21 = 46/14 (Minh, 12th)
-- @first_acct+22 = 46/15 (Minh, 24th)
-- @first_acct+23 = 46/11 (Minh, 3th)
-- @first_acct+24 = 47/10 (Nga, KKH)
-- @first_acct+25 = 48/12 (Phúc, 6th)
-- @first_acct+26 = 48/14 (Phúc, 12th)
-- @first_acct+27 = 49/11 (Quỳnh, 3th)
-- @first_acct+28 = 50/14 (Sơn, 12th)
-- @first_acct+29 = 50/13 (Sơn, 9th)
-- @first_acct+30 = 51/10 (Thảo, KKH)
-- @first_acct+31 = 52/14 (Thanh, 12th)
-- @first_acct+32 = 52/12 (Thanh, 6th)
-- @first_acct+33 = 53/13 (Uyên, 9th)
-- @first_acct+34 = 54/12 (Việt, 6th)
-- @first_acct+35 = 55/14 (Xuân, 12th)
-- @first_acct+36 = 55/10 (Xuân, KKH)
-- @first_acct+37 = 37/12 CLOSED
-- @first_acct+38 = 39/11 CLOSED
-- @first_acct+39 = 43/14 CLOSED
-- @first_acct+40 = 47/12 CLOSED
-- @first_acct+41 = 51/11 CLOSED

-- === DEPOSIT TO WALLET (approved) ===
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at) VALUES
(36, NULL, NULL, 20000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-01-16 09:00:00'),
(36, NULL, NULL, 50000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-02-01 08:00:00'),
(37, NULL, NULL, 15000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-01-22 10:00:00'),
(38, NULL, NULL, 50000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-02-02 09:00:00'),
(38, NULL, NULL, 100000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-03-01 08:00:00'),
(40, NULL, NULL, 60000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-02-18 11:00:00'),
(40, NULL, NULL, 80000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-03-01 09:00:00'),
(42, NULL, NULL, 100000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-03-08 08:00:00'),
(42, NULL, NULL, 150000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-04-01 09:00:00'),
(46, NULL, NULL, 200000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-04-12 08:00:00'),
(46, NULL, NULL, 100000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-05-01 10:00:00'),
(50, NULL, NULL, 80000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-05-08 09:00:00'),
(52, NULL, NULL, 100000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-05-18 11:00:00'),
(55, NULL, NULL, 50000000.00, 'DEPOSIT_TO_WALLET', 'APPROVED', 0, 2, '2025-06-08 08:00:00');

-- === OPEN SAVINGS (approved) ===
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at) VALUES
(36, @first_acct+0, 10, 5000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-01-20 09:00:00'),
(36, @first_acct+1, 12, 20000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-02-01 10:00:00'),
(36, @first_acct+2, 14, 50000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-03-15 11:00:00'),
(37, @first_acct+3, 11, 10000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-01-25 14:00:00'),
(37, @first_acct+4, 10, 3000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-03-10 09:00:00'),
(38, @first_acct+5, 14, 100000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-02-05 10:00:00'),
(38, @first_acct+6, 13, 30000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-03-01 11:00:00'),
(38, @first_acct+7, 15, 50000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-04-01 08:00:00'),
(39, @first_acct+8, 10, 8000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-02-15 15:00:00'),
(40, @first_acct+9, 12, 40000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-02-20 09:00:00'),
(40, @first_acct+10, 14, 80000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-03-01 10:00:00'),
(41, @first_acct+11, 11, 15000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-03-05 14:00:00'),
(41, @first_acct+12, 10, 5000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-04-01 09:00:00'),
(42, @first_acct+13, 14, 150000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-03-10 08:00:00'),
(42, @first_acct+14, 15, 100000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-04-01 09:00:00'),
(42, @first_acct+15, 12, 50000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-05-01 10:00:00'),
(43, @first_acct+16, 11, 10000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-03-15 11:00:00'),
(44, @first_acct+17, 13, 25000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-03-25 13:00:00'),
(44, @first_acct+18, 10, 10000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-04-10 09:00:00'),
(45, @first_acct+19, 12, 20000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-04-05 08:00:00'),
(45, @first_acct+20, 14, 30000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-05-01 10:00:00'),
(46, @first_acct+21, 14, 200000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-04-15 09:00:00'),
(46, @first_acct+22, 15, 100000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-05-01 10:00:00'),
(46, @first_acct+23, 11, 50000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-06-01 11:00:00'),
(47, @first_acct+24, 10, 5000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-04-20 14:00:00'),
(48, @first_acct+25, 12, 30000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-04-25 09:00:00'),
(48, @first_acct+26, 14, 50000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-05-15 10:00:00'),
(49, @first_acct+27, 11, 15000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-05-05 08:30:00'),
(50, @first_acct+28, 14, 80000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-05-10 10:00:00'),
(50, @first_acct+29, 13, 40000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-06-01 11:00:00'),
(51, @first_acct+30, 10, 8000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-05-15 09:30:00'),
(52, @first_acct+31, 14, 100000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-05-20 11:00:00'),
(52, @first_acct+32, 12, 30000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-06-01 08:00:00'),
(53, @first_acct+33, 13, 25000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-05-25 13:00:00'),
(54, @first_acct+34, 12, 20000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-06-05 08:00:00'),
(55, @first_acct+35, 14, 60000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-06-10 09:00:00'),
(55, @first_acct+36, 10, 10000000.00, 'OPEN_SAVINGS', 'APPROVED', 0, 2, '2025-06-15 10:00:00');

-- === DEPOSIT TO SAVINGS (additional deposits) ===
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at) VALUES
(36, @first_acct+1, 12, 5000000.00, 'DEPOSIT_TO_SAVINGS', 'APPROVED', 0, 2, '2025-03-15 10:00:00'),
(38, @first_acct+5, 14, 20000000.00, 'DEPOSIT_TO_SAVINGS', 'APPROVED', 0, 2, '2025-04-10 09:00:00'),
(40, @first_acct+9, 12, 10000000.00, 'DEPOSIT_TO_SAVINGS', 'APPROVED', 0, 2, '2025-04-20 11:00:00'),
(42, @first_acct+13, 14, 30000000.00, 'DEPOSIT_TO_SAVINGS', 'APPROVED', 0, 2, '2025-05-15 08:00:00'),
(45, @first_acct+19, 12, 5000000.00, 'DEPOSIT_TO_SAVINGS', 'APPROVED', 0, 2, '2025-06-01 09:00:00'),
(46, @first_acct+21, 14, 50000000.00, 'DEPOSIT_TO_SAVINGS', 'APPROVED', 0, 2, '2025-06-10 10:00:00'),
(48, @first_acct+25, 12, 10000000.00, 'DEPOSIT_TO_SAVINGS', 'APPROVED', 0, 2, '2025-06-15 09:00:00');

-- === WITHDRAW FROM SAVINGS (non-term partial) ===
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at) VALUES
(36, @first_acct+0, NULL, 2000000.00, 'WITHDRAW_FROM_SAVINGS', 'APPROVED', 833.00, 2, '2025-03-01 10:00:00'),
(39, @first_acct+8, NULL, 3000000.00, 'WITHDRAW_FROM_SAVINGS', 'APPROVED', 1250.00, 2, '2025-04-15 14:00:00'),
(41, @first_acct+12, NULL, 1000000.00, 'WITHDRAW_FROM_SAVINGS', 'APPROVED', 278.00, 2, '2025-05-20 09:00:00'),
(44, @first_acct+18, NULL, 3000000.00, 'WITHDRAW_FROM_SAVINGS', 'APPROVED', 1250.00, 2, '2025-06-01 11:00:00'),
(47, @first_acct+24, NULL, 2000000.00, 'WITHDRAW_FROM_SAVINGS', 'APPROVED', 833.00, 2, '2025-06-10 15:00:00'),
(51, @first_acct+30, NULL, 2000000.00, 'WITHDRAW_FROM_SAVINGS', 'APPROVED', 556.00, 2, '2025-06-20 10:00:00');

-- === CLOSE SAVINGS (closed accounts) ===
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at) VALUES
(37, @first_acct+37, 12, 15000000.00, 'CLOSE_SAVINGS', 'APPROVED', 187500.00, 2, '2025-04-15 09:00:00'),
(39, @first_acct+38, 11, 10000000.00, 'CLOSE_SAVINGS', 'APPROVED', 112500.00, 2, '2025-04-25 10:00:00'),
(43, @first_acct+39, 14, 20000000.00, 'CLOSE_SAVINGS', 'APPROVED', 600000.00, 2, '2025-05-10 11:00:00'),
(47, @first_acct+40, 12, 10000000.00, 'CLOSE_SAVINGS', 'APPROVED', 130000.00, 2, '2025-05-20 14:00:00'),
(51, @first_acct+41, 11, 12000000.00, 'CLOSE_SAVINGS', 'APPROVED', 135000.00, 2, '2025-06-05 08:00:00');

-- === WITHDRAW FROM WALLET ===
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at) VALUES
(36, NULL, NULL, 5000000.00, 'WITHDRAW_FROM_WALLET', 'APPROVED', 0, 2, '2025-03-20 10:00:00'),
(37, NULL, NULL, 3000000.00, 'WITHDRAW_FROM_WALLET', 'APPROVED', 0, 2, '2025-04-01 11:00:00'),
(40, NULL, NULL, 10000000.00, 'WITHDRAW_FROM_WALLET', 'APPROVED', 0, 2, '2025-04-15 09:00:00'),
(42, NULL, NULL, 20000000.00, 'WITHDRAW_FROM_WALLET', 'APPROVED', 0, 2, '2025-05-20 14:00:00'),
(46, NULL, NULL, 15000000.00, 'WITHDRAW_FROM_WALLET', 'APPROVED', 0, 2, '2025-06-01 10:00:00');

-- === PENDING transactions (for staff to process) ===
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at) VALUES
(36, NULL, NULL, 30000000.00, 'DEPOSIT_TO_WALLET', 'PENDING', 0, NULL, NOW() - INTERVAL 2 HOUR),
(38, @first_acct+5, NULL, 10000000.00, 'DEPOSIT_TO_SAVINGS', 'PENDING', 0, NULL, NOW() - INTERVAL 1 HOUR),
(40, NULL, 14, 50000000.00, 'OPEN_SAVINGS', 'PENDING', 0, NULL, NOW() - INTERVAL 45 MINUTE),
(42, @first_acct+13, NULL, 20000000.00, 'WITHDRAW_FROM_SAVINGS', 'PENDING', 0, NULL, NOW() - INTERVAL 30 MINUTE),
(45, @first_acct+20, NULL, 30000000.00, 'CLOSE_SAVINGS', 'PENDING', 0, NULL, NOW() - INTERVAL 15 MINUTE),
(50, NULL, NULL, 5000000.00, 'WITHDRAW_FROM_WALLET', 'PENDING', 0, NULL, NOW() - INTERVAL 10 MINUTE),
(53, NULL, 12, 20000000.00, 'OPEN_SAVINGS', 'PENDING', 0, NULL, NOW() - INTERVAL 5 MINUTE);

-- === REJECTED transactions ===
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at) VALUES
(39, NULL, 14, 500000.00, 'OPEN_SAVINGS', 'REJECTED', 0, 2, '2025-03-01 10:00:00'),
(47, NULL, NULL, 100000000.00, 'WITHDRAW_FROM_WALLET', 'REJECTED', 0, 2, '2025-05-01 14:00:00'),
(51, @first_acct+30, NULL, 10000000.00, 'WITHDRAW_FROM_SAVINGS', 'REJECTED', 0, 2, '2025-06-01 09:00:00');

-- ==========================================
-- 3. SUMMARY
-- ==========================================
SELECT 'MOCK DATA LOADED SUCCESSFULLY' AS status;
SELECT COUNT(*) AS total_users FROM users;
SELECT COUNT(*) AS total_savings_accounts FROM savings_accounts;
SELECT COUNT(*) AS total_transactions FROM transactions;
SELECT COUNT(*) AS pending_transactions FROM transactions WHERE status = 'PENDING';
SELECT SUM(principal_balance) AS total_savings_principal FROM savings_accounts WHERE status = 'ACTIVE';
