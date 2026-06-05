import os
import sys
import time
from datetime import datetime

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import EMAIL_ADDRESS, SMTP_SERVER, SMTP_PORT
from app.smtp_client import send_email
from app.bulk_sender import send_bulk_emails, load_recipients
from app.scheduler import schedule_email, list_scheduled_emails, cancel_scheduled_email
from app.security import encrypt_message, decrypt_message
from app.email_composer import send_composed_email
from app.multi_account import send_email_multi, ACCOUNTS
from app.auto_reply import check_inbox
from app.generate_pdf import generate_sample_pdf


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    print("=" * 60)
    print("             AUTOMATIC EMAIL GENERATOR")
    print("=" * 60)
    print(f"  Account: {EMAIL_ADDRESS or 'Not configured'}")
    print(f"  Server:  {SMTP_SERVER}:{SMTP_PORT}")
    print("=" * 60)


def print_menu():
    print("""
  EMAIL OPERATIONS:
    1.  Send a Single Email
    2.  Send Bulk Emails (from CSV)
    3.  Send Bulk Emails (manual entry)
    4.  Send HTML Email

  SCHEDULER:
    5.  Schedule an Email
    6.  View Scheduled Emails
    7.  Cancel a Scheduled Email

  SECURITY:
    8.  Encrypt & Decrypt Message

  MULTI-ACCOUNT:
    9.  Send via Multi-Account

  AUTO-REPLY:
    10. Check Inbox & Auto-Reply

  UTILITIES:
    11. Generate Sample PDF
    12. Load Recipients from CSV

  SYSTEM:
    13. View Configuration
    14. Exit
""")


def get_attachments():
    path = input("  File paths (comma-separated) or Enter to skip: ").strip()
    if not path:
        return None
    return [a.strip() for a in path.split(",") if a.strip()]


def cmd_send_single():
    print("\n--- Send Single Email ---")
    recipient = input("  Recipient email: ").strip()
    subject = input("  Subject: ").strip()
    print("  Body (end with Ctrl+Z or empty line twice):")
    lines = []
    while True:
        line = input("  ")
        if line == "" and (not lines or lines[-1] == ""):
            break
        lines.append(line)
    body = "\n".join(lines).strip()
    attachments = get_attachments()
    send_email(recipient, subject, body, attachments)


def cmd_send_bulk_csv():
    print("\n--- Send Bulk Emails (from CSV) ---")
    csv_path = input("  CSV file path: ").strip()
    subject = input("  Subject: ").strip()
    print("  Body (use {name} for personalization):")
    body = input("  ").strip()
    attachments = get_attachments()
    recipients = load_recipients(csv_path)
    if recipients:
        send_bulk_emails(recipients, subject, body, attachments)
    else:
        print("No recipients loaded.")


def cmd_send_bulk_manual():
    print("\n--- Send Bulk Emails (Manual) ---")
    emails_input = input("  Recipient emails (comma-separated): ").strip()
    emails = [e.strip() for e in emails_input.split(",") if e.strip()]
    subject = input("  Subject: ").strip()
    print("  Body:")
    body = input("  ").strip()
    attachments = get_attachments()
    send_bulk_emails(emails, subject, body, attachments)


def cmd_send_html():
    print("\n--- Send HTML Email ---")
    recipient = input("  Recipient email: ").strip()
    subject = input("  Subject: ").strip()
    print("  HTML Body (raw HTML):")
    html_body = input("  ").strip()
    attachments = get_attachments()
    send_email(recipient, subject, html_body, attachments, html=True)


def cmd_schedule():
    print("\n--- Schedule Email ---")
    send_time = input("  Send time (YYYY-MM-DD HH:MM): ").strip()
    emails_input = input("  Recipient emails (comma-separated): ").strip()
    emails = [e.strip() for e in emails_input.split(",") if e.strip()]
    subject = input("  Subject: ").strip()
    print("  Body:")
    body = input("  ").strip()
    attachments = get_attachments()
    schedule_email(send_time, emails, subject, body, attachments)


def cmd_list_scheduled():
    print("\n--- Scheduled Emails ---")
    list_scheduled_emails()


def cmd_cancel_scheduled():
    print("\n--- Cancel Scheduled Email ---")
    task_id = input("  Task ID: ").strip()
    cancel_scheduled_email(task_id)


def cmd_encrypt():
    print("\n--- Encrypt / Decrypt ---")
    message = input("  Message to encrypt: ").strip()
    encrypted = encrypt_message(message)
    print(f"  Encrypted: {encrypted}")
    decrypted = decrypt_message(encrypted)
    print(f"  Decrypted: {decrypted}")


def cmd_multi_account():
    print("\n--- Multi-Account Send ---")
    print("  Available accounts:")
    for i, acc in enumerate(ACCOUNTS):
        status = acc["email"] or "Not configured"
        print(f"    [{i}] {status}")
    try:
        idx = int(input("  Select account index: ").strip())
    except ValueError:
        print("Invalid index.")
        return
    recipients_input = input("  Recipient emails (comma-separated): ").strip()
    recipients = [r.strip() for r in recipients_input.split(",") if r.strip()]
    subject = input("  Subject: ").strip()
    print("  Body:")
    body = input("  ").strip()
    send_email_multi(idx, recipients, subject, body)


def cmd_autoreply():
    print("\n--- Check Inbox & Auto-Reply ---")
    check_inbox()


def cmd_gen_pdf():
    print("\n--- Generate Sample PDF ---")
    filename = input("  Filename (default: sample.pdf): ").strip() or "sample.pdf"
    path = generate_sample_pdf(filename)
    print(f"  PDF saved to: {path}")


def cmd_load_csv():
    print("\n--- Load Recipients from CSV ---")
    csv_path = input("  CSV file path: ").strip()
    recipients = load_recipients(csv_path)
    print(f"  Loaded {len(recipients)} recipients:")
    for r in recipients[:10]:
        print(f"    - {r['name']} <{r['email']}>")
    if len(recipients) > 10:
        print(f"    ... and {len(recipients) - 10} more")


def cmd_config():
    print("\n--- Configuration ---")
    print(f"  EMAIL_ADDRESS:  {EMAIL_ADDRESS or 'Not set'}")
    print(f"  SMTP_SERVER:    {SMTP_SERVER}")
    print(f"  SMTP_PORT:      {SMTP_PORT}")
    print(f"  Allowed Extensions:   {', '.join(sorted({'.pdf', '.jpg', '.png', '.docx', '.xlsx'}))}")
    print(f"  Max Attachment Size:  5MB")


def main():
    menu_actions = {
        "1": cmd_send_single,
        "2": cmd_send_bulk_csv,
        "3": cmd_send_bulk_manual,
        "4": cmd_send_html,
        "5": cmd_schedule,
        "6": cmd_list_scheduled,
        "7": cmd_cancel_scheduled,
        "8": cmd_encrypt,
        "9": cmd_multi_account,
        "10": cmd_autoreply,
        "11": cmd_gen_pdf,
        "12": cmd_load_csv,
        "13": cmd_config,
    }

    while True:
        clear_screen()
        print_header()
        print_menu()

        choice = input("  Enter your choice (1-14): ").strip()

        if choice == "14":
            print("\n  Goodbye!")
            break

        action = menu_actions.get(choice)
        if action:
            action()
        else:
            print("\n  Invalid choice! Please try again.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Goodbye!")
        sys.exit(0)
