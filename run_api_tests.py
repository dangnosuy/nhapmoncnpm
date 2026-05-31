import requests
import json
import time
import random
import threading
import sys

BASE_URL = "http://localhost:5000/api"
BUGS = []

def log_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {name} {f'- {details}' if details else ''}")
    if not passed:
        BUGS.append(f"**FAIL:** {name}\n   - Details: {details}")
    return passed

def register_customer(email_prefix):
    email = f"{email_prefix}_{int(time.time())}@test.com"
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Test User",
        "identity_card": f"ID{int(time.time())}{random.randint(1000,9999)}"
    })
    return res.json() if res.status_code == 201 else None, email, "Password123!"

def login(email, password):
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    return res.json().get("token") if res.status_code == 200 else None

def test_auth_and_rbac():
    print("\n--- Phase 1: Auth & RBAC ---")

    # 1. Register & Login
    data, email, pw = register_customer("rbac")
    log_test("Customer Registration", data is not None, f"Email: {email}")
    token_cust = login(email, pw)
    log_test("Customer Login", token_cust is not None)

    token_admin = login("admin@gmail.com", "admin123")
    token_staff = login("staff@gmail.com", "staff123")
    log_test("Staff & Admin Login", token_admin and token_staff)

    # 2. RBAC Checks
    # Customer accessing Admin endpoint
    res = requests.get(f"{BASE_URL}/admin/dashboard", headers={"Authorization": f"Bearer {token_cust}"})
    log_test("RBAC: Customer accessing Admin endpoint", res.status_code == 403, f"Status Code: {res.status_code}")

    # Customer accessing Staff endpoint
    res = requests.get(f"{BASE_URL}/transactions", headers={"Authorization": f"Bearer {token_cust}"})
    log_test("RBAC: Customer accessing Staff endpoint", res.status_code == 403, f"Status Code: {res.status_code}")

    # Staff accessing Admin endpoint
    res = requests.post(f"{BASE_URL}/admin/users", json={}, headers={"Authorization": f"Bearer {token_staff}"})
    log_test("RBAC: Staff accessing Admin endpoint", res.status_code == 403, f"Status Code: {res.status_code}")

    return token_cust, token_staff, token_admin

def test_transfers(token_a):
    print("\n--- Phase 2: Transfers ---")
    data_b, email_b, pw_b = register_customer("trans_b")
    token_b = login(email_b, pw_b)

    res_a_me = requests.get(f"{BASE_URL}/client/me", headers={"Authorization": f"Bearer {token_a}"}).json()
    res_b_me = requests.get(f"{BASE_URL}/client/me", headers={"Authorization": f"Bearer {token_b}"}).json()

    acc_a = res_a_me["user"]["account_number"]
    acc_b = res_b_me["user"]["account_number"]

    # 1. Normal Transfer
    res = requests.post(f"{BASE_URL}/client/transfers", json={
        "to_account_number": acc_b,
        "amount": 500000
    }, headers={"Authorization": f"Bearer {token_a}"})
    log_test("Transfer: Normal (A -> B)", res.status_code == 201)

    # 2. Self Transfer
    res = requests.post(f"{BASE_URL}/client/transfers", json={
        "to_account_number": acc_a,
        "amount": 100000
    }, headers={"Authorization": f"Bearer {token_a}"})
    log_test("Transfer: Self Transfer", res.status_code == 400, f"Expected 400, got {res.status_code}. Response: {res.text}")

    # 3. Negative Amount Transfer
    res = requests.post(f"{BASE_URL}/client/transfers", json={
        "to_account_number": acc_b,
        "amount": -50000
    }, headers={"Authorization": f"Bearer {token_a}"})
    log_test("Transfer: Negative Amount", res.status_code == 400, f"Expected 400, got {res.status_code}. Response: {res.text}")

    # 4. Zero Amount Transfer
    res = requests.post(f"{BASE_URL}/client/transfers", json={
        "to_account_number": acc_b,
        "amount": 0
    }, headers={"Authorization": f"Bearer {token_a}"})
    log_test("Transfer: Zero Amount", res.status_code == 400, f"Expected 400, got {res.status_code}. Response: {res.text}")

    # 5. Amount > Balance
    res = requests.post(f"{BASE_URL}/client/transfers", json={
        "to_account_number": acc_b,
        "amount": 99999999999
    }, headers={"Authorization": f"Bearer {token_a}"})
    log_test("Transfer: Exceed Balance", res.status_code == 400, f"Expected 400, got {res.status_code}. Response: {res.text}")

def test_savings_and_business_rules(token_cust, token_staff, token_admin):
    print("\n--- Phase 5: Business Rules (QD1, QD2, QD3) ---")

    # GET products
    prods = requests.get(f"{BASE_URL}/client/savings-products", headers={"Authorization": f"Bearer {token_cust}"}).json()["products"]
    term_product = next((p for p in prods if p["term_months"] > 0), None)
    non_term_product = next((p for p in prods if p["term_months"] == 0), None)

    if not term_product or not non_term_product:
        print("Missing products! Exiting.")
        return

    # QD1: Minimum amount check
    print("\n--- Testing QD1 (Min Open Amount) ---")
    res = requests.post(f"{BASE_URL}/client/open-savings", json={
        "product_id": term_product["product_id"],
        "amount": 50000 # Default is 1M
    }, headers={"Authorization": f"Bearer {token_cust}"})
    log_test("QD1: Open Savings with amount < Min (50k)", res.status_code == 400, f"Expected 400, got {res.status_code}. Response: {res.text}")

    # Normal Open Savings
    res = requests.post(f"{BASE_URL}/client/open-savings", json={
        "product_id": term_product["product_id"],
        "amount": 1000000
    }, headers={"Authorization": f"Bearer {token_cust}"})
    log_test("Open Savings: Term Account (1M)", res.status_code == 201)
    tx_id_term = res.json().get("transaction_id")

    res = requests.post(f"{BASE_URL}/client/open-savings", json={
        "product_id": non_term_product["product_id"],
        "amount": 1000000
    }, headers={"Authorization": f"Bearer {token_cust}"})
    log_test("Open Savings: Non-Term Account (1M)", res.status_code == 201)
    tx_id_nonterm = res.json().get("transaction_id")

    # Approve both
    requests.put(f"{BASE_URL}/transactions/{tx_id_term}/approve", headers={"Authorization": f"Bearer {token_staff}"})
    requests.put(f"{BASE_URL}/transactions/{tx_id_nonterm}/approve", headers={"Authorization": f"Bearer {token_staff}"})

    # Fetch accounts
    accs = requests.get(f"{BASE_URL}/client/savings-accounts", headers={"Authorization": f"Bearer {token_cust}"}).json()["accounts"]
    acc_term = next((a for a in accs if a["term_months"] > 0), None)
    acc_nonterm = next((a for a in accs if a["term_months"] == 0), None)

    # QD2: Additional deposits
    print("\n--- Testing QD2 (Additional Deposits) ---")
    res = requests.post(f"{BASE_URL}/client/savings-accounts/{acc_term['account_id']}/deposit-requests", json={
        "amount": 500000
    }, headers={"Authorization": f"Bearer {token_cust}"})
    log_test("QD2: Deposit to Term Account (not matured)", res.status_code == 400, f"Expected 400, got {res.status_code}. Response: {res.text}")

    res = requests.post(f"{BASE_URL}/client/savings-accounts/{acc_nonterm['account_id']}/deposit-requests", json={
        "amount": 500000
    }, headers={"Authorization": f"Bearer {token_cust}"})
    log_test("QD2: Deposit to Non-Term Account", res.status_code == 201, f"Expected 201, got {res.status_code}. Response: {res.text}")

    # Reject the nonterm deposit to clean state
    tx_dep = res.json().get("transaction_id")
    if tx_dep:
        requests.put(f"{BASE_URL}/transactions/{tx_dep}/reject", headers={"Authorization": f"Bearer {token_staff}"})

    # QD3: Withdraw / Close Rules
    print("\n--- Testing QD3 (Withdraw & Close Rules) ---")
    # Partial withdraw from Term Account
    res = requests.post(f"{BASE_URL}/client/savings-accounts/{acc_term['account_id']}/withdraw-requests", json={
        "amount": 100000
    }, headers={"Authorization": f"Bearer {token_cust}"})
    log_test("QD3: Partial Withdraw from Term Account", res.status_code == 400, f"Expected 400, got {res.status_code}. Response: {res.text}")

    # Early Close Term Account
    res = requests.post(f"{BASE_URL}/client/close-savings/{acc_term['account_id']}", headers={"Authorization": f"Bearer {token_cust}"})
    data = res.json()
    log_test("QD3: Early Close Term Account", res.status_code == 201 and data.get("is_early_withdrawal") == True, f"Got: {data}")
    tx_close_term = data.get("transaction_id")
    if tx_close_term:
        requests.put(f"{BASE_URL}/transactions/{tx_close_term}/approve", headers={"Authorization": f"Bearer {token_staff}"})

    # Partial withdraw from Non-Term Account (min days check)
    res = requests.post(f"{BASE_URL}/client/savings-accounts/{acc_nonterm['account_id']}/withdraw-requests", json={
        "amount": 100000
    }, headers={"Authorization": f"Bearer {token_cust}"})
    # Since it was just opened today, held_days = 0. Min is 15.
    log_test("QD3: Withdraw Non-Term before 15 days", res.status_code == 400, f"Expected 400, got {res.status_code}. Response: {res.text}")

def test_race_conditions(token_cust):
    print("\n--- Phase 7: Race Conditions ---")
    # Try to transfer same money concurrently
    accs = requests.get(f"{BASE_URL}/client/me", headers={"Authorization": f"Bearer {token_cust}"}).json()
    bal = accs["user"]["wallet_balance"]

    data_b, email_b, pw_b = register_customer("race_b")
    token_b = login(email_b, pw_b)
    acc_b = requests.get(f"{BASE_URL}/client/me", headers={"Authorization": f"Bearer {token_b}"}).json()["user"]["account_number"]

    results = []
    def do_transfer():
        res = requests.post(f"{BASE_URL}/client/transfers", json={
            "to_account_number": acc_b,
            "amount": bal # Transfer entire balance
        }, headers={"Authorization": f"Bearer {token_cust}"})
        results.append(res.status_code)

    t1 = threading.Thread(target=do_transfer)
    t2 = threading.Thread(target=do_transfer)
    t1.start(); t2.start()
    t1.join(); t2.join()

    successes = results.count(201)
    log_test("Race Condition: Concurrent Double Transfer", successes == 1, f"Expected exactly 1 success, got {successes}. Status codes: {results}")

def run():
    print("Starting Comprehensive API Tests...")
    t_cust, t_staff, t_admin = test_auth_and_rbac()
    if t_cust and t_staff and t_admin:
        test_transfers(t_cust)
        test_savings_and_business_rules(t_cust, t_staff, t_admin)
        test_race_conditions(t_cust)
    else:
        print("Failed to get tokens, aborting.")

    print("\n====================")
    print(f"Bugs Found: {len(BUGS)}")
    for b in BUGS:
        print(b)

    with open("TEST_RESULTS.md", "w") as f:
        f.write("# Automated API Test Results\n\n")
        if BUGS:
            f.write("## 🚨 Bugs Found\n")
            for b in BUGS:
                f.write(f"- {b}\n")
        else:
            f.write("## ✅ No bugs found in automated tests!\n")

if __name__ == '__main__':
    run()
