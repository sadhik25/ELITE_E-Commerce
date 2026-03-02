import sqlite3
import os

def init_db():
    if not os.path.exists('database'):
        os.makedirs('database')
    
    conn = sqlite3.connect('database/smart_db.sqlite')
    cursor = conn.cursor()

    # 1. Admin Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        is_superadmin INTEGER DEFAULT 0,
        is_approved INTEGER DEFAULT 0,
        profile_image TEXT
    )
    ''')

    # 2. Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        price REAL NOT NULL,
        image TEXT,
        image2 TEXT,
        image3 TEXT,
        is_bestseller INTEGER DEFAULT 0,
        added_by INTEGER,
        rating REAL DEFAULT 4.5,
        rating_count INTEGER DEFAULT 120,
        FOREIGN KEY (added_by) REFERENCES admin (admin_id)
    )
    ''')

    # 3. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        city TEXT,
        pincode TEXT,
        profile_image TEXT
    )
    ''')

    # 4. User Addresses Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_addresses (
        address_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        address_line TEXT,
        city TEXT,
        pincode TEXT,
        phone TEXT,
        is_default INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    # 5. Orders Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders_table (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL NOT NULL,
        payment_id TEXT,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        address TEXT,
        city TEXT,
        pincode TEXT,
        phone TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    # 6. Order Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items_table (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders_table (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')

    # 7. OTP Reset Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS otp_reset (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        otp TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_used INTEGER DEFAULT 0
    )
    ''')

    # Insert a super admin if not exists (using the one from config or a default)
    # Note: password will need to be hashed by the app later if reset, but we can leave it empty for now or add a default.
    
    conn.commit()
    conn.close()
    print("SQLite Database initialized successfully at database/smart_db.sqlite")

if __name__ == '__main__':
    init_db()
