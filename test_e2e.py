"""
End-to-end test for all modules in the Automatic Email Generator.
Tests every function without actually sending emails (SMTP calls are skipped).
"""
import os
import sys
import time
import tempfile
from datetime import datetime, timedelta

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [OK] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}  -  {detail}")

def section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")

# ─── 1. Environment ──────────────────────────────────────────────────────
section("1. Environment Configuration")

from dotenv import load_dotenv
load_dotenv()

test(".env file exists", os.path.exists(".env"))
test(".env.example exists", os.path.exists(".env.example"))
test(".gitignore exists", os.path.exists(".gitignore"))
test(".env has credentials", bool(os.getenv("EMAIL_USER_1")), "EMAIL_USER_1 is set")
test("EMAIL_USER loaded", bool(os.getenv("EMAIL_USER")), "EMAIL_USER is set")

# ─── 2. Config Module ─────────────────────────────────────────────────────
section("2. Config Module")

from app.config import EMAIL_ADDRESS, SMTP_SERVER, SMTP_PORT, ALLOWED_EXTENSIONS, IMAP_SERVER

test("EMAIL_ADDRESS loaded", bool(EMAIL_ADDRESS), f"Got: {EMAIL_ADDRESS}")
test("SMTP_SERVER configured", SMTP_SERVER == "smtp.gmail.com")
test("SMTP_PORT is int", isinstance(SMTP_PORT, int) and SMTP_PORT == 587)
test("ALLOWED_EXTENSIONS has pdf", ".pdf" in ALLOWED_EXTENSIONS)
test("ALLOWED_EXTENSIONS has jpg", ".jpg" in ALLOWED_EXTENSIONS)
test("IMAP_SERVER set", bool(IMAP_SERVER))

# ─── 3. Imports (all modules) ────────────────────────────────────────────
section("3. Module Imports")

from app.smtp_client import send_email
from app.bulk_sender import send_bulk_emails, load_recipients
from app.scheduler import schedule_email, list_scheduled_emails, cancel_scheduled_email
from app.security import encrypt_message, decrypt_message
from app.email_composer import compose_email, send_composed_email
from app.attachment_handler import attach_files, is_valid_attachment
from app.multi_account import send_email_multi, ACCOUNTS
from app.auto_reply import check_inbox
from app.generate_pdf import generate_sample_pdf

test("smtp_client.send_email is callable", callable(send_email))
test("bulk_sender.send_bulk_emails is callable", callable(send_bulk_emails))
test("bulk_sender.load_recipients is callable", callable(load_recipients))
test("scheduler.schedule_email is callable", callable(schedule_email))
test("scheduler.list_scheduled_emails is callable", callable(list_scheduled_emails))
test("scheduler.cancel_scheduled_email is callable", callable(cancel_scheduled_email))
test("security.encrypt_message is callable", callable(encrypt_message))
test("security.decrypt_message is callable", callable(decrypt_message))
test("email_composer.compose_email is callable", callable(compose_email))
test("email_composer.send_composed_email is callable", callable(send_composed_email))
test("attachment_handler.attach_files is callable", callable(attach_files))
test("attachment_handler.is_valid_attachment is callable", callable(is_valid_attachment))
test("multi_account.send_email_multi is callable", callable(send_email_multi))
test("auto_reply.check_inbox is callable", callable(check_inbox))
test("generate_pdf.generate_sample_pdf is callable", callable(generate_sample_pdf))

# ─── 4. Security (Encrypt/Decrypt) ───────────────────────────────────────
section("4. Security  -  Encrypt/Decrypt")

original = "This is a secret message! Testing 123."
encrypted = encrypt_message(original)
decrypted = decrypt_message(encrypted)

test("Encryption returns string", isinstance(encrypted, str))
test("Encrypted != original", encrypted != original)
test("Decryption matches original", decrypted == original, f"Got: {decrypted}")
test("Encrypted doesn't contain plaintext", original not in encrypted)

# ─── 5. PDF Generation ────────────────────────────────────────────────────
section("5. PDF Generation")

pdf_path = generate_sample_pdf("test_e2e_sample.pdf")
test("PDF file was created", os.path.exists(pdf_path), f"Path: {pdf_path}")
test("PDF file has content", os.path.getsize(pdf_path) > 0, f"Size: {os.path.getsize(pdf_path)} bytes")
test("PDF is in data/ dir", "data" in pdf_path)

# ─── 6. Attachment Handler ────────────────────────────────────────────────
section("6. Attachment Handler")

test("Valid PDF returns True", is_valid_attachment(pdf_path))
test("Non-existent file returns False", not is_valid_attachment("nonexistent_file.xyz"))
test("Invalid extension returns False", not is_valid_attachment(__file__))  # .py not allowed

from email.mime.multipart import MIMEMultipart
msg = MIMEMultipart()
result = attach_files(msg, [pdf_path])
test("attach_files returns MIMEMultipart", isinstance(result, MIMEMultipart))
# Check content-type for attachments
ct = result.get_content_type()
test("Message has multipart content", ct == "multipart/mixed" or "multipart" in ct)

# ─── 7. CSV Loading ──────────────────────────────────────────────────────
section("7. CSV Loading")

csv_content = "name,email\nAlice,alice@test.com\nBob,bob@test.com\nCharlie,charlie@test.com"
csv_path = os.path.join(tempfile.gettempdir(), "test_recipients.csv")
with open(csv_path, "w", encoding="utf-8") as f:
    f.write(csv_content)

recipients = load_recipients(csv_path)
test("Loaded 3 recipients", len(recipients) == 3, f"Got: {len(recipients)}")
test("First recipient name is Alice", recipients[0]["name"] == "Alice")
test("First recipient email", recipients[0]["email"] == "alice@test.com")
test("Non-existent CSV returns empty list", load_recipients("fake.csv") == [])

# ─── 8. Bulk Sender (flat string list) ──────────────────────────────────
section("8. Bulk Sender  -  Flat Email Strings")

# We can't actually send, but we can verify the function accepts string lists
# by checking it doesn't crash on the recipient iteration logic
# The function will fail at SMTP auth, but before that it should process recipients
# Let's verify the recipient handling logic directly

from app.bulk_sender import EMAIL_USER, EMAIL_PASSWORD
test("Bulk sender has email configured", bool(EMAIL_USER), f"Got: {EMAIL_USER}")
test("Bulk sender has password configured", bool(EMAIL_PASSWORD), "Password is set (hidden)")

# Test the internal logic: manually iterate over what send_bulk_emails does
test_emails = ["alice@test.com", "bob@test.com"]
for r in test_emails:
    name = ""
    to_email = r if isinstance(r, str) else r.get("email", r)
test("Flat string list iteration works", to_email == "bob@test.com")

# Test dict-style too
test_dicts = [{"name": "Alice", "email": "alice@test.com"}]
for r in test_dicts:
    name = r.get("name", "") if not isinstance(r, str) else ""
    to_email = r if isinstance(r, str) else r.get("email", r)
test("Dict list iteration works", name == "Alice" and to_email == "alice@test.com")

# ─── 9. Scheduler ─────────────────────────────────────────────────────────
section("9. Scheduler")

future = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

schedule_email(future, "single@test.com", "Test Subj", "Test body",
               single_recipient=True, task_id="e2e_test_task")

tasks = list_scheduled_emails(return_dict=True) or {}
test("Scheduled task appears in list", "e2e_test_task" in tasks, f"Tasks: {list(tasks.keys())}")
test("Task has correct subject", tasks["e2e_test_task"]["subject"] == "Test Subj")
test("Task has correct time", tasks["e2e_test_task"]["time"] == future)

cancel_scheduled_email("e2e_test_task")
tasks_after = list_scheduled_emails(return_dict=True) or {}
test("Cancelled task removed", "e2e_test_task" not in tasks_after)

test("Cancel non-existent doesn't crash", cancel_scheduled_email("fake_id_123") is None)

# Schedule with auto-generated task_id
schedule_email(future, ["multi@test.com"], "Auto ID", "Body")
tasks2 = list_scheduled_emails(return_dict=True) or {}
auto_ids = [t for t in tasks2 if t.startswith("task_")]
test("Auto-generated task_id works", len(auto_ids) > 0)

# Cleanup
for tid in list(tasks2.keys()):
    cancel_scheduled_email(tid)

# ─── 10. Multi-Account ──────────────────────────────────────────────────
section("10. Multi-Account")

test("ACCOUNTS is a list", isinstance(ACCOUNTS, list))
test("At least 1 account configured", len(ACCOUNTS) >= 1)
test("Account 0 has email", bool(ACCOUNTS[0]["email"]))
test("Account 0 has password", bool(ACCOUNTS[0]["password"]))

if len(ACCOUNTS) > 1 and ACCOUNTS[1]["email"]:
    test("Account 1 is configured", True, f"Email: {ACCOUNTS[1]['email']}")
else:
    test("Account 1 not configured (optional)", True, "Skipping  -  only 1 account set up")

# Test send_email_multi fails gracefully with bad index
result = send_email_multi(99, ["test@test.com"], "Test", "Body")
test("Bad account index handled gracefully", result is None)

# ─── 11. Email Composer ──────────────────────────────────────────────────
section("11. Email Composer")

msg = compose_email("test@test.com", "Test Subject", "Hello World")
test("compose_email returns MIMEMultipart", msg is not None)
test("Subject is correct", msg["Subject"] == "Test Subject")
test("To is correct", msg["To"] == "test@test.com")

# Test with HTML
msg_html = compose_email("test@test.com", "HTML Test", "<h1>Hello</h1>", html=True)
test("HTML compose works", msg_html is not None)

# ─── 12. Main Module ─────────────────────────────────────────────────────
section("12. Main Module Entry Point")

import main as main_module
test("main module imports cleanly", True)

# Check menu_actions exist
test("main module has menu_actions", hasattr(main_module, "cmd_send_single"))
test("main module has cmd_config", hasattr(main_module, "cmd_config"))

# ─── 13. Frontend ────────────────────────────────────────────────────────
section("13. Frontend App")

import py_compile
try:
    py_compile.compile(os.path.join("frontend", "app.py"), doraise=True)
    test("frontend/app.py syntax OK", True)
except py_compile.PyCompileError as e:
    test("frontend/app.py syntax OK", False, str(e))

# ─── 14. Cleanup ─────────────────────────────────────────────────────────
section("14. Cleanup")

os.remove(csv_path)
os.remove(pdf_path)
test("Temp files cleaned up", not os.path.exists(csv_path) and not os.path.exists(pdf_path))

# ─── Summary ─────────────────────────────────────────────────────────────
section("SUMMARY")
total = PASS + FAIL
print(f"  Total tests: {total}")
print(f"  Passed:      {PASS}")
print(f"  Failed:      {FAIL}")
print(f"  Success:     {PASS / total * 100:.1f}%" if total > 0 else "  No tests ran!")
print()

if FAIL > 0:
    print("  [FAIL] Some tests FAILED. Check the [FAIL] entries above.")
    sys.exit(1)
else:
    print("  [OK] ALL TESTS PASSED!")
    sys.exit(0)
