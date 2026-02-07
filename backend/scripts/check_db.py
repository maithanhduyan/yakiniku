"""Quick script to check DB tables and add missing columns."""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'yakiniku.db')
print(f"DB path: {os.path.abspath(db_path)}")
print(f"DB exists: {os.path.exists(db_path)}")

if not os.path.exists(db_path):
    print("No local DB file found. It will be created on next backend start with all columns.")
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"Tables: {tables}")

if 'devices' in tables:
    cursor = conn.execute("PRAGMA table_info(devices)")
    cols = [row[1] for row in cursor.fetchall()]
    print(f"Devices columns: {cols}")

    # Add missing columns
    new_cols = {
        'device_fingerprint': 'VARCHAR(64)',
        'session_token': 'VARCHAR(64)',
        'session_expires_at': 'DATETIME',
    }
    for col_name, col_type in new_cols.items():
        if col_name not in cols:
            sql = f"ALTER TABLE devices ADD COLUMN {col_name} {col_type}"
            print(f"Adding column: {sql}")
            conn.execute(sql)
        else:
            print(f"Column {col_name} already exists")

    conn.commit()
    print("Done! Columns updated.")
else:
    print("Devices table does not exist yet — it will be created on next backend start.")

conn.close()
