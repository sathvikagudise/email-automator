"""
Pre-populates demo data so the app looks "live" during a demo.
Run this BEFORE launching the frontend.
"""
import os
import sys
import csv
from datetime import datetime, timedelta
from pathlib import Path

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.generate_pdf import generate_sample_pdf
from app.security import encrypt_message
from app.scheduler import schedule_email, _generate_task_id

DATA_DIR = os.path.join(project_root, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ─── 1. Generate sample PDF ────────────────────────────────────────────────
print("[1/5] Generating sample PDF...")
pdf_path = generate_sample_pdf("demo_invoice.pdf")
print(f"  -> {pdf_path}")

# ─── 2. Create sample recipients CSV ───────────────────────────────────────
print("[2/5] Creating sample recipients CSV...")
csv_path = os.path.join(DATA_DIR, "recipients.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "email"])
    writer.writerow(["Alice Johnson", "alice.johnson@example.com"])
    writer.writerow(["Bob Smith", "bob.smith@example.com"])
    writer.writerow(["Charlie Brown", "charlie.brown@example.com"])
    writer.writerow(["Diana Prince", "diana.prince@example.com"])
    writer.writerow(["Eve Adams", "eve.adams@example.com"])
print(f"  -> {csv_path} (5 recipients)")

# ─── 3. Pre-encrypt a demo message ──────────────────────────────────────────
print("[3/5] Creating encrypted demo output...")
encrypted = encrypt_message("Welcome to the Automatic Email Generator!\nThis is a proof of successful encryption and decryption.")
enc_path = os.path.join(DATA_DIR, "demo_encrypted.txt")
with open(enc_path, "w", encoding="utf-8") as f:
    f.write(encrypted)
print(f"  -> {enc_path}")

# ─── 4. Schedule demo emails ──────────────────────────────────────────────
print("[4/5] Scheduling demo emails...")
# Schedule for tomorrow so they show up in "View Scheduled"
tomorrow_10am = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
tomorrow_2pm = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
day_after = (datetime.now() + timedelta(days=2)).replace(hour=9, minute=30, second=0, microsecond=0)

schedule_email(
    send_time=tomorrow_10am.strftime("%Y-%m-%d %H:%M"),
    email_list=["alice@example.com", "bob@example.com"],
    subject="Weekly Newsletter - Issue #42",
    body="Hi {name},\n\nHere is this week's newsletter with all the latest updates.\n\nBest,\nThe Team",
    task_id="demo_weekly_newsletter"
)

schedule_email(
    send_time=tomorrow_2pm.strftime("%Y-%m-%d %H:%M"),
    email_list=["diana@example.com"],
    subject="Meeting Reminder: Project Review",
    body="Hi Diana,\n\nThis is a reminder about the project review meeting tomorrow.\n\nRegards,\nScheduler",
    task_id="demo_meeting_reminder",
    single_recipient=True
)

schedule_email(
    send_time=day_after.strftime("%Y-%m-%d %H:%M"),
    email_list=["charlie@example.com", "eve@example.com"],
    subject="Invoice #1234 - Payment Due",
    body="Dear {name},\n\nYour invoice is due for payment. Please find the details attached.\n\nThank you.",
    task_id="demo_invoice_reminder"
)
print(f"  -> 3 emails scheduled for the next 2 days")

# ─── 5. Summary ────────────────────────────────────────────────────────────
print("\n[5/5] Demo data setup complete!")
print("=" * 50)
print("  Files created:")
print(f"    - data/demo_invoice.pdf")
print(f"    - data/recipients.csv (5 contacts)")
print(f"    - data/demo_encrypted.txt")
print(f"  Scheduled tasks active:")
print(f"    - demo_weekly_newsletter (tomorrow 10:00)")
print(f"    - demo_meeting_reminder (tomorrow 14:00)")
print(f"    - demo_invoice_reminder (day after 09:30)")
print("=" * 50)
print("\nNow launch the frontend: python -m streamlit run frontend/app.py")
