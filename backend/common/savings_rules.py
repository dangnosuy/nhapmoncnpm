from datetime import datetime


DEMO_MINUTES_PER_YEAR = 12
MINUTES_PER_DAY = 24 * 60
MIN_OPEN_AMOUNT_KEY = "MIN_OPEN_AMOUNT"
MIN_SAVINGS_DEPOSIT_AMOUNT_KEY = "MIN_SAVINGS_DEPOSIT_AMOUNT"
NON_TERM_MIN_DAYS_KEY = "NON_TERM_MIN_DAYS"


DEFAULT_CONFIGS = {
    MIN_OPEN_AMOUNT_KEY: ("50000", "So tien toi thieu khi mo so tiet kiem"),
    MIN_SAVINGS_DEPOSIT_AMOUNT_KEY: ("50000", "So tien toi thieu khi gui them vao so"),
    NON_TERM_MIN_DAYS_KEY: ("15", "So ngay toi thieu de rut so khong ky han"),
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
    if isinstance(started_at, str):
        started_at = datetime.fromisoformat(started_at)
    ended_at = ended_at or datetime.now()
    return max((ended_at - started_at).total_seconds() / 86400, 0)


def term_days(term_months):
    # Demo mode: 1 saved "month" maps to 1 real minute.
    return int(term_months or 0) / 1440


def rule_days_to_demo_days(rule_days):
    # Demo scale: 30 rule days = 1 real minute.
    return max(float(rule_days or 0), 0) / 30 / MINUTES_PER_DAY


def demo_years_from_real_days(days_held):
    real_minutes = max(float(days_held or 0), 0) * MINUTES_PER_DAY
    return real_minutes / DEMO_MINUTES_PER_YEAR


def calculate_interest(principal, annual_rate, days_held):
    principal = float(principal or 0)
    annual_rate = float(annual_rate or 0)
    demo_years = demo_years_from_real_days(days_held)
    return round(principal * annual_rate / 100 * demo_years, 2)


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
