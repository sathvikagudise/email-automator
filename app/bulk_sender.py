import os
import smtplib
import time
import csv
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from app.attachment_handler import attach_files

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER") or os.getenv("EMAIL_USER_1", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or os.getenv("EMAIL_PASSWORD_1", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_recipients(file_path):
    recipients = []
    if not os.path.exists(file_path):
        logging.error(f"Recipients file '{file_path}' not found!")
        return recipients

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    recipients.append({"name": row[0].strip(), "email": row[1].strip()})
    except Exception as e:
        logging.error(f"Error loading recipients: {e}")

    return recipients


def send_bulk_emails(recipients, subject, body, attachments=None, html=False):
    if not recipients:
        logging.error("No recipients found.")
        return

    if not EMAIL_USER or not EMAIL_PASSWORD:
        logging.error("SMTP credentials missing. Check your .env file.")
        return

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        logging.info("Connected to SMTP server!")

        for recipient in recipients:
            try:
                if isinstance(recipient, str):
                    name = ""
                    to_email = recipient
                else:
                    name = recipient.get("name", "")
                    to_email = recipient.get("email", recipient)

                msg = MIMEMultipart()
                msg["From"] = EMAIL_USER
                msg["To"] = to_email
                msg["Subject"] = subject

                personalized_body = body.replace("{name}", name) if name else body

                if html:
                    msg.attach(MIMEText(personalized_body, "html"))
                else:
                    msg.attach(MIMEText(personalized_body, "plain"))

                valid_attachments = [f for f in (attachments or []) if os.path.exists(f)]
                if valid_attachments:
                    attach_files(msg, valid_attachments)

                server.sendmail(EMAIL_USER, to_email, msg.as_string())
                logging.info(f"Email sent to {name or to_email} ({to_email})")

                time.sleep(2)

            except Exception as email_error:
                logging.error(f"Failed to send email to {recipient}: {email_error}")

        server.quit()
        logging.info("All emails processed successfully!")

    except smtplib.SMTPAuthenticationError:
        logging.error("Authentication Error: Check your email and app password!")
    except Exception as e:
        logging.error(f"Error sending bulk emails: {e}")


if __name__ == "__main__":
    recipients = load_recipients("data/recipients.csv")
    send_bulk_emails(recipients, "Important Notification", "Hello {name},\n\nThis is a bulk email test.\n\nBest regards,\nYour Team")
