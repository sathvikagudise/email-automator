import os
from dotenv import load_dotenv

load_dotenv()

print("Environment Variables:")
print(f"  EMAIL_USER_1:     {os.getenv('EMAIL_USER_1')}")
print(f"  EMAIL_PASSWORD_1: {'****' if os.getenv('EMAIL_PASSWORD_1') else 'Not set'}")
print(f"  EMAIL_USER_2:     {os.getenv('EMAIL_USER_2')}")
print(f"  EMAIL_PASSWORD_2: {'****' if os.getenv('EMAIL_PASSWORD_2') else 'Not set'}")
print(f"  SMTP_SERVER:      {os.getenv('SMTP_SERVER')}")
print(f"  SMTP_PORT:        {os.getenv('SMTP_PORT')}")
print(f"  IMAP_SERVER:      {os.getenv('IMAP_SERVER')}")
print()
print("All variables loaded successfully!" if os.getenv("EMAIL_USER_1") else "WARNING: No credentials found!")
