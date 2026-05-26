from datetime import datetime
from dateutil.relativedelta import relativedelta


DEMO_MINUTES_PER_YEAR = 12
MINUTES_PER_DAY = 24 * 60
DAYS_PER_YEAR = 365
MIN_OPEN_AMOUNT_KEY = "MIN_OPEN_AMOUNT"
MIN_SAVINGS_DEPOSIT_AMOUNT_KEY = "MIN_SAVINGS_DEPOSIT_AMOUNT"
NON_TERM_MIN_DAYS_KEY = "NON_TERM_MIN_DAYS"

MIN_OPEN_AMOUNT_FALLBACK = 1000000


DEFAULT_CONFIGS = {
    MIN_OPEN_AMOUNT_KEY: ("1000000", "So tien toi thieu khi mo so tiet kiem (QD1: 1.000.000d)"),
    MIN_SAVINGS_DEPOSIT_AMOUNT_KEY: ("100000", "So tien toi thieu khi gui them vao so (QD2: 100.000d)"),
    NON_TERM_MIN_DAYS_KEY: ("15", "So ngay toi thieu de rut so khong ky han (QD3: 15 ngay)"),
}


def get_config(cursor, key, default_value):
    cursor.execute("SELECT config_value FROM system_configs WHERE config_key = %s", (key,))
    row = cursor.fetchone()
    return row[0] if row else default_value


def get_float_config(cursor, key, default_value):
    try:
        return float(get_config(cursor, key, default_value))
    except (TypeError, ValueError):
        return float(default_value)


def get_int_config(cursor, key, default_value):
    try:
        return int(float(get_config(cursor, key, default_value)))
    except (TypeError, ValueError):
        return int(default_value)


def days_between(started_at, ended_at=None):
    """Return the number of real days elapsed between two timestamps."""
    if isinstance(started_at, str):
        started_at = datetime.fromisoformat(started_at)
    ended_at = ended_at or datetime.now()
    return max((ended_at - started_at).total_seconds() / 86400, 0)


def term_days(term_months):
    """Convert term_months (business months) to real days.

    Real mode: 1 month = 30 days.
    """
    return int(term_months or 0) * 30


def rule_days_to_real_days(rule_days):
    """In real mode, rule days are actual calendar days."""
    return max(float(rule_days or 0), 0)


def years_from_days(days_held):
    """Convert days to years for interest calculation (365 days = 1 year)."""
    return max(float(days_held or 0), 0) / DAYS_PER_YEAR


def calculate_interest(principal, annual_rate, days_held):
    """Calculate interest based on real calendar days."""
    principal = float(principal or 0)
    annual_rate = float(annual_rate or 0)
    years = years_from_days(days_held)
    return round(principal * annual_rate / 100 * years, 2)


def get_non_term_rate(cursor):
    """Get the interest rate of the non-term product (KKH) for early withdrawal."""
    cursor.execute(
        "SELECT interest_rate FROM savings_products WHERE term_months = 0 AND is_active = TRUE LIMIT 1"
    )
    row = cursor.fetchone()
    return float(row[0]) if row else 0.5


def get_applicable_interest_rate(cursor, term_months, product_rate, days_held):
    """Determine the correct interest rate based on QĐ3.

    - Term product withdrawn BEFORE maturity → use non-term rate (0.5%)
    - Term product withdrawn ON or AFTER maturity → use product rate
    - Non-term product → always use product rate (already 0.5%)
    """
    term_months_val = int(term_months or 0)

    if term_months_val == 0:
        # Non-term: always use own rate
        return float(product_rate)

    # Term product: check if matured
    maturity_real_days = term_days(term_months_val)
    if days_held < maturity_real_days:
        # Early withdrawal → apply non-term rate per QĐ3
        return get_non_term_rate(cursor)
    else:
        return float(product_rate)


def demo_maturity_date(opened_at, term_months):
    """Calculate the display maturity date (business calendar).

    Even though demo runs in minutes, we display the maturity date
    as if it were real months from the opened_at date.
    """
    if isinstance(opened_at, str):
        opened_at = datetime.fromisoformat(opened_at)
    term_val = int(term_months or 0)
    if term_val == 0:
        return None  # Non-term has no maturity
    return (opened_at + relativedelta(months=term_val)).strftime("%Y-%m-%d")


def demo_elapsed_display(opened_at):
    """Convert real elapsed time to a display string in months/days.

    Returns a string like "2 tháng 15 ngày".
    """
    if isinstance(opened_at, str):
        opened_at = datetime.fromisoformat(opened_at)
    held_days = days_between(opened_at)
    real_months = int(held_days // 30)
    remaining_days = int(held_days % 30)

    parts = []
    if real_months > 0:
        parts.append(f"{real_months} tháng")
    if remaining_days > 0 or not parts:
        parts.append(f"{remaining_days} ngày")
    return " ".join(parts)


def is_matured(opened_at, term_months):
    """Check if a term savings account has matured (demo time)."""
    term_val = int(term_months or 0)
    if term_val == 0:
        return False  # Non-term never matures
    held = days_between(opened_at)
    return held >= term_days(term_val)


def check_auto_rollover(cursor, conn, account_id):
    """Lazy auto-rollover: if a term account has matured, compound interest and reset.

    Returns True if rollover was performed, False otherwise.
    """
    cursor.execute(
        """
        SELECT s.account_id, s.principal_balance, s.opened_at, s.status, s.user_id,
               p.term_months, p.interest_rate
        FROM savings_accounts s
        JOIN savings_products p ON s.product_id = p.product_id
        WHERE s.account_id = %s AND s.status = 'ACTIVE'
        """,
        (account_id,)
    )
    row = cursor.fetchone()
    if not row:
        return False

    _, principal, opened_at, status, user_id, t_months, rate = row
    t_months = int(t_months or 0)
    if t_months == 0 or status != 'ACTIVE':
        return False

    held_days = days_between(opened_at)
    maturity = term_days(t_months)
    if held_days < maturity:
        return False

    # Calculate how many full terms have elapsed
    rollover_count = 0
    current_principal = float(principal)
    current_opened = opened_at if not isinstance(opened_at, str) else datetime.fromisoformat(opened_at)

    while True:
        elapsed = days_between(current_opened)
        mat = term_days(t_months)
        if elapsed < mat:
            break
        # One term has passed: compute interest for exactly one term
        interest = calculate_interest(current_principal, float(rate), mat)
        current_principal += interest
        # Advance opened_at by one term (in real time: term_months months)
        current_opened = current_opened + relativedelta(months=t_months)
        rollover_count += 1
        # Safety: prevent infinite loop
        if rollover_count > 100:
            break

    if rollover_count == 0:
        return False

    # Update the account
    cursor.execute(
        """
        UPDATE savings_accounts
        SET principal_balance = %s, opened_at = %s
        WHERE account_id = %s
        """,
        (round(current_principal, 2), current_opened, account_id)
    )

    # Record a summary rollover transaction
    total_interest = round(current_principal - float(principal), 2)
    cursor.execute(
        """
        INSERT INTO transactions
            (user_id, account_id, amount, transaction_type, status, interest_amount, processed_by)
        VALUES (%s, %s, %s, 'AUTO_ROLLOVER', 'APPROVED', %s, NULL)
        """,
        (user_id, account_id, float(principal), total_interest)
    )
    conn.commit()
    return True


def ensure_default_configs(cursor):
    for key, (value, description) in DEFAULT_CONFIGS.items():
        cursor.execute(
            """
            INSERT INTO system_configs (config_key, config_value, description)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE description = VALUES(description)
            """,
            (key, value, description)
        )
