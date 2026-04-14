import mysql.connector

# ⚠️ Sửa password cho đúng môi trường của bạn
db_conn = mysql.connector.connect(
    host='localhost',
    user='smart_savings',
    password='password123',
    database='modern_savings_db'
)
db_cursor = db_conn.cursor()
