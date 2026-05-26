#!/usr/bin/env python3
"""Seed realistic mock data into the Smart Savings database."""

import mysql.connector
from datetime import datetime, timedelta
import random

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="smart_savings",
    password="SmartSavings@2026!",
    database="modern_savings_db"
)
cursor = db.cursor()

# Product ID mapping (from existing DB):
# 10=Không kỳ hạn, 11=3 tháng, 12=6 tháng, 13=9 tháng, 14=12 tháng, 15=24 tháng
PRODUCT_KKH = 10
PRODUCT_3M = 11
PRODUCT_6M = 12
PRODUCT_9M = 13
PRODUCT_12M = 14
PRODUCT_24M = 15

STAFF_ID = 2  # staff@gmail.com

# Customer user IDs (from existing DB)
CUSTOMERS = {
    36: "Nguyễn Văn An",
    37: "Trần Thị Bình",
    38: "Lê Hoàng Cường",
    39: "Phạm Thị Dung",
    40: "Hoàng Văn Em",
    41: "Võ Thị Giang",
    42: "Đoàn Minh Hải",
    43: "Bùi Thị Hương",
    44: "Nguyễn Đức Khánh",
    45: "Lý Thị Lan",
    46: "Trương Văn Minh",
    47: "Đặng Thị Nga",
    48: "Phan Văn Phúc",
    49: "Nguyễn Thị Quỳnh",
    50: "Lê Văn Sơn",
    51: "Hồ Thị Thảo",
    52: "Vũ Đức Thanh",
    53: "Nguyễn Thị Uyên",
    54: "Trần Văn Việt",
    55: "Phạm Thị Xuân",
}

def dt(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

# ==========================================
# 1. SAVINGS ACCOUNTS
# ==========================================
accounts_to_create = [
    # (user_id, product_id, principal_balance, opened_at, status)
    (36, PRODUCT_KKH, 5_000_000, "2025-01-20 09:00:00", "ACTIVE"),
    (36, PRODUCT_6M, 20_000_000, "2025-02-01 10:00:00", "ACTIVE"),
    (36, PRODUCT_12M, 50_000_000, "2025-03-15 11:00:00", "ACTIVE"),
    (37, PRODUCT_3M, 10_000_000, "2025-01-25 14:00:00", "ACTIVE"),
    (37, PRODUCT_KKH, 3_000_000, "2025-03-10 09:00:00", "ACTIVE"),
    (38, PRODUCT_12M, 100_000_000, "2025-02-05 10:00:00", "ACTIVE"),
    (38, PRODUCT_9M, 30_000_000, "2025-03-01 11:00:00", "ACTIVE"),
    (38, PRODUCT_24M, 50_000_000, "2025-04-01 08:00:00", "ACTIVE"),
    (39, PRODUCT_KKH, 8_000_000, "2025-02-15 15:00:00", "ACTIVE"),
    (40, PRODUCT_6M, 40_000_000, "2025-02-20 09:00:00", "ACTIVE"),
    (40, PRODUCT_12M, 80_000_000, "2025-03-01 10:00:00", "ACTIVE"),
    (41, PRODUCT_3M, 15_000_000, "2025-03-05 14:00:00", "ACTIVE"),
    (41, PRODUCT_KKH, 5_000_000, "2025-04-01 09:00:00", "ACTIVE"),
    (42, PRODUCT_12M, 150_000_000, "2025-03-10 08:00:00", "ACTIVE"),
    (42, PRODUCT_24M, 100_000_000, "2025-04-01 09:00:00", "ACTIVE"),
    (42, PRODUCT_6M, 50_000_000, "2025-05-01 10:00:00", "ACTIVE"),
    (43, PRODUCT_3M, 10_000_000, "2025-03-15 11:00:00", "ACTIVE"),
    (44, PRODUCT_9M, 25_000_000, "2025-03-25 13:00:00", "ACTIVE"),
    (44, PRODUCT_KKH, 10_000_000, "2025-04-10 09:00:00", "ACTIVE"),
    (45, PRODUCT_6M, 20_000_000, "2025-04-05 08:00:00", "ACTIVE"),
    (45, PRODUCT_12M, 30_000_000, "2025-05-01 10:00:00", "ACTIVE"),
    (46, PRODUCT_12M, 200_000_000, "2025-04-15 09:00:00", "ACTIVE"),
    (46, PRODUCT_24M, 100_000_000, "2025-05-01 10:00:00", "ACTIVE"),
    (46, PRODUCT_3M, 50_000_000, "2025-06-01 11:00:00", "ACTIVE"),
    (47, PRODUCT_KKH, 5_000_000, "2025-04-20 14:00:00", "ACTIVE"),
    (48, PRODUCT_6M, 30_000_000, "2025-04-25 09:00:00", "ACTIVE"),
    (48, PRODUCT_12M, 50_000_000, "2025-05-15 10:00:00", "ACTIVE"),
    (49, PRODUCT_3M, 15_000_000, "2025-05-05 08:30:00", "ACTIVE"),
    (50, PRODUCT_12M, 80_000_000, "2025-05-10 10:00:00", "ACTIVE"),
    (50, PRODUCT_9M, 40_000_000, "2025-06-01 11:00:00", "ACTIVE"),
    (51, PRODUCT_KKH, 8_000_000, "2025-05-15 09:30:00", "ACTIVE"),
    (52, PRODUCT_12M, 100_000_000, "2025-05-20 11:00:00", "ACTIVE"),
    (52, PRODUCT_6M, 30_000_000, "2025-06-01 08:00:00", "ACTIVE"),
    (53, PRODUCT_9M, 25_000_000, "2025-05-25 13:00:00", "ACTIVE"),
    (54, PRODUCT_6M, 20_000_000, "2025-06-05 08:00:00", "ACTIVE"),
    (55, PRODUCT_12M, 60_000_000, "2025-06-10 09:00:00", "ACTIVE"),
    (55, PRODUCT_KKH, 10_000_000, "2025-06-15 10:00:00", "ACTIVE"),
    # CLOSED accounts
    (37, PRODUCT_6M, 0, "2025-01-10 09:00:00", "CLOSED"),
    (39, PRODUCT_3M, 0, "2025-01-20 10:00:00", "CLOSED"),
    (43, PRODUCT_12M, 0, "2025-02-01 11:00:00", "CLOSED"),
    (47, PRODUCT_6M, 0, "2025-02-15 14:00:00", "CLOSED"),
    (51, PRODUCT_3M, 0, "2025-03-01 08:00:00", "CLOSED"),
]

# Build account lookup: (user_id, product_id, status) -> account_id
account_map = {}
for uid, pid, bal, opened, status in accounts_to_create:
    cursor.execute(
        "INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES (%s, %s, %s, %s, %s)",
        (uid, pid, bal, dt(opened), status)
    )
    account_map[(uid, pid, status)] = cursor.lastrowid

db.commit()
print(f"[✓] Inserted {len(accounts_to_create)} savings accounts")

# Helper to get account_id
def acct(uid, pid, status="ACTIVE"):
    return account_map.get((uid, pid, status))

# ==========================================
# 2. TRANSACTIONS
# ==========================================
transactions = []

# DEPOSIT TO WALLET (approved)
wallet_deposits = [
    (36, 20_000_000, "2025-01-16 09:00:00"),
    (36, 50_000_000, "2025-02-01 08:00:00"),
    (37, 15_000_000, "2025-01-22 10:00:00"),
    (38, 50_000_000, "2025-02-02 09:00:00"),
    (38, 100_000_000, "2025-03-01 08:00:00"),
    (40, 60_000_000, "2025-02-18 11:00:00"),
    (40, 80_000_000, "2025-03-01 09:00:00"),
    (42, 100_000_000, "2025-03-08 08:00:00"),
    (42, 150_000_000, "2025-04-01 09:00:00"),
    (46, 200_000_000, "2025-04-12 08:00:00"),
    (46, 100_000_000, "2025-05-01 10:00:00"),
    (50, 80_000_000, "2025-05-08 09:00:00"),
    (52, 100_000_000, "2025-05-18 11:00:00"),
    (55, 50_000_000, "2025-06-08 08:00:00"),
]
for uid, amt, ts in wallet_deposits:
    transactions.append((uid, None, None, amt, "DEPOSIT_TO_WALLET", "APPROVED", 0, STAFF_ID, dt(ts)))

# OPEN SAVINGS (approved)
for uid, pid, bal, opened, status in accounts_to_create:
    if status == "ACTIVE":
        aid = acct(uid, pid, status)
        if aid:
            transactions.append((uid, aid, pid, bal, "OPEN_SAVINGS", "APPROVED", 0, STAFF_ID, dt(opened)))

# DEPOSIT TO SAVINGS (additional deposits)
extra_deposits = [
    (36, PRODUCT_6M, 5_000_000, "2025-03-15 10:00:00"),
    (38, PRODUCT_12M, 20_000_000, "2025-04-10 09:00:00"),
    (40, PRODUCT_6M, 10_000_000, "2025-04-20 11:00:00"),
    (42, PRODUCT_12M, 30_000_000, "2025-05-15 08:00:00"),
    (45, PRODUCT_6M, 5_000_000, "2025-06-01 09:00:00"),
    (46, PRODUCT_12M, 50_000_000, "2025-06-10 10:00:00"),
    (48, PRODUCT_6M, 10_000_000, "2025-06-15 09:00:00"),
]
for uid, pid, amt, ts in extra_deposits:
    aid = acct(uid, pid)
    if aid:
        transactions.append((uid, aid, pid, amt, "DEPOSIT_TO_SAVINGS", "APPROVED", 0, STAFF_ID, dt(ts)))

# WITHDRAW FROM SAVINGS (non-term partial)
withdrawals = [
    (36, PRODUCT_KKH, 2_000_000, 833, "2025-03-01 10:00:00"),
    (39, PRODUCT_KKH, 3_000_000, 1250, "2025-04-15 14:00:00"),
    (41, PRODUCT_KKH, 1_000_000, 278, "2025-05-20 09:00:00"),
    (44, PRODUCT_KKH, 3_000_000, 1250, "2025-06-01 11:00:00"),
    (47, PRODUCT_KKH, 2_000_000, 833, "2025-06-10 15:00:00"),
    (51, PRODUCT_KKH, 2_000_000, 556, "2025-06-20 10:00:00"),
]
for uid, pid, amt, interest, ts in withdrawals:
    aid = acct(uid, pid)
    if aid:
        transactions.append((uid, aid, None, amt, "WITHDRAW_FROM_SAVINGS", "APPROVED", interest, STAFF_ID, dt(ts)))

# CLOSE SAVINGS
closes = [
    (37, PRODUCT_6M, "CLOSED", 15_000_000, 187_500, "2025-04-15 09:00:00"),
    (39, PRODUCT_3M, "CLOSED", 10_000_000, 112_500, "2025-04-25 10:00:00"),
    (43, PRODUCT_12M, "CLOSED", 20_000_000, 600_000, "2025-05-10 11:00:00"),
    (47, PRODUCT_6M, "CLOSED", 10_000_000, 130_000, "2025-05-20 14:00:00"),
    (51, PRODUCT_3M, "CLOSED", 12_000_000, 135_000, "2025-06-05 08:00:00"),
]
for uid, pid, status, amt, interest, ts in closes:
    aid = acct(uid, pid, status)
    if aid:
        transactions.append((uid, aid, pid, amt, "CLOSE_SAVINGS", "APPROVED", interest, STAFF_ID, dt(ts)))

# WITHDRAW FROM WALLET
wallet_withdrawals = [
    (36, 5_000_000, "2025-03-20 10:00:00"),
    (37, 3_000_000, "2025-04-01 11:00:00"),
    (40, 10_000_000, "2025-04-15 09:00:00"),
    (42, 20_000_000, "2025-05-20 14:00:00"),
    (46, 15_000_000, "2025-06-01 10:00:00"),
]
for uid, amt, ts in wallet_withdrawals:
    transactions.append((uid, None, None, amt, "WITHDRAW_FROM_WALLET", "APPROVED", 0, STAFF_ID, dt(ts)))

# PENDING transactions
now = datetime.now()
pending = [
    (36, None, None, 30_000_000, "DEPOSIT_TO_WALLET", "PENDING", 0, None, now - timedelta(hours=2)),
    (38, acct(38, PRODUCT_12M), None, 10_000_000, "DEPOSIT_TO_SAVINGS", "PENDING", 0, None, now - timedelta(hours=1)),
    (40, None, PRODUCT_12M, 50_000_000, "OPEN_SAVINGS", "PENDING", 0, None, now - timedelta(minutes=45)),
    (42, acct(42, PRODUCT_12M), None, 20_000_000, "WITHDRAW_FROM_SAVINGS", "PENDING", 0, None, now - timedelta(minutes=30)),
    (45, acct(45, PRODUCT_12M), None, 30_000_000, "CLOSE_SAVINGS", "PENDING", 0, None, now - timedelta(minutes=15)),
    (50, None, None, 5_000_000, "WITHDRAW_FROM_WALLET", "PENDING", 0, None, now - timedelta(minutes=10)),
    (53, None, PRODUCT_6M, 20_000_000, "OPEN_SAVINGS", "PENDING", 0, None, now - timedelta(minutes=5)),
]
for uid, aid, tpid, amt, ttype, status, interest, proc, ts in pending:
    transactions.append((uid, aid, tpid, amt, ttype, status, interest, proc, ts))

# REJECTED transactions
rejected = [
    (39, None, PRODUCT_12M, 500_000, "OPEN_SAVINGS", "REJECTED", 0, STAFF_ID, "2025-03-01 10:00:00"),
    (47, None, None, 100_000_000, "WITHDRAW_FROM_WALLET", "REJECTED", 0, STAFF_ID, "2025-05-01 14:00:00"),
    (51, acct(51, PRODUCT_KKH), None, 10_000_000, "WITHDRAW_FROM_SAVINGS", "REJECTED", 0, STAFF_ID, "2025-06-01 09:00:00"),
]
for uid, aid, tpid, amt, ttype, status, interest, proc, ts in rejected:
    transactions.append((uid, aid, tpid, amt, ttype, status, interest, proc, dt(ts) if isinstance(ts, str) else ts))

# Insert all transactions
insert_sql = """
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
cursor.executemany(insert_sql, transactions)
db.commit()
print(f"[✓] Inserted {len(transactions)} transactions")

# ==========================================
# 3. SUMMARY
# ==========================================
cursor.execute("SELECT COUNT(*) FROM savings_accounts")
print(f"\n📊 Total savings accounts: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM transactions")
print(f"📊 Total transactions: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM transactions WHERE status='PENDING'")
print(f"📊 Pending transactions: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM transactions WHERE status='APPROVED'")
print(f"📊 Approved transactions: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM transactions WHERE status='REJECTED'")
print(f"📊 Rejected transactions: {cursor.fetchone()[0]}")
cursor.execute("SELECT SUM(principal_balance) FROM savings_accounts WHERE status='ACTIVE'")
total_principal = cursor.fetchone()[0]
print(f"📊 Total active principal: {total_principal:,.0f} VND")

cursor.close()
db.close()
print("\n✅ Mock data seeded successfully!")
