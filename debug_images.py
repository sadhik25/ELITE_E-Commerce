
import sqlite3
import os

db_path = os.path.join('database', 'smart_db.sqlite')
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    cursor.execute("SELECT product_id, name, image FROM products LIMIT 20")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row['product_id']}, Name: {row['name']}, Image: {row['image']}")
except Exception as e:
    print(f"Error: {e}")

conn.close()
