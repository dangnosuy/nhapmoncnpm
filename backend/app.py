from flask import Flask, jsonify
from flask_cors import CORS
from common.auth import auth_bp
from staff.staff import transactions_bp
from admin.admin import admin_bp
from client.client import client_bp
from common.db import db_cursor, db_conn
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

# Đăng ký các Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(client_bp)

ensure_account_number_schema()


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong 🏓 – Server đang chạy!'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
