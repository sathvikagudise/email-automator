import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER") or os.getenv("EMAIL_USER_1", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or os.getenv("EMAIL_PASSWORD_1", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def send_email(recipient, subject, body, attachments=None, html=False):
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            raise ValueError("SMTP credentials are missing. Check your .env file.")

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = recipient
        msg["Subject"] = subject

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        if attachments:
            for file in attachments:
                if os.path.exists(file):
                    with open(file, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file)}")
                        msg.attach(part)
                else:
                    logging.warning(f"Attachment not found: {file}")

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, recipient, msg.as_string())
        server.quit()

        logging.info(f"Email sent successfully to {recipient}")

    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP Authentication Error: Check your email and app password.")
    except smtplib.SMTPException as smtp_error:
        logging.error(f"SMTP Error: {smtp_error}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    send_email("test@example.com", "Test Subject", "This is a test email.")
