from flask import Blueprint, request, jsonify
import mysql.connector
from common.requireRole import require_role
from common.db import DB_CONFIG
from common.savings_rules import (
    MIN_OPEN_AMOUNT_KEY,
    MIN_SAVINGS_DEPOSIT_AMOUNT_KEY,
    NON_TERM_MIN_DAYS_KEY,
    calculate_interest,
    days_between,
    get_float_config,
    get_int_config,
    term_days,
)

client_bp = Blueprint("client", __name__)


def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    return conn, cursor


def _get_current_user_id():
    return request.user_data.get("user_id")


def _fetch_customer_basic(cursor, user_id):
    cursor.execute(
        """
        SELECT user_id, email, full_name, identity_card, account_number, wallet_balance, status, created_at
        FROM users
        WHERE user_id = %s AND role = 'CUSTOMER'
        """,
        (user_id,)
    )
    return cursor.fetchone()


def _parse_positive_amount(value, message="Số tiền không hợp lệ!"):
    try:
        amount = float(value)
        if amount <= 0:
            return None, jsonify({"message": message}), 400
        return amount, None, None
    except (TypeError, ValueError):
        return None, jsonify({"message": "Số tiền không hợp lệ!"}), 400


@client_bp.route("/api/client/me", methods=["GET"])
@require_role(["CUSTOMER"])
def get_my_profile():
    user_id = _get_current_user_id()
    conn, cursor = get_db()
    try:
        row = _fetch_customer_basic(cursor, user_id)
        if not row:
            return jsonify({"message": "Không tìm thấy khách hàng!"}), 404

        return jsonify({
            "message": "Thông tin cá nhân",
            "user": {
                "user_id": row[0],
                "email": row[1],
                "full_name": row[2],
                "identity_card": row[3],
                "account_number": row[4],
                "wallet_balance": float(row[5]),
                "status": row[6],
                "created_at": str(row[7])
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/dashboard", methods=["GET"])
@require_role(["CUSTOMER"])
def get_client_dashboard():
    user_id = _get_current_user_id()
    conn, cursor = get_db()
    try:
        user = _fetch_customer_basic(cursor, user_id)
        if not user:
            return jsonify({"message": "Không tìm thấy khách hàng!"}), 404

        cursor.execute(
            """
            SELECT COUNT(*), COALESCE(SUM(principal_balance), 0)
            FROM savings_accounts
            WHERE user_id = %s AND status = 'ACTIVE'
            """,
            (user_id,)
        )
        total_accounts, total_savings = cursor.fetchone()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM transactions
            WHERE user_id = %s AND status = 'PENDING'
            """,
            (user_id,)
        )
        pending_transactions = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT
                s.account_id,
                p.name AS product_name,
                p.interest_rate,
                p.term_months,
                s.principal_balance,
                s.opened_at,
                s.status
            FROM savings_accounts s
            JOIN savings_products p ON s.product_id = p.product_id
            WHERE s.user_id = %s AND s.status = 'ACTIVE'
            ORDER BY s.opened_at DESC
            LIMIT 5
            """,
            (user_id,)
        )
        rows = cursor.fetchall()

        recent_accounts = [
            {
                "account_id": row[0],
                "product_name": row[1],
                "interest_rate": float(row[2]),
                "term_months": row[3],
                "principal_balance": float(row[4]),
                "opened_at": str(row[5]),
                "status": row[6]
            }
            for row in rows
        ]

        return jsonify({
            "message": "Dashboard khách hàng",
            "data": {
                "user_id": user[0],
                "email": user[1],
                "full_name": user[2],
                "identity_card": user[3],
                "account_number": user[4],
                "wallet_balance": float(user[5]),
                "status": user[6],
                "created_at": str(user[7]),
                "active_savings_accounts": int(total_accounts or 0),
                "total_savings_principal": float(total_savings or 0),
                "pending_transactions": int(pending_transactions or 0),
                "recent_accounts": recent_accounts
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/savings-products", methods=["GET"])
@require_role(["CUSTOMER"])
def get_active_savings_products():
    conn, cursor = get_db()
    try:
        cursor.execute(
            """
            SELECT product_id, name, term_months, interest_rate, min_days_hold, description
            FROM savings_products
            WHERE is_active = TRUE
            ORDER BY term_months ASC, interest_rate ASC
            """
        )
        rows = cursor.fetchall()

        products = [
            {
                "product_id": row[0],
                "name": row[1],
                "term_months": row[2],
                "interest_rate": float(row[3]),
                "min_days_hold": row[4],
                "description": row[5]
            }
            for row in rows
        ]

        return jsonify({
            "message": "Danh sách gói tiết kiệm đang hoạt động",
            "total": len(products),
            "products": products
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/savings-accounts", methods=["GET"])
@require_role(["CUSTOMER"])
def get_my_savings_accounts():
    user_id = _get_current_user_id()
    status_filter = request.args.get("status")

    query = """
        SELECT
            s.account_id,
            p.name AS product_name,
            p.interest_rate,
            p.term_months,
            p.min_days_hold,
            s.principal_balance,
            s.opened_at,
            s.status
        FROM savings_accounts s
        JOIN savings_products p ON s.product_id = p.product_id
        WHERE s.user_id = %s
    """
    params = [user_id]

    if status_filter:
        query += " AND s.status = %s"
        params.append(status_filter)

    query += " ORDER BY s.opened_at DESC"

    conn, cursor = get_db()
    try:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        accounts = [
            {
                "account_id": row[0],
                "product_name": row[1],
                "interest_rate": float(row[2]),
                "term_months": row[3],
                "min_days_hold": row[4],
                "principal_balance": float(row[5]),
                "opened_at": str(row[6]),
                "status": row[7]
            }
            for row in rows
        ]

        return jsonify({
            "message": "Danh sách sổ tiết kiệm của tôi",
            "total": len(accounts),
            "accounts": accounts
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/savings-accounts/<int:account_id>", methods=["GET"])
@require_role(["CUSTOMER"])
def get_my_savings_account_detail(account_id):
    user_id = _get_current_user_id()
    conn, cursor = get_db()
    try:
        cursor.execute(
            """
            SELECT
                s.account_id,
                s.user_id,
                p.product_id,
                p.name,
                p.term_months,
                p.interest_rate,
                p.min_days_hold,
                s.principal_balance,
                s.opened_at,
                s.status,
                DATEDIFF(NOW(), s.opened_at) AS days_held
            FROM savings_accounts s
            JOIN savings_products p ON s.product_id = p.product_id
            WHERE s.account_id = %s AND s.user_id = %s
            """,
            (account_id, user_id)
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"message": "Không tìm thấy sổ tiết kiệm!"}), 404

        return jsonify({
            "message": "Chi tiết sổ tiết kiệm",
            "account": {
                "account_id": row[0],
                "user_id": row[1],
                "product_id": row[2],
                "product_name": row[3],
                "term_months": row[4],
                "interest_rate": float(row[5]),
                "min_days_hold": row[6],
                "principal_balance": float(row[7]),
                "opened_at": str(row[8]),
                "status": row[9],
                "days_held": int(row[10] or 0),
                "maturity_days": term_days(row[4])
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/deposit-requests", methods=["POST"])
@require_role(["CUSTOMER"])
def create_deposit_request():
    user_id = _get_current_user_id()
    data = request.get_json() or {}
    amount = data.get("amount")

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"message": "Số tiền nạp phải lớn hơn 0!"}), 400
    except (TypeError, ValueError):
        return jsonify({"message": "Số tiền không hợp lệ!"}), 400

    conn, cursor = get_db()
    try:
        cursor.execute(
            """
            INSERT INTO transactions (user_id, amount, transaction_type, status)
            VALUES (%s, %s, 'DEPOSIT_TO_WALLET', 'PENDING')
            """,
            (user_id, amount)
        )
        conn.commit()

        return jsonify({
            "message": "Đã tạo yêu cầu nạp tiền, vui lòng chờ duyệt!",
            "transaction_id": cursor.lastrowid,
            "amount": amount,
            "status": "PENDING"
        }), 201
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/withdraw-requests", methods=["POST"])
@require_role(["CUSTOMER"])
def create_withdraw_request():
    user_id = _get_current_user_id()
    data = request.get_json() or {}
    amount = data.get("amount")

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"message": "Số tiền rút phải lớn hơn 0!"}), 400
    except (TypeError, ValueError):
        return jsonify({"message": "Số tiền không hợp lệ!"}), 400

    conn, cursor = get_db()
    try:
        cursor.execute(
            "SELECT wallet_balance, account_number FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "Không tìm thấy khách hàng!"}), 404

        if float(user[0]) < amount:
            return jsonify({"message": "Số dư ví không đủ để tạo yêu cầu rút!"}), 400

        cursor.execute(
            """
            INSERT INTO transactions (user_id, amount, transaction_type, status)
            VALUES (%s, %s, 'WITHDRAW_FROM_WALLET', 'PENDING')
            """,
            (user_id, amount)
        )
        conn.commit()

        return jsonify({
            "message": "Đã tạo yêu cầu rút tiền, vui lòng chờ duyệt!",
            "transaction_id": cursor.lastrowid,
            "amount": amount,
            "status": "PENDING"
        }), 201
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/transfers", methods=["POST"])
@require_role(["CUSTOMER"])
def transfer_to_account_number():
    user_id = _get_current_user_id()
    data = request.get_json() or {}
    to_account_number = str(data.get("to_account_number", "")).strip()
    amount = data.get("amount")

    if not to_account_number:
        return jsonify({"message": "Vui lòng nhập số tài khoản nhận."}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"message": "Số tiền chuyển phải lớn hơn 0!"}), 400
    except (TypeError, ValueError):
        return jsonify({"message": "Số tiền không hợp lệ!"}), 400

    conn, cursor = get_db()
    try:
        cursor.execute(
            "SELECT user_id, wallet_balance, full_name, account_number FROM users WHERE user_id = %s AND role = 'CUSTOMER'",
            (user_id,)
        )
        sender = cursor.fetchone()
        if not sender:
            return jsonify({"message": "Không tìm thấy tài khoản nguồn!"}), 404

        sender_id, sender_wallet, sender_name, sender_account_number = sender
        if to_account_number == str(sender_account_number):
            return jsonify({"message": "Không thể tự chuyển khoản cho chính mình!"}), 400

        cursor.execute(
            "SELECT user_id, full_name, account_number FROM users WHERE account_number = %s AND role = 'CUSTOMER'",
            (to_account_number,)
        )
        receiver = cursor.fetchone()
        if not receiver:
            return jsonify({"message": "Không tìm thấy tài khoản nhận!"}), 404

        receiver_id, receiver_name, receiver_account_number = receiver

        if float(sender_wallet) < amount:
            return jsonify({"message": "Số dư ví không đủ để chuyển khoản!"}), 400

        cursor.execute("UPDATE users SET wallet_balance = wallet_balance - %s WHERE user_id = %s", (amount, sender_id))
        cursor.execute("UPDATE users SET wallet_balance = wallet_balance + %s WHERE user_id = %s", (amount, receiver_id))

        cursor.execute(
            """
            INSERT INTO transactions (user_id, amount, transaction_type, status)
            VALUES (%s, %s, 'WITHDRAW_FROM_WALLET', 'APPROVED')
            """,
            (sender_id, amount)
        )
        sender_txn_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO transactions (user_id, amount, transaction_type, status)
            VALUES (%s, %s, 'DEPOSIT_TO_WALLET', 'APPROVED')
            """,
            (receiver_id, amount)
        )
        receiver_txn_id = cursor.lastrowid

        conn.commit()
        return jsonify({
            "message": "Chuyển khoản thành công!",
            "from_account_number": str(sender_account_number),
            "to_account_number": str(receiver_account_number),
            "from_name": sender_name,
            "to_name": receiver_name,
            "amount": amount,
            "sender_transaction_id": sender_txn_id,
            "receiver_transaction_id": receiver_txn_id
        }), 201
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/open-savings", methods=["POST"])
@require_role(["CUSTOMER"])
def create_open_savings_request():
    user_id = _get_current_user_id()
    data = request.get_json() or {}

    product_id = data.get("product_id")
    amount = data.get("amount")

    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Dữ liệu đầu vào không hợp lệ!"}), 400
    amount, error_response, status_code = _parse_positive_amount(amount, "Số tiền gửi phải lớn hơn 0!")
    if error_response:
        return error_response, status_code

    conn, cursor = get_db()
    try:
        min_open_amount = get_float_config(cursor, MIN_OPEN_AMOUNT_KEY, 1000000)
        if amount < min_open_amount:
            return jsonify({
                "message": f"Số tiền mở sổ tối thiểu là {min_open_amount:,.0f} VND!"
            }), 400

        cursor.execute(
            """
            SELECT product_id, is_active, name
            FROM savings_products
            WHERE product_id = %s
            """,
            (product_id,)
        )
        product = cursor.fetchone()

        if not product:
            return jsonify({"message": "Gói tiết kiệm không tồn tại!"}), 404
        if not product[1]:
            return jsonify({"message": "Gói tiết kiệm hiện đang tạm khóa!"}), 400

        cursor.execute(
            "SELECT wallet_balance FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "Không tìm thấy khách hàng!"}), 404

        if float(user[0]) < amount:
            return jsonify({"message": "Số dư ví không đủ để mở sổ tiết kiệm!"}), 400

        cursor.execute(
            """
            INSERT INTO transactions (user_id, target_product_id, amount, transaction_type, status)
            VALUES (%s, %s, %s, 'OPEN_SAVINGS', 'PENDING')
            """,
            (user_id, product_id, amount)
        )
        new_transaction_id = cursor.lastrowid

        conn.commit()

        return jsonify({
            "message": "Đã tạo yêu cầu mở sổ tiết kiệm, vui lòng chờ nhân viên duyệt!",
            "transaction_id": new_transaction_id,
            "target_product_id": product_id,
            "amount": amount,
            "status": "PENDING"
        }), 201
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/close-savings/<int:account_id>", methods=["POST"])
@require_role(["CUSTOMER"])
def create_close_savings_request(account_id):
    user_id = _get_current_user_id()
    conn, cursor = get_db()
    try:
        cursor.execute(
            """
            SELECT
                s.account_id,
                s.user_id,
                s.principal_balance,
                s.opened_at,
                s.status,
                p.min_days_hold,
                p.term_months,
                p.interest_rate
            FROM savings_accounts s
            JOIN savings_products p ON s.product_id = p.product_id
            WHERE s.account_id = %s AND s.user_id = %s
            """,
            (account_id, user_id)
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"message": "Không tìm thấy sổ tiết kiệm!"}), 404

        account_id_db, _, principal_balance, opened_at, status, min_days_hold, term_months, interest_rate = row

        if status != "ACTIVE":
            return jsonify({"message": "Chỉ được tất toán sổ đang ở trạng thái ACTIVE!"}), 400

        cursor.execute(
            """
            SELECT transaction_id
            FROM transactions
            WHERE account_id = %s AND transaction_type = 'CLOSE_SAVINGS' AND status = 'PENDING'
            """,
            (account_id_db,)
        )
        existing_pending = cursor.fetchone()
        if existing_pending:
            return jsonify({"message": "Sổ này đã có yêu cầu tất toán đang chờ duyệt!"}), 400

        cursor.execute(
            """
            SELECT DATEDIFF(NOW(), %s)
            """,
            (opened_at,)
        )
        days_held = int(cursor.fetchone()[0] or 0)

        required_days = term_days(term_months) if int(term_months or 0) > 0 else int(min_days_hold or get_int_config(cursor, NON_TERM_MIN_DAYS_KEY, 15))
        if required_days and days_held < required_days:
            return jsonify({
                "message": f"Chưa đủ thời gian giữ tối thiểu {required_days} ngày để tất toán!",
                "days_held": days_held,
                "min_days_hold": int(required_days)
            }), 400

        interest_amount = calculate_interest(float(principal_balance), float(interest_rate), days_held)
        cursor.execute(
            """
            INSERT INTO transactions (user_id, account_id, amount, transaction_type, status, interest_amount)
            VALUES (%s, %s, %s, 'CLOSE_SAVINGS', 'PENDING', %s)
            """,
            (user_id, account_id_db, float(principal_balance), interest_amount)
        )
        conn.commit()

        return jsonify({
            "message": "Đã tạo yêu cầu tất toán sổ tiết kiệm, vui lòng chờ duyệt!",
            "transaction_id": cursor.lastrowid,
            "account_id": account_id_db,
            "amount": float(principal_balance),
            "interest_amount": interest_amount,
            "total_receive": float(principal_balance) + interest_amount,
            "status": "PENDING"
        }), 201
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/transactions", methods=["GET"])
@require_role(["CUSTOMER"])
def get_my_transactions():
    user_id = _get_current_user_id()
    status_filter = request.args.get("status")
    transaction_type = request.args.get("transaction_type")

    query = """
        SELECT
            t.transaction_id,
            t.account_id,
            t.amount,
            t.transaction_type,
            t.status,
            t.interest_amount,
            t.processed_by,
            t.created_at,
            p.name AS product_name
        FROM transactions t
        LEFT JOIN savings_accounts s ON t.account_id = s.account_id
        LEFT JOIN savings_products p ON s.product_id = p.product_id
        WHERE t.user_id = %s
    """
    params = [user_id]

    if status_filter:
        query += " AND t.status = %s"
        params.append(status_filter)

    if transaction_type:
        query += " AND t.transaction_type = %s"
        params.append(transaction_type)

    query += " ORDER BY t.created_at DESC"

    conn, cursor = get_db()
    try:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        transactions = [
            {
                "transaction_id": row[0],
                "account_id": row[1],
                "amount": float(row[2]),
                "transaction_type": row[3],
                "status": row[4],
                "interest_amount": float(row[5]),
                "processed_by": row[6],
                "created_at": str(row[7]),
                "product_name": row[8]
            }
            for row in rows
        ]

        return jsonify({
            "message": "Lịch sử giao dịch của tôi",
            "total": len(transactions),
            "transactions": transactions
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/savings-accounts/<int:account_id>/deposit-requests", methods=["POST"])
@require_role(["CUSTOMER"])
def create_savings_deposit_request(account_id):
    user_id = _get_current_user_id()
    data = request.get_json() or {}
    amount, error_response, status_code = _parse_positive_amount(data.get("amount"), "Số tiền gửi thêm phải lớn hơn 0!")
    if error_response:
        return error_response, status_code

    conn, cursor = get_db()
    try:
        min_deposit = get_float_config(cursor, MIN_SAVINGS_DEPOSIT_AMOUNT_KEY, 100000)
        if amount < min_deposit:
            return jsonify({"message": f"Số tiền gửi thêm tối thiểu là {min_deposit:,.0f} VND!"}), 400

        cursor.execute(
            """
            SELECT s.account_id, s.status, s.opened_at, p.term_months
            FROM savings_accounts s
            JOIN savings_products p ON s.product_id = p.product_id
            WHERE s.account_id = %s AND s.user_id = %s
            """,
            (account_id, user_id)
        )
        account = cursor.fetchone()
        if not account:
            return jsonify({"message": "Không tìm thấy sổ tiết kiệm!"}), 404
        if account[1] != "ACTIVE":
            return jsonify({"message": "Chỉ được gửi thêm vào sổ đang ACTIVE!"}), 400

        cursor.execute("SELECT wallet_balance FROM users WHERE user_id = %s", (user_id,))
        wallet = float(cursor.fetchone()[0])
        if wallet < amount:
            return jsonify({"message": "Số dư ví không đủ để gửi thêm vào sổ!"}), 400

        product_term_days = term_days(account[3])
        if product_term_days > 0 and days_between(account[2]) < product_term_days:
            return jsonify({
                "message": "Sổ có kỳ hạn chỉ được gửi thêm khi đã đến kỳ hạn tính lãi!",
                "days_held": days_between(account[2]),
                "required_days": product_term_days
            }), 400

        cursor.execute(
            """
            INSERT INTO transactions (user_id, account_id, amount, transaction_type, status)
            VALUES (%s, %s, %s, 'DEPOSIT_TO_SAVINGS', 'PENDING')
            """,
            (user_id, account_id, amount)
        )
        conn.commit()

        return jsonify({
            "message": "Đã tạo yêu cầu gửi thêm vào sổ, vui lòng chờ duyệt!",
            "transaction_id": cursor.lastrowid,
            "account_id": account_id,
            "amount": amount,
            "status": "PENDING"
        }), 201
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@client_bp.route("/api/client/savings-accounts/<int:account_id>/withdraw-requests", methods=["POST"])
@require_role(["CUSTOMER"])
def create_savings_withdraw_request(account_id):
    user_id = _get_current_user_id()
    data = request.get_json() or {}
    amount, error_response, status_code = _parse_positive_amount(data.get("amount"), "Số tiền rút phải lớn hơn 0!")
    if error_response:
        return error_response, status_code

    conn, cursor = get_db()
    try:
        cursor.execute(
            """
            SELECT s.account_id, s.principal_balance, s.opened_at, s.status,
                   p.term_months, p.interest_rate, p.min_days_hold
            FROM savings_accounts s
            JOIN savings_products p ON s.product_id = p.product_id
            WHERE s.account_id = %s AND s.user_id = %s
            """,
            (account_id, user_id)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({"message": "Không tìm thấy sổ tiết kiệm!"}), 404

        _, principal_balance, opened_at, status, term_months, interest_rate, min_days_hold = row
        principal_balance = float(principal_balance)
        if status != "ACTIVE":
            return jsonify({"message": "Chỉ được rút tiền từ sổ đang ACTIVE!"}), 400
        if amount > principal_balance:
            return jsonify({"message": "Số tiền rút không được vượt quá số dư sổ!"}), 400

        held_days = days_between(opened_at)
        if int(term_months or 0) > 0:
            return jsonify({"message": "Sổ có kỳ hạn phải tất toán toàn bộ, không được rút một phần!"}), 400

        required_days = int(min_days_hold or get_int_config(cursor, NON_TERM_MIN_DAYS_KEY, 15))
        if held_days < required_days:
            return jsonify({
                "message": f"Sổ không kỳ hạn phải gửi trên {required_days} ngày mới được rút!",
                "days_held": held_days,
                "min_days_hold": required_days
            }), 400

        interest_amount = calculate_interest(amount, float(interest_rate), held_days)
        cursor.execute(
            """
            INSERT INTO transactions (user_id, account_id, amount, transaction_type, status, interest_amount)
            VALUES (%s, %s, %s, 'WITHDRAW_FROM_SAVINGS', 'PENDING', %s)
            """,
            (user_id, account_id, amount, interest_amount)
        )
        conn.commit()

        return jsonify({
            "message": "Đã tạo yêu cầu rút tiền từ sổ, vui lòng chờ duyệt!",
            "transaction_id": cursor.lastrowid,
            "account_id": account_id,
            "amount": amount,
            "interest_amount": interest_amount,
            "total_receive": amount + interest_amount,
            "status": "PENDING"
        }), 201
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Lỗi server!", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
