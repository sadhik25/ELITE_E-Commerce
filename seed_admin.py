import sqlite3
import bcrypt
import config
import os

def seed_admin():
    conn = sqlite3.connect(os.path.abspath(config.DATABASE))
    cursor = conn.cursor()
    
    password = "admin" # Default password for seeding
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Check if admin already exists
    cursor.execute("SELECT * FROM admin WHERE email = ?", (config.MAIL_USERNAME,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO admin (name, email, password, is_superadmin, is_approved) VALUES (?, ?, ?, 1, 1)",
            ("Super Admin", config.MAIL_USERNAME, hashed_password)
        )
        conn.commit()
        print(f"Super Admin created with email: {config.MAIL_USERNAME} and password: {password}")
    else:
        print("Super Admin already exists.")
        
    conn.close()

    

if __name__ == '__main__':
    seed_admin()
