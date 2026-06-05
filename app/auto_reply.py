import os
import smtplib
import imaplib
import email
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER") or os.getenv("EMAIL_USER_1", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or os.getenv("EMAIL_PASSWORD_1", "")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

AUTO_REPLY_SUBJECT = "Re: Your Email"
AUTO_REPLY_BODY = """
Hello,

Thank you for reaching out. I'm currently unavailable but will get back to you as soon as possible.

Best regards,
{name}
"""

CHECK_INTERVAL = 60
AUTO_REPLY_NAME = os.getenv("AUTO_REPLY_NAME", "Auto-Reply Bot")


def check_inbox():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()

        if not email_ids:
            print("No new unread emails.")
            mail.logout()
            return

        print(f"Found {len(email_ids)} new unread email(s)!")

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)") or (None, [None])

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    sender_email = email.utils.parseaddr(msg["From"])[1]

                    print(f"New email from: {sender_email}")
                    send_auto_reply(sender_email)
                    mail.store(email_id, "+FLAGS", "\\Seen")

        mail.logout()
        print("Auto-reply process completed.")

    except Exception as e:
        print(f"Error checking inbox: {e}")


def send_auto_reply(to_email):
    try:
        print(f"Sending auto-reply to {to_email}...")

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = AUTO_REPLY_SUBJECT

        personalized_body = AUTO_REPLY_BODY.replace("{name}", AUTO_REPLY_NAME)
        msg.attach(MIMEText(personalized_body, "plain"))

        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()

        print(f"Auto-reply sent to {to_email}")

    except Exception as e:
        print(f"Failed to send auto-reply to {to_email}: {e}")


if __name__ == "__main__":
    print("Starting auto-reply monitor...")
    while True:
        print("\nChecking for new emails...")
        check_inbox()
        print(f"Waiting {CHECK_INTERVAL} seconds before checking again...")
        time.sleep(CHECK_INTERVAL)
