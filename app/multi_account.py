import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

ACCOUNTS = [
    {
        "email": os.getenv("EMAIL_USER_1"),
        "password": os.getenv("EMAIL_PASSWORD_1")
    },
    {
        "email": os.getenv("EMAIL_USER_2"),
        "password": os.getenv("EMAIL_PASSWORD_2")
    },
]

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


def send_email_multi(sender_index, recipients, subject, body, html=False):
    if sender_index >= len(ACCOUNTS) or not ACCOUNTS[sender_index]["email"]:
        print(f"Error: No email account configured at index {sender_index}. Check your .env file.")
        return

    sender = ACCOUNTS[sender_index]
    sender_email = sender["email"]
    sender_password = sender["password"]

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)

        if isinstance(recipients, str):
            recipients = [recipients]

        for recipient in recipients:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient
            msg["Subject"] = subject

            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))

            server.sendmail(sender_email, recipient, msg.as_string())
            print(f"Email sent from {sender_email} to {recipient}")

        server.quit()

    except smtplib.SMTPAuthenticationError:
        print(f"Authentication failed for {sender_email}. Check your email/password.")
    except Exception as e:
        print(f"Error sending email from {sender_email}: {e}")


if __name__ == "__main__":
    send_email_multi(
        sender_index=0,
        recipients=["test@example.com"],
        subject="Multi-Account Email Test",
        body="This is a test email sent from the multi-account system."
    )
