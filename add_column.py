import sqlite3
import os
import config

def add_bestseller_column():
    try:
        conn = sqlite3.connect(os.path.abspath(config.DATABASE))
        cursor = conn.cursor()
        
        # Add is_bestseller column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN is_bestseller INTEGER DEFAULT 0")
            print("Successfully added is_bestseller column.")
        except sqlite3.OperationalError as err:
            if "duplicate column name" in str(err).lower():
                print("Column is_bestseller already exists.")
            else:
                print(f"Error: {err}")
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == '__main__':
    add_bestseller_column()
