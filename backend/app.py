from flask import Flask, jsonify
from flask_cors import CORS
from common.auth import auth_bp
from staff.staff import transactions_bp
from admin.admin import admin_bp
from client.client import client_bp
from common.db import db_cursor, db_conn
from common.savings_rules import ensure_default_configs
from werkzeug.security import generate_password_hash
import random
import os

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mot_chuoi_bi_mat_rat_dai_va_kho_doan')


def _generate_unique_account_number():
    while True:
        account_number = ''.join(random.choices('0123456789', k=10))
        db_cursor.execute("SELECT user_id FROM users WHERE account_number = %s", (account_number,))
        if not db_cursor.fetchone():
            return account_number


def ensure_account_number_schema():
    db_cursor.execute("SHOW COLUMNS FROM users LIKE 'account_number'")
    has_column = db_cursor.fetchone()
    if not has_column:
        db_cursor.execute(
            "ALTER TABLE users ADD COLUMN account_number VARCHAR(20) UNIQUE NULL AFTER identity_card"
        )

    db_cursor.execute("SELECT user_id FROM users WHERE account_number IS NULL OR account_number = ''")
    users_missing = db_cursor.fetchall()
    for (user_id,) in users_missing:
        new_account_number = _generate_unique_account_number()
        db_cursor.execute(
            "UPDATE users SET account_number = %s WHERE user_id = %s",
            (new_account_number, user_id)
        )

    db_conn.commit()


def ensure_transaction_schema():
    db_cursor.execute("SHOW COLUMNS FROM transactions LIKE 'transaction_type'")
    transaction_type_column = db_cursor.fetchone()
    if transaction_type_column:
        db_cursor.execute(
            """
            ALTER TABLE transactions MODIFY transaction_type
            ENUM('DEPOSIT_TO_WALLET', 'WITHDRAW_FROM_WALLET', 'OPEN_SAVINGS',
                 'DEPOSIT_TO_SAVINGS', 'WITHDRAW_FROM_SAVINGS', 'CLOSE_SAVINGS',
                 'TRANSFER_OUT', 'TRANSFER_IN') NOT NULL
            """
        )

    db_cursor.execute("SHOW COLUMNS FROM transactions LIKE 'interest_amount'")
    has_interest = db_cursor.fetchone()
    if not has_interest:
        db_cursor.execute(
            "ALTER TABLE transactions ADD COLUMN interest_amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00 AFTER status"
        )

    db_conn.commit()


def ensure_default_admin_account():
    default_admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@gmail.com")
    default_admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
    default_admin_name = "System Admin"
    default_admin_identity_card = "ADMIN000001"

    db_cursor.execute(
        "SELECT user_id FROM users WHERE email = %s",
        (default_admin_email,)
    )
    admin = db_cursor.fetchone()
    password_hash = generate_password_hash(default_admin_password, method='pbkdf2:sha256')

    if admin:
        db_cursor.execute(
            """
            UPDATE users
            SET password_hash = %s, role = 'ADMIN', status = 'ACTIVE'
            WHERE user_id = %s
            """,
            (password_hash, admin[0])
        )
    else:
        # Nếu đã có admin cũ (hoặc bản ghi giữ identity_card mặc định), tái sử dụng để tránh trùng UNIQUE.
        db_cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE identity_card = %s OR role = 'ADMIN'
            ORDER BY user_id ASC
            LIMIT 1
            """,
            (default_admin_identity_card,)
        )
        existing_admin = db_cursor.fetchone()

        if existing_admin:
            db_cursor.execute(
                """
                UPDATE users
                SET email = %s,
                    password_hash = %s,
                    full_name = %s,
                    identity_card = %s,
                    role = 'ADMIN',
                    status = 'ACTIVE'
                WHERE user_id = %s
                """,
                (
                    default_admin_email,
                    password_hash,
                    default_admin_name,
                    default_admin_identity_card,
                    existing_admin[0]
                )
            )
        else:
            account_number = _generate_unique_account_number()
            db_cursor.execute(
                """
                INSERT INTO users (email, password_hash, full_name, identity_card, role, status, account_number)
                VALUES (%s, %s, %s, %s, 'ADMIN', 'ACTIVE', %s)
                """,
                (default_admin_email, password_hash, default_admin_name, default_admin_identity_card, account_number)
            )

    db_conn.commit()


def ensure_default_staff_account():
    default_staff_email = os.getenv("DEFAULT_STAFF_EMAIL", "staff@gmail.com")
    default_staff_password = os.getenv("DEFAULT_STAFF_PASSWORD", "staff123")
    default_staff_name = "Default Staff"
    default_staff_identity_card = "STAFF000001"

    db_cursor.execute(
        "SELECT user_id FROM users WHERE email = %s",
        (default_staff_email,)
    )
    staff = db_cursor.fetchone()
    password_hash = generate_password_hash(default_staff_password, method='pbkdf2:sha256')

    if staff:
        db_cursor.execute(
            """
            UPDATE users
            SET password_hash = %s, role = 'STAFF', status = 'ACTIVE'
            WHERE user_id = %s
            """,
            (password_hash, staff[0])
        )
    else:
        db_cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE identity_card = %s
            LIMIT 1
            """,
            (default_staff_identity_card,)
        )
        existing_staff = db_cursor.fetchone()
        if existing_staff:
            db_cursor.execute(
                """
                UPDATE users
                SET email = %s,
                    password_hash = %s,
                    full_name = %s,
                    identity_card = %s,
                    role = 'STAFF',
                    status = 'ACTIVE'
                WHERE user_id = %s
                """,
                (
                    default_staff_email,
                    password_hash,
                    default_staff_name,
                    default_staff_identity_card,
                    existing_staff[0]
                )
            )
        else:
            account_number = _generate_unique_account_number()
            db_cursor.execute(
                """
                INSERT INTO users (email, password_hash, full_name, identity_card, role, status, account_number)
                VALUES (%s, %s, %s, %s, 'STAFF', 'ACTIVE', %s)
                """,
                (default_staff_email, password_hash, default_staff_name, default_staff_identity_card, account_number)
            )

    db_conn.commit()


def ensure_default_savings_products():
    db_cursor.execute("SELECT COUNT(*) FROM savings_products")
    total_products = int(db_cursor.fetchone()[0] or 0)
    if total_products > 0:
        return

    default_products = [
        ("Không kỳ hạn", 0, 0.50, 15, "Rút linh hoạt sau thời gian giữ tối thiểu."),
        ("Tiết kiệm 3 phút", 3, 5.00, 0, "Kỳ hạn demo 3 phút để kiểm thử quy trình tất toán."),
        ("Tiết kiệm 6 phút", 6, 5.50, 0, "Kỳ hạn demo 6 phút để kiểm thử quy trình tất toán."),
    ]

    db_cursor.executemany(
        """
        INSERT INTO savings_products (name, term_months, interest_rate, min_days_hold, is_active, description)
        VALUES (%s, %s, %s, %s, TRUE, %s)
        """,
        default_products
    )
    db_conn.commit()


def ensure_system_configs():
    ensure_default_configs(db_cursor)
    db_conn.commit()

# Đăng ký các Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(client_bp)

ensure_account_number_schema()
ensure_transaction_schema()
ensure_default_admin_account()
ensure_default_staff_account()
ensure_default_savings_products()
ensure_system_configs()


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong 🏓 – Server đang chạy!'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
