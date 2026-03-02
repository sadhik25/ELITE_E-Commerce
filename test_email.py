import smtplib
import config

def test_gmail_connection():
    print("--- Gmail Connection Test ---")
    print(f"Username: {config.MAIL_USERNAME}")
    print(f"Password: {'*' * len(config.MAIL_PASSWORD)} (Length: {len(config.MAIL_PASSWORD)})")
    
    # Process password like in app.py
    password = "".join(config.MAIL_PASSWORD.split())
    print(f"Processed Password Length: {len(password)}")
    
    try:
        print("Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("Logging in...")
        server.login(config.MAIL_USERNAME, password)
        print("SUCCESS: Login successful!")
        server.quit()
    except Exception as e:
        print(f"FAILURE: Login failed.")
        print(f"Error Message: {e}")
        print("\nCommon fixes for Gmail 535 Error:")
        print("1. Ensure 2-Step Verification is ENABLED on your Google Account.")
        print("2. Create a NEW 'App Password' at: https://myaccount.google.com/apppasswords")
        print("3. Use the 16-character code from Google as your MAIL_PASSWORD in config.py.")

if __name__ == "__main__":
    test_gmail_connection()
