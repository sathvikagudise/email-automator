import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER") or os.getenv("EMAIL_USER_1", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or os.getenv("EMAIL_PASSWORD_1", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


def compose_email(recipient, subject, body, attachments=None, html=False):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = recipient
        msg["Subject"] = subject

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    attach_file(msg, file_path)
                else:
                    print(f"Warning: Attachment '{file_path}' not found, skipping.")

        print("Email composed successfully!")
        return msg

    except Exception as e:
        print(f"Error composing email: {e}")
        return None


def attach_file(msg, file_path):
    try:
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

        print(f"Attached: {filename}")

    except Exception as e:
        print(f"Failed to attach file '{file_path}': {e}")


def send_composed_email(recipient, subject, body, attachments=None, html=False):
    msg = compose_email(recipient, subject, body, attachments, html)
    if not msg:
        print("Email composition failed. Aborting send.")
        return

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        server.sendmail(EMAIL_USER, recipient, msg.as_string())
        server.quit()

        print(f"Email sent successfully to {recipient}!")

    except smtplib.SMTPAuthenticationError:
        print(f"Authentication failed. Check your email credentials.")
    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == "__main__":
    send_composed_email(
        "test@example.com",
        "Test Email",
        "Hello,\n\nThis is a test email.\n\nBest Regards!"
    )
