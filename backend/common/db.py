import mysql.connector
import os

# Cấu hình DB dùng chung toàn backend.
# Có thể override qua biến môi trường: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "database": os.getenv("DB_NAME", "modern_savings_db")
}

db_conn = mysql.connector.connect(**DB_CONFIG)
db_cursor = db_conn.cursor()
