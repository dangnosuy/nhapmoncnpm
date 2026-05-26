import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000/api'

# 1. Register a new customer
customer_email = f"cust_{int(time.time())}@test.com"
register_data = {
    "email": customer_email,
    "password": "Password123!",
    "full_name": "Test Customer",
    "identity_card": f"0{int(time.time())}",
    "address": "123 Test St"
}

print(f"Registering customer {customer_email}...")
r = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print(r.status_code, r.text)

# 2. Login customer
print(f"Logging in customer...")
r = requests.post(f"{BASE_URL}/auth/login", json={"email": customer_email, "password": "Password123!"})
assert r.status_code == 200
token_cust = r.json()['token']
headers_cust = {"Authorization": f"Bearer {token_cust}"}

# 3. Check ME (verify welcome bonus 10M)
r = requests.get(f"{BASE_URL}/client/me", headers=headers_cust)
me_data = r.json()
print("Customer ME:", me_data)
assert me_data['user']['wallet_balance'] == 10000000.0

# 4. Make customer a STAFF manually via DB for testing purposes
print("Promoting customer to STAFF temporarily to get a staff account...")
import mysql.connector
import os
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "smart_savings"),
    "password": os.getenv("DB_PASSWORD", "SmartSavings@2026!"),
    "database": os.getenv("DB_NAME", "modern_savings_db")
}
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()
# Create another user for staff
staff_email = f"staff_{int(time.time())}@test.com"
r = requests.post(f"{BASE_URL}/auth/register", json={
    "email": staff_email,
    "password": "Password123!",
    "full_name": "Test Staff",
    "identity_card": f"1{int(time.time())}"
})
cursor.execute("UPDATE users SET role='STAFF' WHERE email=%s", (staff_email,))
conn.commit()

# 5. Login staff
print(f"Logging in staff {staff_email}...")
r = requests.post(f"{BASE_URL}/auth/login", json={"email": staff_email, "password": "Password123!"})
assert r.status_code == 200
token_staff = r.json()['token']
headers_staff = {"Authorization": f"Bearer {token_staff}"}

# 6. Get savings products
r = requests.get(f"{BASE_URL}/client/savings-products", headers=headers_cust)
products = r.json()['products']
# find a term product
term_product = next(p for p in products if p['term_months'] > 0)

# 7. Customer opens savings account
print(f"Opening savings account with product {term_product['name']} (ID: {term_product['product_id']})...")
open_data = {
    "product_id": term_product['product_id'],
    "amount": 2000000
}
r = requests.post(f"{BASE_URL}/client/open-savings", json=open_data, headers=headers_cust)
print(r.status_code, r.text)
assert r.status_code == 201
tx_id = r.json()['transaction_id']

# 8. Staff approves opening
print(f"Staff approving transaction {tx_id}...")
r = requests.patch(f"{BASE_URL}/transactions/{tx_id}", json={"status": "APPROVED"}, headers=headers_staff)
print(r.status_code, r.text)
assert r.status_code == 200

# 9. Verify Customer balance is now 8M
r = requests.get(f"{BASE_URL}/client/me", headers=headers_cust)
assert r.json()['user']['wallet_balance'] == 8000000.0
print("Balance successfully deducted.")

# 10. Check account demo times
r = requests.get(f"{BASE_URL}/client/savings-accounts", headers=headers_cust)
accs = r.json()['accounts']
print("Customer accounts:", json.dumps(accs, indent=2, ensure_ascii=False))
acc_id = accs[0]['account_id']

# 11. Estimate interest for early withdrawal
print(f"Estimating early withdrawal interest for account {acc_id}...")
r = requests.get(f"{BASE_URL}/client/savings-accounts/{acc_id}/estimate-interest", headers=headers_cust)
print("Estimate result:", r.json())
assert r.json()['is_early_withdrawal'] == True

# 12. Withdraw from account (close completely because it's a term account)
print(f"Closing account {acc_id}...")
r = requests.post(f"{BASE_URL}/client/close-savings/{acc_id}", headers=headers_cust)
print(r.status_code, r.text)
assert r.status_code == 201
tx_id2 = r.json()['transaction_id']

# 13. Staff approves withdrawal
print(f"Staff approving withdrawal transaction {tx_id2}...")
r = requests.patch(f"{BASE_URL}/transactions/{tx_id2}", json={"status": "APPROVED"}, headers=headers_staff)
print(r.status_code, r.text)
assert r.status_code == 200

# 14. Check customer balance
r = requests.get(f"{BASE_URL}/client/me", headers=headers_cust)
final_balance = r.json()['user']['wallet_balance']
print("Final Customer Balance:", final_balance)
# 8000000 + 2000000 + early interest (0.5% for 0 months is 0, so should be close to 10M)

print("All tests passed!")
