import mysql.connector
import os
import threading

# Cấu hình DB dùng chung toàn backend.
# Có thể override qua biến môi trường: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "smart_savings"),
    "password": os.getenv("DB_PASSWORD", "SmartSavings@2026!"),
    "database": os.getenv("DB_NAME", "modern_savings_db")
}

_db_state = threading.local()


def _connect():
    return mysql.connector.connect(**DB_CONFIG)


def _get_connection():
    conn = getattr(_db_state, "connection", None)
    if conn is None or not conn.is_connected():
        conn = _connect()
        _db_state.connection = conn
        _db_state.cursor = conn.cursor(buffered=True)
    return conn


def _get_cursor():
    _get_connection()
    cursor = getattr(_db_state, "cursor", None)
    if cursor is None:
        cursor = _db_state.connection.cursor(buffered=True)
        _db_state.cursor = cursor
    return cursor


class DbConnectionProxy:
    def __getattr__(self, name):
        return getattr(_get_connection(), name)


class DbCursorProxy:
    def __getattr__(self, name):
        return getattr(_get_cursor(), name)

    def execute(self, *args, **kwargs):
        return _get_cursor().execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return _get_cursor().executemany(*args, **kwargs)

    def fetchone(self):
        return _get_cursor().fetchone()

    def fetchall(self):
        return _get_cursor().fetchall()


db_conn = DbConnectionProxy()
db_cursor = DbCursorProxy()
