#!/usr/bin/env python3
"""Seed realistic mock data into the Smart Savings database.
   Data spans Jan 2025 - May 2026 with varied transaction volumes
   to create natural up/down analytics charts (stock-chart style).
"""

import mysql.connector
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

random.seed(42)  # Reproducible

db = mysql.connector.connect(
    host="localhost",
    user="smart_savings",
    password="SmartSavings@2026!",
    database="modern_savings_db"
)
cursor = db.cursor()

# Product IDs (from existing DB): only 3 active products are used.
PRODUCT_KKH = 10  # Không kỳ hạn 0.5%
PRODUCT_3M  = 11  # 3 tháng 4.5%
PRODUCT_6M  = 12  # 6 tháng 5.2%

STAFF_ID = 2

# Customer user IDs
CUSTOMERS = list(range(36, 56))  # 36-55


def ensure_mock_users():
    password_hash = generate_password_hash('Password123!', method='pbkdf2:sha256')
    users = [
        (1, 'admin@gmail.com', generate_password_hash('admin123', method='pbkdf2:sha256'), 'System Admin', 'ADMIN000001', '9000000001', 'ADMIN'),
        (2, 'staff@gmail.com', generate_password_hash('staff123', method='pbkdf2:sha256'), 'Default Staff', 'STAFF000001', '9000000002', 'STAFF'),
        (34, 'staff2@gmail.com', generate_password_hash('staff123', method='pbkdf2:sha256'), 'Backup Staff', 'STAFF000034', '9000000034', 'STAFF'),
        (36, 'an@test.local', password_hash, 'An', 'CUST000036', '9000000036', 'CUSTOMER'),
        (37, 'binh@test.local', password_hash, 'Bình', 'CUST000037', '9000000037', 'CUSTOMER'),
        (38, 'cuong@test.local', password_hash, 'Cường', 'CUST000038', '9000000038', 'CUSTOMER'),
        (39, 'dung@test.local', password_hash, 'Dung', 'CUST000039', '9000000039', 'CUSTOMER'),
        (40, 'em@test.local', password_hash, 'Em', 'CUST000040', '9000000040', 'CUSTOMER'),
        (41, 'giang@test.local', password_hash, 'Giang', 'CUST000041', '9000000041', 'CUSTOMER'),
        (42, 'hai@test.local', password_hash, 'Hải', 'CUST000042', '9000000042', 'CUSTOMER'),
        (43, 'huong@test.local', password_hash, 'Hương', 'CUST000043', '9000000043', 'CUSTOMER'),
        (44, 'khanh@test.local', password_hash, 'Khánh', 'CUST000044', '9000000044', 'CUSTOMER'),
        (45, 'lan@test.local', password_hash, 'Lan', 'CUST000045', '9000000045', 'CUSTOMER'),
        (46, 'minh@test.local', password_hash, 'Minh', 'CUST000046', '9000000046', 'CUSTOMER'),
        (47, 'nga@test.local', password_hash, 'Nga', 'CUST000047', '9000000047', 'CUSTOMER'),
        (48, 'phuc@test.local', password_hash, 'Phúc', 'CUST000048', '9000000048', 'CUSTOMER'),
        (49, 'quynh@test.local', password_hash, 'Quỳnh', 'CUST000049', '9000000049', 'CUSTOMER'),
        (50, 'son@test.local', password_hash, 'Sơn', 'CUST000050', '9000000050', 'CUSTOMER'),
        (51, 'thao@test.local', password_hash, 'Thảo', 'CUST000051', '9000000051', 'CUSTOMER'),
        (52, 'thanh@test.local', password_hash, 'Thanh', 'CUST000052', '9000000052', 'CUSTOMER'),
        (53, 'uyen@test.local', password_hash, 'Uyên', 'CUST000053', '9000000053', 'CUSTOMER'),
        (54, 'viet@test.local', password_hash, 'Việt', 'CUST000054', '9000000054', 'CUSTOMER'),
        (55, 'xuan@test.local', password_hash, 'Xuân', 'CUST000055', '9000000055', 'CUSTOMER'),
    ]

    cursor.executemany(
        """
        INSERT IGNORE INTO users
            (user_id, email, password_hash, full_name, identity_card, account_number, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        users,
    )
    db.commit()


def ensure_mock_products():
    products = [
        (PRODUCT_KKH, 'Không kỳ hạn', 0, 0.50, 15, 'Rút linh hoạt sau thời gian giữ tối thiểu.'),
        (PRODUCT_3M, 'Tiết kiệm 3 tháng', 3, 5.00, 0, 'Kỳ hạn 3 tháng.'),
        (PRODUCT_6M, 'Tiết kiệm 6 tháng', 6, 5.50, 0, 'Kỳ hạn 6 tháng.'),
        (PRODUCT_9M, 'Tiết kiệm 9 tháng', 9, 5.80, 0, 'Kỳ hạn 9 tháng.'),
        (PRODUCT_12M, 'Tiết kiệm 12 tháng', 12, 6.00, 0, 'Kỳ hạn 12 tháng.'),
        (PRODUCT_24M, 'Tiết kiệm 24 tháng', 24, 6.50, 0, 'Kỳ hạn 24 tháng.'),
    ]

    cursor.executemany(
        """
        INSERT IGNORE INTO savings_products
            (product_id, name, term_months, interest_rate, min_days_hold, is_active, description)
        VALUES (%s, %s, %s, %s, %s, TRUE, %s)
        """,
        products,
    )
    db.commit()

def dt(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

def rand_time(day_str):
    """Random time within a day."""
    h = random.randint(7, 21)
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return dt(f"{day_str} {h:02d}:{m:02d}:{s:02d}")

def rand_amount(base, variance=0.4):
    """Random amount around base with variance."""
    factor = 1.0 + random.uniform(-variance, variance)
    return round(base * factor / 100000) * 100000  # Round to 100k

# ==========================================
# 1. CLEAR OLD MOCK DATA (only for users 36-55)
# ==========================================
ensure_mock_users()
ensure_mock_products()
cursor.execute("DELETE FROM transactions WHERE user_id >= 36")
cursor.execute("DELETE FROM savings_accounts WHERE user_id >= 36")
db.commit()
print("[✓] Cleared old mock data for users 36-55")

# ==========================================
# 2. SAVINGS ACCOUNTS — spread across 2025-2026
# ==========================================
# Each customer gets 1-4 accounts opened at different times
accounts_to_create = []

# Monthly account opening schedule (varied for realistic chart)
# Format: (month_key, count_of_new_accounts)
# Peaks: Mar 2025 (Tet bonus), Sep 2025 (back to school savings), Jan 2026 (year-end bonus)
# Valleys: May 2025, Nov 2025, Apr 2026
opening_schedule = {
    "2025-01": 3, "2025-02": 2, "2025-03": 6, "2025-04": 3,
    "2025-05": 1, "2025-06": 2, "2025-07": 3, "2025-08": 2,
    "2025-09": 5, "2025-10": 2, "2025-11": 1, "2025-12": 4,
    "2026-01": 7, "2026-02": 3, "2026-03": 4, "2026-04": 1,
    "2026-05": 2,
}

product_choices = [PRODUCT_KKH, PRODUCT_3M, PRODUCT_6M]
product_weights = [0.25, 0.35, 0.40]

acct_idx = 0
for month_key, count in opening_schedule.items():
    for _ in range(count):
        uid = random.choice(CUSTOMERS)
        pid = random.choices(product_choices, weights=product_weights, k=1)[0]
        day = random.randint(1, 28)
        opened = f"{month_key}-{day:02d}"
        base_amounts = {
            PRODUCT_KKH: 5_000_000,
            PRODUCT_3M: 10_000_000,
            PRODUCT_6M: 20_000_000,
        }
        bal = rand_amount(base_amounts[pid], 0.5)
        bal = max(bal, 1_000_000)
        accounts_to_create.append((uid, pid, bal, opened, "ACTIVE"))
        acct_idx += 1

# Add some CLOSED accounts (historical)
closed_accounts = [
    (37, PRODUCT_6M, 0, "2025-01-10", "CLOSED"),
    (39, PRODUCT_3M, 0, "2025-02-20", "CLOSED"),
    (43, PRODUCT_6M, 0, "2025-03-01", "CLOSED"),
    (47, PRODUCT_6M, 0, "2025-06-15", "CLOSED"),
    (51, PRODUCT_3M, 0, "2025-08-01", "CLOSED"),
    (36, PRODUCT_3M, 0, "2025-10-10", "CLOSED"),
    (40, PRODUCT_6M, 0, "2025-12-01", "CLOSED"),
    (45, PRODUCT_6M, 0, "2026-01-15", "CLOSED"),
]
accounts_to_create.extend(closed_accounts)

# Insert accounts and build lookup
account_map = {}
for uid, pid, bal, opened, status in accounts_to_create:
    cursor.execute(
        "INSERT INTO savings_accounts (user_id, product_id, principal_balance, opened_at, status) VALUES (%s, %s, %s, %s, %s)",
        (uid, pid, bal, rand_time(opened), status)
    )
    account_map[(uid, pid, status, opened[:7])] = cursor.lastrowid

db.commit()
print(f"[✓] Inserted {len(accounts_to_create)} savings accounts")

def find_acct(uid, pid=None, status="ACTIVE"):
    """Find an account_id for a user."""
    for (u, p, s, m), aid in account_map.items():
        if u == uid and s == status:
            if pid is None or p == pid:
                return aid, p
    return None, None

# ==========================================
# 3. TRANSACTIONS — spread 2025-2026, varied volumes
# ==========================================
transactions = []

# Monthly transaction volume profile (creates up/down chart pattern)
# Higher = more transactions that month = higher total amounts
monthly_volume = {
    # 2025 — natural fluctuation
    "2025-01": 0.6,   # Post-holiday slow
    "2025-02": 0.9,   # Tet bonus → deposits spike
    "2025-03": 1.2,   # Peak — people save Tet money
    "2025-04": 0.7,   # Drop off
    "2025-05": 0.4,   # Valley — summer spending
    "2025-06": 0.5,   # Still low
    "2025-07": 0.8,   # Recovery
    "2025-08": 0.6,   # Dip
    "2025-09": 1.1,   # Back-to-school savings
    "2025-10": 0.7,   # Decline
    "2025-11": 0.5,   # Valley
    "2025-12": 1.0,   # Year-end bonus deposits
    # 2026 — continued fluctuation
    "2026-01": 1.4,   # BIG peak — Tet 2026
    "2026-02": 1.3,   # Still high — Tet savings
    "2026-03": 0.8,   # Cooling down
    "2026-04": 0.5,   # Valley
    "2026-05": 0.9,   # Recovery (partial month)
}

# Generate wallet deposits per month
for month_key, volume in monthly_volume.items():
    num_deposits = max(1, int(8 * volume))
    for _ in range(num_deposits):
        uid = random.choice(CUSTOMERS)
        day = random.randint(1, 28)
        base = random.choice([5_000_000, 10_000_000, 20_000_000, 30_000_000, 50_000_000])
        amt = rand_amount(base * volume, 0.3)
        amt = max(amt, 1_000_000)
        ts = rand_time(f"{month_key}-{day:02d}")
        transactions.append((uid, None, None, amt, "DEPOSIT_TO_WALLET", "APPROVED", 0, STAFF_ID, ts))

print(f"[✓] Generated {len(transactions)} wallet deposits")

# Generate OPEN_SAVINGS transactions from the accounts we created
open_tx_count = 0
for uid, pid, bal, opened, status in accounts_to_create:
    if status == "ACTIVE":
        ts = rand_time(opened)
        transactions.append((uid, None, pid, bal, "OPEN_SAVINGS", "APPROVED", 0, STAFF_ID, ts))
        open_tx_count += 1

print(f"[✓] Generated {open_tx_count} open savings transactions")

# Generate additional deposits to savings (spread across months)
extra_deposit_count = 0
for month_key, volume in monthly_volume.items():
    num_extra = max(0, int(4 * volume))
    for _ in range(num_extra):
        uid = random.choice(CUSTOMERS)
        aid, pid = find_acct(uid, status="ACTIVE")
        if aid and pid:
            day = random.randint(1, 28)
            base = random.choice([2_000_000, 5_000_000, 10_000_000, 20_000_000])
            amt = rand_amount(base * volume, 0.3)
            amt = max(amt, 500_000)
            ts = rand_time(f"{month_key}-{day:02d}")
            transactions.append((uid, aid, pid, amt, "DEPOSIT_TO_SAVINGS", "APPROVED", 0, STAFF_ID, ts))
            extra_deposit_count += 1

print(f"[✓] Generated {extra_deposit_count} additional deposits")

# Generate withdrawals (varied — more in low-volume months when people need cash)
withdrawal_count = 0
for month_key, volume in monthly_volume.items():
    # Inverse relationship: low deposit months = higher withdrawal tendency
    withdrawal_volume = max(0.2, 1.2 - volume)
    num_withdrawals = max(0, int(3 * withdrawal_volume))
    for _ in range(num_withdrawals):
        uid = random.choice(CUSTOMERS)
        aid, pid = find_acct(uid, PRODUCT_KKH, "ACTIVE")
        if not aid:
            aid, pid = find_acct(uid, status="ACTIVE")
        if aid:
            day = random.randint(1, 28)
            base = random.choice([1_000_000, 2_000_000, 5_000_000, 10_000_000])
            amt = rand_amount(base, 0.3)
            amt = max(amt, 500_000)
            interest = round(amt * 0.005 * random.uniform(0.5, 2.0))
            ts = rand_time(f"{month_key}-{day:02d}")
            transactions.append((uid, aid, None, amt, "WITHDRAW_FROM_SAVINGS", "APPROVED", interest, STAFF_ID, ts))
            withdrawal_count += 1

print(f"[✓] Generated {withdrawal_count} savings withdrawals")

# Wallet withdrawals
wallet_withdraw_count = 0
for month_key, volume in monthly_volume.items():
    num = max(0, int(2 * (1.0 - volume * 0.3)))
    for _ in range(num):
        uid = random.choice(CUSTOMERS)
        day = random.randint(1, 28)
        base = random.choice([2_000_000, 5_000_000, 10_000_000])
        amt = rand_amount(base, 0.3)
        amt = max(amt, 500_000)
        ts = rand_time(f"{month_key}-{day:02d}")
        transactions.append((uid, None, None, amt, "WITHDRAW_FROM_WALLET", "APPROVED", 0, STAFF_ID, ts))
        wallet_withdraw_count += 1

print(f"[✓] Generated {wallet_withdraw_count} wallet withdrawals")

# Close savings transactions
close_count = 0
for uid, pid, bal, opened, status in accounts_to_create:
    if status == "CLOSED":
        # Close date = 3-6 months after open
        open_dt = datetime.strptime(opened, "%Y-%m-%d")
        close_dt = open_dt + timedelta(days=random.randint(90, 180))
        if close_dt > datetime(2026, 5, 26):
            close_dt = datetime(2026, 5, 20)
        base = random.choice([10_000_000, 15_000_000, 20_000_000])
        amt = rand_amount(base, 0.3)
        interest = round(amt * random.uniform(0.01, 0.04))
        ts = rand_time(close_dt.strftime("%Y-%m-%d"))
        transactions.append((uid, None, pid, amt, "CLOSE_SAVINGS", "APPROVED", interest, STAFF_ID, ts))
        close_count += 1

print(f"[✓] Generated {close_count} close savings transactions")

# PENDING transactions (recent — last few hours)
now = datetime.now()
pending = [
    (36, None, None, 30_000_000, "DEPOSIT_TO_WALLET", "PENDING", 0, None, now - timedelta(hours=2)),
    (38, None, None, 10_000_000, "DEPOSIT_TO_SAVINGS", "PENDING", 0, None, now - timedelta(hours=1)),
    (40, None, PRODUCT_6M, 50_000_000, "OPEN_SAVINGS", "PENDING", 0, None, now - timedelta(minutes=45)),
    (42, None, None, 20_000_000, "WITHDRAW_FROM_SAVINGS", "PENDING", 0, None, now - timedelta(minutes=30)),
    (45, None, None, 30_000_000, "CLOSE_SAVINGS", "PENDING", 0, None, now - timedelta(minutes=15)),
    (50, None, None, 5_000_000, "WITHDRAW_FROM_WALLET", "PENDING", 0, None, now - timedelta(minutes=10)),
    (53, None, PRODUCT_6M, 20_000_000, "OPEN_SAVINGS", "PENDING", 0, None, now - timedelta(minutes=5)),
]
transactions.extend(pending)

# REJECTED transactions (spread across timeline)
rejected_months = ["2025-03", "2025-06", "2025-09", "2025-12", "2026-02", "2026-04"]
for rm in rejected_months:
    uid = random.choice(CUSTOMERS)
    day = random.randint(1, 28)
    base = random.choice([500_000, 1_000_000, 5_000_000])
    amt = rand_amount(base, 0.2)
    ttype = random.choice(["OPEN_SAVINGS", "WITHDRAW_FROM_WALLET", "WITHDRAW_FROM_SAVINGS"])
    ts = rand_time(f"{rm}-{day:02d}")
    transactions.append((uid, None, None, amt, ttype, "REJECTED", 0, STAFF_ID, ts))

# ==========================================
# 4. INSERT ALL TRANSACTIONS
# ==========================================
insert_sql = """
INSERT INTO transactions (user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount, processed_by, created_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
cursor.executemany(insert_sql, transactions)
db.commit()
print(f"\n[✓] Inserted {len(transactions)} transactions total")

# ==========================================
# 5. SUMMARY
# ==========================================
cursor.execute("SELECT COUNT(*) FROM savings_accounts WHERE user_id >= 36")
print(f"\n📊 Savings accounts (mock): {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id >= 36")
print(f"📊 Transactions (mock): {cursor.fetchone()[0]}")

for status in ["APPROVED", "PENDING", "REJECTED"]:
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount),0) FROM transactions WHERE user_id >= 36 AND status = %s", (status,))
    cnt, total = cursor.fetchone()
    print(f"📊 {status}: {cnt} transactions, total: {total:,.0f} VND")

cursor.execute("SELECT DATE_FORMAT(created_at, '%%Y-%%m') AS month, COUNT(*) AS cnt, SUM(amount) AS total FROM transactions WHERE user_id >= 36 AND status='APPROVED' GROUP BY month ORDER BY month")
print("\n📊 Monthly transaction distribution:")
for row in cursor.fetchall():
    print(f"   {row[0]}: {row[1]} txns, {row[2]:,.0f} VND")

cursor.execute("SELECT SUM(principal_balance) FROM savings_accounts WHERE user_id >= 36 AND status='ACTIVE'")
total_principal = cursor.fetchone()[0] or 0
print(f"\n📊 Total active principal: {total_principal:,.0f} VND")

cursor.close()
db.close()
print("\n✅ Mock data seeded successfully! (Jan 2025 - May 2026)")
