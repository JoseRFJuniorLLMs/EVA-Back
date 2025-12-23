
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eva_saude.db")
print(f"Checking DB at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(historico);")
    columns = cursor.fetchall()
    print("Columns in 'historico':")
    for c in columns:
        print(f" - {c[1]} ({c[2]})")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
