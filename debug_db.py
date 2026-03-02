import sqlite3
import os
import config

conn = sqlite3.connect(os.path.abspath(config.DATABASE))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- Categories in DB ---")
cursor.execute("SELECT DISTINCT category FROM products")
cats = cursor.fetchall()
for c in cats:
    print(f"'{c['category']}'")

print("\n--- Products Count by Category ---")
cursor.execute("SELECT category, COUNT(*) as count FROM products GROUP BY category")
counts = cursor.fetchall()
for c in counts:
    print(f"'{c['category']}': {c['count']}")

print("\n--- Products in Sports ---")
cursor.execute("SELECT name, category, image FROM products WHERE category = 'Sports'")
for p in cursor.fetchall():
    print(f"'{p['name']}' -> '{p['image']}'")

print("\n--- Products in Footwear ---")
cursor.execute("SELECT name, category, image FROM products WHERE category = 'Footwear'")
for p in cursor.fetchall():
    print(f"'{p['name']}' -> '{p['image']}'")

print("\n--- Products in Electronics ---")
cursor.execute("SELECT name, category, image FROM products WHERE category = 'Electronics'")
for p in cursor.fetchall():
    print(f"'{p['name']}' -> '{p['image']}'")

cursor.close()
conn.close()
