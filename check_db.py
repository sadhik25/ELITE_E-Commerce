import sqlite3
import os
import config

def check_db():
    try:
        conn = sqlite3.connect(os.path.abspath(config.DATABASE))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM products")
        cats = cursor.fetchall()
        print("Categories in DB:")
        for c in cats:
            print(f"- '{c['category']}'")
            
        cursor.execute("SELECT name, category, image FROM products LIMIT 10")
        prods = cursor.fetchall()
        print("\nFirst 10 products:")
        for p in prods:
            print(f"- {p['name']} ({p['category']}) -> {p['image']}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == '__main__':
    check_db()
