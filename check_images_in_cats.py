import sqlite3
import os
import config

conn = sqlite3.connect(os.path.abspath(config.DATABASE))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

for cat in ['Fashion', 'Laptops', 'Sports', 'Electronics']:
    print(f"\n--- Products in {cat} ---")
    cursor.execute(f"SELECT name, image FROM products WHERE category = '{cat}'")
    for p in cursor.fetchall():
        print(f"'{p['name']}' -> '{p['image']}'")

cursor.close()
conn.close()
