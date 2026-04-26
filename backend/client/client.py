from flask import Blueprint, request, jsonify
import mysql.connector
from common.requireRole import require_role
from common.db import DB_CONFIG

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
                s.status
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
                "status": row[9]
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
        amount = float(amount)
        if amount <= 0:
            return jsonify({"message": "Số tiền gửi phải lớn hơn 0!"}), 400
    except (TypeError, ValueError):
        return jsonify({"message": "Dữ liệu đầu vào không hợp lệ!"}), 400

    conn, cursor = get_db()
    try:
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

        # Mở sổ tức thì: trừ tiền ví + tạo sổ + ghi nhận giao dịch đã duyệt.
        cursor.execute(
            "UPDATE users SET wallet_balance = wallet_balance - %s WHERE user_id = %s",
            (amount, user_id)
        )

        cursor.execute(
            """
            INSERT INTO savings_accounts (user_id, product_id, principal_balance, status)
            VALUES (%s, %s, %s, 'ACTIVE')
            """,
            (user_id, product_id, amount)
        )
        new_account_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO transactions (user_id, account_id, amount, transaction_type, status)
            VALUES (%s, %s, %s, 'OPEN_SAVINGS', 'APPROVED')
            """,
            (user_id, new_account_id, amount)
        )
        new_transaction_id = cursor.lastrowid

        conn.commit()

        return jsonify({
            "message": "Mở sổ tiết kiệm thành công!",
            "transaction_id": new_transaction_id,
            "account_id": new_account_id,
            "status": "APPROVED"
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
                p.min_days_hold
            FROM savings_accounts s
            JOIN savings_products p ON s.product_id = p.product_id
            WHERE s.account_id = %s AND s.user_id = %s
            """,
            (account_id, user_id)
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"message": "Không tìm thấy sổ tiết kiệm!"}), 404

        account_id_db, _, principal_balance, opened_at, status, min_days_hold = row

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

        if min_days_hold and days_held < int(min_days_hold):
            return jsonify({
                "message": f"Chưa đủ thời gian giữ tối thiểu {min_days_hold} ngày để tất toán!",
                "days_held": days_held,
                "min_days_hold": int(min_days_hold)
            }), 400

        cursor.execute(
            """
            INSERT INTO transactions (user_id, account_id, amount, transaction_type, status)
            VALUES (%s, %s, %s, 'CLOSE_SAVINGS', 'PENDING')
            """,
            (user_id, account_id_db, float(principal_balance))
        )
        conn.commit()

        return jsonify({
            "message": "Đã tạo yêu cầu tất toán sổ tiết kiệm, vui lòng chờ duyệt!",
            "transaction_id": cursor.lastrowid,
            "account_id": account_id_db,
            "amount": float(principal_balance),
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
                "processed_by": row[5],
                "created_at": str(row[6]),
                "product_name": row[7]
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