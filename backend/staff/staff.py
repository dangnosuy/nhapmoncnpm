from flask import Blueprint, request, jsonify
from common.db import db_cursor, db_conn
from common.requireRole import require_role
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

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/api/transactions', methods=['GET'])
@require_role(['STAFF', 'ADMIN'])
def get_all_transactions():
    """Chỉ STAFF và ADMIN mới được xem danh sách giao dịch."""
    status_filter = request.args.get('status')
    type_filter = request.args.get('transaction_type')
    
    query = """
        SELECT
            t.transaction_id,
            u.full_name AS customer_name,
            t.account_id,
            t.target_product_id,
            p.name AS target_product_name,
            t.amount,
            t.transaction_type,
            t.status,
            t.interest_amount,
            t.created_at
        FROM transactions t
        JOIN users u ON t.user_id = u.user_id
        LEFT JOIN savings_products p ON t.target_product_id = p.product_id
        WHERE 1=1
    """
    params = []
    
    if status_filter:
        query += " AND t.status = %s"
        params.append(status_filter)

    if type_filter:
        query += " AND t.transaction_type = %s"
        params.append(type_filter)
        
    query += " ORDER BY t.created_at DESC"
    
    try:
        db_cursor.execute(query, tuple(params))
        rows = db_cursor.fetchall()

        transactions = [
            {
                'transaction_id': row[0],
                'customer_name': row[1],
                'account_id': row[2],
                'target_product_id': row[3],
                'target_product_name': row[4],
                'amount': float(row[5]),
                'transaction_type': row[6],
                'status': row[7],
                'interest_amount': float(row[8] or 0),
                'created_at': str(row[9]),
            }
            for row in rows
        ]
        return jsonify({
            'message':      'Danh sách lịch sử giao dịch',
            'total':        len(transactions),
            'transactions': transactions
        }), 200
    except Exception as e:
        return jsonify({'message': 'Lỗi server!', 'error': str(e)}), 500


@transactions_bp.route('/api/transactions/<int:transaction_id>/approve', methods=['PUT'])
@require_role(['STAFF', 'ADMIN'])
def approve_transaction(transaction_id):
    """Duyệt phiếu yêu cầu và thực thi thay đổi vào Database."""
    staff_id = request.user_data.get('user_id')
    try:
        db_cursor.execute(
            """
            SELECT user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount
            FROM transactions
            WHERE transaction_id = %s
            """,
            (transaction_id,)
        )
        txn = db_cursor.fetchone()
        
        if not txn:
            return jsonify({'message': 'Không tìm thấy giao dịch!'}), 404
            
        user_id, account_id, target_product_id, amount, transaction_type, status, interest_amount = txn
        amount = float(amount)
        interest_amount = float(interest_amount or 0)
        
        if status != 'PENDING':
            return jsonify({'message': f'Giao dịch không ở trạng thái PENDING (Hiện tại: {status})'}), 400
            
        if transaction_type == 'DEPOSIT_TO_WALLET':
            db_cursor.execute("UPDATE users SET wallet_balance = wallet_balance + %s WHERE user_id = %s", (amount, user_id))
            
        elif transaction_type == 'WITHDRAW_FROM_WALLET':
            db_cursor.execute("SELECT wallet_balance FROM users WHERE user_id = %s", (user_id,))
            wallet = float(db_cursor.fetchone()[0])
            if wallet < amount:
                return jsonify({'message': 'Số dư ví không đủ để rút!'}), 400
            db_cursor.execute("UPDATE users SET wallet_balance = wallet_balance - %s WHERE user_id = %s", (amount, user_id))
            
        elif transaction_type == 'OPEN_SAVINGS':
            min_open_amount = get_float_config(db_cursor, MIN_OPEN_AMOUNT_KEY, 1000000)
            if amount < min_open_amount:
                return jsonify({'message': f'Số tiền mở sổ tối thiểu là {min_open_amount:,.0f} VND!'}), 400
            if not target_product_id:
                return jsonify({'message': 'Thiếu loại tiết kiệm cần mở!'}), 400
            db_cursor.execute("SELECT is_active FROM savings_products WHERE product_id = %s", (target_product_id,))
            product = db_cursor.fetchone()
            if not product:
                return jsonify({'message': 'Gói tiết kiệm không tồn tại!'}), 404
            if not product[0]:
                return jsonify({'message': 'Gói tiết kiệm hiện đang tạm khóa!'}), 400
            db_cursor.execute("SELECT wallet_balance FROM users WHERE user_id = %s", (user_id,))
            wallet = float(db_cursor.fetchone()[0])
            if wallet < amount:
                return jsonify({'message': 'Số dư trong ví không đủ để mở sổ tiết kiệm!'}), 400
            db_cursor.execute("UPDATE users SET wallet_balance = wallet_balance - %s WHERE user_id = %s", (amount, user_id))
            db_cursor.execute(
                """
                INSERT INTO savings_accounts (user_id, product_id, principal_balance, status)
                VALUES (%s, %s, %s, 'ACTIVE')
                """,
                (user_id, target_product_id, amount)
            )
            account_id = db_cursor.lastrowid
            db_cursor.execute(
                "UPDATE transactions SET account_id = %s WHERE transaction_id = %s",
                (account_id, transaction_id)
            )

        elif transaction_type == 'DEPOSIT_TO_SAVINGS':
            min_deposit = get_float_config(db_cursor, MIN_SAVINGS_DEPOSIT_AMOUNT_KEY, 100000)
            if amount < min_deposit:
                return jsonify({'message': f'Số tiền gửi thêm tối thiểu là {min_deposit:,.0f} VND!'}), 400
            db_cursor.execute(
                """
                SELECT s.user_id, s.status, s.opened_at, p.term_months
                FROM savings_accounts s
                JOIN savings_products p ON s.product_id = p.product_id
                WHERE s.account_id = %s
                """,
                (account_id,)
            )
            account = db_cursor.fetchone()
            if not account or account[0] != user_id:
                return jsonify({'message': 'Không tìm thấy sổ tiết kiệm của khách hàng!'}), 404
            if account[1] != 'ACTIVE':
                return jsonify({'message': 'Chỉ được gửi thêm vào sổ ACTIVE!'}), 400
            required_days = term_days(account[3])
            if required_days > 0 and days_between(account[2]) < required_days:
                return jsonify({'message': 'Sổ có kỳ hạn chỉ được gửi thêm khi đã đến kỳ hạn tính lãi!'}), 400
            db_cursor.execute("SELECT wallet_balance FROM users WHERE user_id = %s", (user_id,))
            wallet = float(db_cursor.fetchone()[0])
            if wallet < amount:
                return jsonify({'message': 'Số dư ví không đủ để gửi thêm vào sổ!'}), 400
            db_cursor.execute("UPDATE users SET wallet_balance = wallet_balance - %s WHERE user_id = %s", (amount, user_id))
            db_cursor.execute("UPDATE savings_accounts SET principal_balance = principal_balance + %s WHERE account_id = %s", (amount, account_id))

        elif transaction_type == 'WITHDRAW_FROM_SAVINGS':
            db_cursor.execute(
                """
                SELECT s.principal_balance, s.opened_at, s.status, p.term_months, p.interest_rate, p.min_days_hold
                FROM savings_accounts s
                JOIN savings_products p ON s.product_id = p.product_id
                WHERE s.account_id = %s AND s.user_id = %s
                """,
                (account_id, user_id)
            )
            account = db_cursor.fetchone()
            if not account:
                return jsonify({'message': 'Không tìm thấy sổ tiết kiệm!'}), 404
            principal_balance, opened_at, account_status, term_months, interest_rate, min_days_hold = account
            principal_balance = float(principal_balance)
            if account_status != 'ACTIVE':
                return jsonify({'message': 'Chỉ được rút tiền từ sổ ACTIVE!'}), 400
            if int(term_months or 0) > 0:
                return jsonify({'message': 'Sổ có kỳ hạn phải tất toán toàn bộ, không được rút một phần!'}), 400
            if amount > principal_balance:
                return jsonify({'message': 'Số tiền rút vượt quá số dư sổ!'}), 400
            held_days = days_between(opened_at)
            required_days = int(min_days_hold or get_int_config(db_cursor, NON_TERM_MIN_DAYS_KEY, 15))
            if held_days < required_days:
                return jsonify({'message': f'Sổ không kỳ hạn phải gửi trên {required_days} ngày mới được rút!'}), 400
            interest_amount = calculate_interest(amount, float(interest_rate), held_days)
            db_cursor.execute(
                "UPDATE users SET wallet_balance = wallet_balance + %s WHERE user_id = %s",
                (amount + interest_amount, user_id)
            )
            db_cursor.execute(
                """
                UPDATE savings_accounts
                SET principal_balance = principal_balance - %s,
                    status = CASE WHEN principal_balance - %s <= 0 THEN 'CLOSED' ELSE status END
                WHERE account_id = %s
                """,
                (amount, amount, account_id)
            )
            db_cursor.execute(
                "UPDATE transactions SET interest_amount = %s WHERE transaction_id = %s",
                (interest_amount, transaction_id)
            )
            
        elif transaction_type == 'CLOSE_SAVINGS':
            db_cursor.execute(
                """
                SELECT s.principal_balance, s.opened_at, s.status, p.term_months, p.interest_rate, p.min_days_hold
                FROM savings_accounts s
                JOIN savings_products p ON s.product_id = p.product_id
                WHERE s.account_id = %s AND s.user_id = %s
                """,
                (account_id, user_id)
            )
            account = db_cursor.fetchone()
            if not account:
                return jsonify({'message': 'Không tìm thấy sổ tiết kiệm!'}), 404
            principal_balance, opened_at, account_status, term_months, interest_rate, min_days_hold = account
            principal_balance = float(principal_balance)
            if account_status != 'ACTIVE':
                return jsonify({'message': 'Chỉ được tất toán sổ ACTIVE!'}), 400
            held_days = days_between(opened_at)
            required_days = term_days(term_months) if int(term_months or 0) > 0 else int(min_days_hold or get_int_config(db_cursor, NON_TERM_MIN_DAYS_KEY, 15))
            if required_days and held_days < required_days:
                return jsonify({'message': f'Chưa đủ thời gian giữ tối thiểu {required_days} ngày để tất toán!'}), 400
            interest_amount = calculate_interest(principal_balance, float(interest_rate), held_days)
            db_cursor.execute("UPDATE users SET wallet_balance = wallet_balance + %s WHERE user_id = %s", (principal_balance + interest_amount, user_id))
            db_cursor.execute("UPDATE savings_accounts SET status = 'CLOSED', principal_balance = 0 WHERE account_id = %s", (account_id,))
            db_cursor.execute(
                "UPDATE transactions SET amount = %s, interest_amount = %s WHERE transaction_id = %s",
                (principal_balance, interest_amount, transaction_id)
            )

        else:
            return jsonify({'message': f'Loại giao dịch không hỗ trợ: {transaction_type}'}), 400

        db_cursor.execute("UPDATE transactions SET status = 'APPROVED', processed_by = %s WHERE transaction_id = %s", (staff_id, transaction_id))
        db_conn.commit()
        return jsonify({'message': 'Duyệt giao dịch thành công!'}), 200
        
    except Exception as e:
        db_conn.rollback()
        return jsonify({'message': 'Lỗi server!', 'error': str(e)}), 500


@transactions_bp.route('/api/transactions/<int:transaction_id>/reject', methods=['PUT'])
@require_role(['STAFF', 'ADMIN'])
def reject_transaction(transaction_id):
    """Từ chối phiếu yêu cầu."""
    staff_id = request.user_data.get('user_id')
    try:
        db_cursor.execute("SELECT status, transaction_type, account_id FROM transactions WHERE transaction_id = %s", (transaction_id,))
        txn = db_cursor.fetchone()
        
        if not txn:
            return jsonify({'message': 'Không tìm thấy giao dịch!'}), 404
            
        status, transaction_type, account_id = txn
        if status != 'PENDING':
            return jsonify({'message': f'Giao dịch không ở trạng thái PENDING (Hiện tại: {status})'}), 400
            
        db_cursor.execute("UPDATE transactions SET status = 'REJECTED', processed_by = %s WHERE transaction_id = %s", (staff_id, transaction_id))
        
        db_conn.commit()
        return jsonify({'message': 'Đã từ chối giao dịch!'}), 200
        
    except Exception as e:
        db_conn.rollback()
        return jsonify({'message': 'Lỗi server!', 'error': str(e)}), 500


@transactions_bp.route('/api/transactions/<int:transaction_id>', methods=['PATCH'])
@require_role(['STAFF', 'ADMIN'])
def update_transaction_status(transaction_id):
    """RESTful endpoint cập nhật trạng thái duyệt giao dịch."""
    data = request.get_json() or {}
    status = (data.get('status') or '').upper()

    if status == 'APPROVED':
        return approve_transaction(transaction_id)
    if status == 'REJECTED':
        return reject_transaction(transaction_id)

    return jsonify({'message': 'Trạng thái không hợp lệ! Chỉ chấp nhận APPROVED hoặc REJECTED.'}), 400


@transactions_bp.route('/api/balance-system', methods=['GET'])
@require_role(['STAFF', 'ADMIN'])
def get_system_balance():
    """Xem tổng số dư ví và tổng tiền gốc tiết kiệm của toàn hệ thống."""
    try:
        db_cursor.execute("SELECT SUM(wallet_balance) FROM users WHERE role = 'CUSTOMER'")
        total_wallet = db_cursor.fetchone()[0] or 0.0
        
        db_cursor.execute("SELECT SUM(principal_balance) FROM savings_accounts WHERE status = 'ACTIVE'")
        total_savings = db_cursor.fetchone()[0] or 0.0
        
        return jsonify({
            'message': 'Cân đối hệ thống',
            'total_wallet_balance': float(total_wallet),
            'total_savings_principal': float(total_savings)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Lỗi server!', 'error': str(e)}), 500


@transactions_bp.route('/api/users', methods=['GET'])
@require_role(['STAFF', 'ADMIN'])
def get_customers():
    """Lấy danh sách thông tin khách hàng (role CUSTOMER)."""
    try:
        db_cursor.execute("""
            SELECT user_id, full_name, email, identity_card, wallet_balance, status, created_at 
            FROM users 
            WHERE role = 'CUSTOMER'
            ORDER BY created_at DESC
        """)
        rows = db_cursor.fetchall()
        users = [
            {
                'user_id': row[0],
                'full_name': row[1],
                'email': row[2],
                'identity_card': row[3],
                'wallet_balance': float(row[4]),
                'status': row[5],
                'created_at': str(row[6])
            }
            for row in rows
        ]
        return jsonify({
            'message': 'Danh sách khách hàng',
            'total': len(users),
            'users': users
        })
    except Exception as e:
        return jsonify({'message': 'Lỗi server!', 'error': str(e)}), 500


@transactions_bp.route('/api/savings-accounts', methods=['GET'])
@require_role(['STAFF', 'ADMIN'])
def get_all_savings_accounts():
    """Lấy danh sách toàn bộ sổ tiết kiệm."""
    try:
        db_cursor.execute("""
            SELECT 
                s.account_id, u.full_name AS customer_name, p.name AS product_name,
                s.principal_balance, s.opened_at, s.status, p.interest_rate, p.term_months
            FROM savings_accounts s
            JOIN users u ON s.user_id = u.user_id
            JOIN savings_products p ON s.product_id = p.product_id
            ORDER BY s.opened_at DESC
        """)
        rows = db_cursor.fetchall()
        accounts = [
            {
                'account_id': row[0],
                'customer_name': row[1],
                'product_name': row[2],
                'principal_balance': float(row[3]),
                'opened_at': str(row[4]),
                'status': row[5],
                'interest_rate': float(row[6]),
                'term_months': row[7]
            }
            for row in rows
        ]
        return jsonify({
            'message': 'Danh sách sổ tiết kiệm',
            'total': len(accounts),
            'accounts': accounts
        }), 200
    except Exception as e:
        return jsonify({'message': 'Lỗi server!', 'error': str(e)}), 500


@transactions_bp.route('/api/savings-accounts/<int:account_id>', methods=['GET'])
@require_role(['STAFF', 'ADMIN'])
def get_savings_account_detail(account_id):
    """Xem chi tiết một sổ tiết kiệm cụ thể."""
    try:
        db_cursor.execute("""
            SELECT 
                s.account_id, u.full_name, u.identity_card, p.name,
                s.principal_balance, s.opened_at, s.status, p.interest_rate, p.term_months, p.min_days_hold
            FROM savings_accounts s
            JOIN users u ON s.user_id = u.user_id
            JOIN savings_products p ON s.product_id = p.product_id
            WHERE s.account_id = %s
        """, (account_id,))
        row = db_cursor.fetchone()
        
        if not row:
            return jsonify({'message': 'Không tìm thấy sổ tiết kiệm!'}), 404
            
        account = {
            'account_id': row[0],
            'customer_name': row[1],
            'identity_card': row[2],
            'product_name': row[3],
            'principal_balance': float(row[4]),
            'opened_at': str(row[5]),
            'status': row[6],
            'interest_rate': float(row[7]),
            'term_months': row[8],
            'min_days_hold': row[9]
        }
        return jsonify({
            'message': 'Chi tiết sổ tiết kiệm',
            'account': account
        }), 200
    except Exception as e:
        return jsonify({'message': 'Lỗi server!', 'error': str(e)}), 500


@transactions_bp.route('/api/reports/daily-activity', methods=['GET'])
@require_role(['STAFF', 'ADMIN'])
def get_daily_activity_report():
    """BM5.1: Báo cáo doanh số hoạt động ngày theo loại tiết kiệm."""
    report_date = request.args.get('date')
    if not report_date:
        return jsonify({'message': 'Vui lòng truyền query date theo định dạng YYYY-MM-DD!'}), 400

    try:
        db_cursor.execute(
            """
            SELECT
                COALESCE(p.name, target_p.name, 'Ví điện tử') AS product_name,
                SUM(CASE
                    WHEN t.transaction_type IN ('OPEN_SAVINGS', 'DEPOSIT_TO_SAVINGS', 'DEPOSIT_TO_WALLET')
                    THEN t.amount ELSE 0 END) AS total_in,
                SUM(CASE
                    WHEN t.transaction_type IN ('WITHDRAW_FROM_SAVINGS', 'CLOSE_SAVINGS', 'WITHDRAW_FROM_WALLET')
                    THEN t.amount + COALESCE(t.interest_amount, 0) ELSE 0 END) AS total_out
            FROM transactions t
            LEFT JOIN savings_accounts s ON t.account_id = s.account_id
            LEFT JOIN savings_products p ON s.product_id = p.product_id
            LEFT JOIN savings_products target_p ON t.target_product_id = target_p.product_id
            WHERE DATE(t.created_at) = %s AND t.status = 'APPROVED'
            GROUP BY product_name
            ORDER BY product_name
            """,
            (report_date,)
        )
        rows = db_cursor.fetchall()
        items = [
            {
                'product_name': row[0],
                'total_in': float(row[1] or 0),
                'total_out': float(row[2] or 0),
                'difference': float((row[1] or 0) - (row[2] or 0))
            }
            for row in rows
        ]
        return jsonify({'message': 'Báo cáo doanh số hoạt động ngày', 'date': report_date, 'items': items}), 200
    except Exception as e:
        return jsonify({'message': 'Lỗi server!', 'error': str(e)}), 500


@transactions_bp.route('/api/reports/monthly-open-close', methods=['GET'])
@require_role(['STAFF', 'ADMIN'])
def get_monthly_open_close_report():
    """BM5.2: Báo cáo mở/đóng sổ tháng theo loại tiết kiệm."""
    month = request.args.get('month')
    product_id = request.args.get('product_id')
    if not month:
        return jsonify({'message': 'Vui lòng truyền query month theo định dạng YYYY-MM!'}), 400

    params = [month]
    product_filter = ""
    if product_id:
        product_filter = " AND COALESCE(s.product_id, t.target_product_id) = %s"
        params.append(product_id)

    try:
        db_cursor.execute(
            f"""
            SELECT
                DATE(t.created_at) AS report_day,
                COALESCE(p.name, target_p.name) AS product_name,
                SUM(CASE WHEN t.transaction_type = 'OPEN_SAVINGS' THEN 1 ELSE 0 END) AS opened_count,
                SUM(CASE WHEN t.transaction_type = 'CLOSE_SAVINGS' THEN 1 ELSE 0 END) AS closed_count
            FROM transactions t
            LEFT JOIN savings_accounts s ON t.account_id = s.account_id
            LEFT JOIN savings_products p ON s.product_id = p.product_id
            LEFT JOIN savings_products target_p ON t.target_product_id = target_p.product_id
            WHERE DATE_FORMAT(t.created_at, '%Y-%m') = %s
              AND t.status = 'APPROVED'
              AND t.transaction_type IN ('OPEN_SAVINGS', 'CLOSE_SAVINGS')
              {product_filter}
            GROUP BY report_day, product_name
            ORDER BY report_day ASC, product_name ASC
            """,
            tuple(params)
        )
        rows = db_cursor.fetchall()
        items = [
            {
                'date': str(row[0]),
                'product_name': row[1],
                'opened_count': int(row[2] or 0),
                'closed_count': int(row[3] or 0),
                'difference': int((row[2] or 0) - (row[3] or 0))
            }
            for row in rows
        ]
        return jsonify({'message': 'Báo cáo mở/đóng sổ tháng', 'month': month, 'items': items}), 200
    except Exception as e:
        return jsonify({'message': 'Lỗi server!', 'error': str(e)}), 500
