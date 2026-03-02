import os
# config.py
# ------------------------------------
# This file holds all configurations
# like Secret Key, Database connection
# details, Email settings, Razorpay keys etc.
# ------------------------------------

SECRET_KEY = "sadhikso"   # used for sessions

# MySQL Database Configuration (DEPRECATED)
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Sadhik@0325"
DB_NAME = "smart_db"

# SQLite Database Configuration
DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'smart_db.sqlite')




# Email SMTP Settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'shaiksadhik1225@gmail.com'
MAIL_PASSWORD = 'vaqanqoeieltznah'   # Gmail App Password




RAZORPAY_KEY_ID = "rzp_test_SKLYLFiWOIxoIj"
RAZORPAY_KEY_SECRET = "3GBHvBhM7CJYQsswp0BsLrzP"


