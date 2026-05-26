from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from common.db import db_cursor, db_conn
import jwt
import datetime
import random

auth_bp = Blueprint('auth', __name__)

def _generate_unique_account_number(cursor):
    while True:
        account_number = ''.join(random.choices('0123456789', k=10))
        cursor.execute("SELECT user_id FROM users WHERE account_number = %s", (account_number,))
        if not cursor.fetchone():
            return account_number


@auth_bp.route('/api/auth/register', methods=['POST'])
@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    email         = data.get('email')
    password      = data.get('password')
    full_name     = data.get('full_name')
    identity_card = data.get('identity_card')
    address       = data.get('address', '')

    if not email or not password or not full_name:
        return jsonify({'message': 'Vui lòng điền đủ thông tin!'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    account_number = _generate_unique_account_number(db_cursor)
    welcome_bonus = 10000000

    try:
        sql = """INSERT INTO users (email, password_hash, full_name, identity_card, account_number, address, wallet_balance)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        db_cursor.execute(sql, (email, hashed_password, full_name, identity_card, account_number, address, welcome_bonus))
        db_conn.commit()
        return jsonify({
            'message': 'Đăng ký thành công! Tài khoản được tặng 10.000.000 VND.',
            'account_number': account_number,
            'welcome_bonus': welcome_bonus
        }), 201
    except Exception as e:
        return jsonify({'message': 'Email hoặc CMND/CCCD đã tồn tại!', 'error': str(e)}), 400


@auth_bp.route('/api/auth/login', methods=['POST'])
@auth_bp.route('/api/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = data.get('email')
    password = data.get('password')

    db_cursor.execute(
        "SELECT user_id, password_hash, role, status FROM users WHERE email = %s",
        (email,)
    )
    user = db_cursor.fetchone()

    if not user:
        return jsonify({'message': 'Tài khoản không tồn tại!'}), 404

    user_id, password_hash, role, status = user

    if status == 'LOCKED':
        return jsonify({'message': 'Tài khoản đã bị khóa!'}), 403

    if check_password_hash(password_hash, password):
        payload = {
            'user_id': user_id,
            'role':    role,
            'exp':     datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            'message': 'Đăng nhập thành công!',
            'token':   token,
            'role':    role
        }), 200

    return jsonify({'message': 'Sai mật khẩu!'}), 401


@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
@auth_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    identity_card = (data.get('identity_card') or '').strip()
    new_password = data.get('new_password') or ''

    if not email or not identity_card or not new_password:
        return jsonify({'message': 'Vui lòng nhập đủ email, CMND/CCCD và mật khẩu mới!'}), 400

    if len(new_password) < 6:
        return jsonify({'message': 'Mật khẩu mới phải có ít nhất 6 ký tự!'}), 400

    try:
        db_cursor.execute(
            "SELECT user_id FROM users WHERE email = %s AND identity_card = %s",
            (email, identity_card)
        )
        user = db_cursor.fetchone()
        if not user:
            return jsonify({'message': 'Thông tin xác thực không đúng!'}), 404

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db_cursor.execute(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (hashed_password, user[0])
        )
        db_conn.commit()
        return jsonify({'message': 'Đổi mật khẩu thành công. Bạn có thể đăng nhập lại.'}), 200
    except Exception as e:
        db_conn.rollback()
        return jsonify({'message': 'Không thể đặt lại mật khẩu.', 'error': str(e)}), 500
