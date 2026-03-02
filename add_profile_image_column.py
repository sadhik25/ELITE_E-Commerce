import sqlite3
import os
import config

def get_db_connection():
    return sqlite3.connect(os.path.abspath(config.DATABASE))

def check_and_fix_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if profile_image column exists in users table in SQLite
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'profile_image' not in columns:
        print("Adding 'profile_image' column to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT DEFAULT NULL")
        conn.commit()
    else:
        print("'profile_image' column already exists in 'users' table.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_and_fix_users()
