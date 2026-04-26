from flask import Flask, jsonify
from flask_cors import CORS
from common.auth import auth_bp
from staff.staff import transactions_bp
from admin.admin import admin_bp
from client.client import client_bp
from common.db import db_cursor, db_conn
from werkzeug.security import generate_password_hash
import random

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'mot_chuoi_bi_mat_rat_dai_va_kho_doan'


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


def ensure_default_admin_account():
    default_admin_email = "admin@gmail.com"
    default_admin_password = "admin123"
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


def ensure_default_savings_products():
    db_cursor.execute("SELECT COUNT(*) FROM savings_products")
    total_products = int(db_cursor.fetchone()[0] or 0)
    if total_products > 0:
        return

    default_products = [
        ("Không kỳ hạn", 0, 0.20, 0, "Rút linh hoạt, lãi suất thấp."),
        ("Tiết kiệm 3 tháng", 3, 4.80, 30, "Phù hợp mục tiêu ngắn hạn."),
        ("Tiết kiệm 6 tháng", 6, 5.60, 60, "Lãi suất tốt cho mục tiêu trung hạn."),
        ("Tiết kiệm 12 tháng", 12, 6.40, 90, "Lãi suất cao cho mục tiêu dài hạn."),
    ]

    db_cursor.executemany(
        """
        INSERT INTO savings_products (name, term_months, interest_rate, min_days_hold, is_active, description)
        VALUES (%s, %s, %s, %s, TRUE, %s)
        """,
        default_products
    )
    db_conn.commit()

# Đăng ký các Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(client_bp)

ensure_account_number_schema()
ensure_default_admin_account()
ensure_default_savings_products()


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong 🏓 – Server đang chạy!'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
