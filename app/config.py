import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_USER") or os.getenv("EMAIL_USER_1", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or os.getenv("EMAIL_PASSWORD_1", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.png', '.docx', '.xlsx'}
MAX_FILE_SIZE_MB = 5
BULK_EMAIL_DELAY = float(os.getenv("BULK_EMAIL_DELAY", 2))
LOG_FILE = "logs/email_log.txt"
