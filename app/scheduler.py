import os
import json
import time
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.bulk_sender import send_bulk_emails
from app.smtp_client import send_email

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TASKS_FILE = os.path.join(DATA_DIR, "scheduled_tasks.json")

scheduled_tasks = {}
_task_counter = 0


def _save_tasks():
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(scheduled_tasks, f, indent=2)
    except Exception:
        pass


def _load_tasks():
    global scheduled_tasks
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                now = datetime.now()
                # Only keep future tasks
                valid = {}
                for tid, task in data.items():
                    try:
                        t = datetime.strptime(task["time"], "%Y-%m-%d %H:%M")
                        if t > now:
                            valid[tid] = task
                    except (ValueError, KeyError):
                        pass
                scheduled_tasks = valid
        except Exception:
            scheduled_tasks = {}


_load_tasks()


def _generate_task_id():
    global _task_counter
    _task_counter += 1
    return f"task_{_task_counter}_{datetime.now().strftime('%H%M%S')}"


def schedule_email(send_time, email_list, subject, body, attachments=None, task_id=None, single_recipient=False):
    try:
        send_time_obj = datetime.strptime(send_time, "%Y-%m-%d %H:%M")
        current_time = datetime.now()

        if send_time_obj < current_time:
            print("Error: Scheduled time is in the past!")
            return

        tid = task_id or _generate_task_id()

        if tid in scheduled_tasks:
            print(f"Warning: Task '{tid}' already scheduled!")
            return

        def job():
            print(f"Sending scheduled email: {subject}")
            if single_recipient:
                send_email(email_list, subject, body, attachments)
            else:
                recipients = email_list if isinstance(email_list, list) else [email_list]
                send_bulk_emails(recipients, subject, body, attachments)
            scheduled_tasks.pop(tid, None)

        delay = (send_time_obj - current_time).total_seconds()
        t = threading.Thread(target=lambda: (time.sleep(delay), job()), daemon=True)
        t.start()

        scheduled_tasks[tid] = {
            "time": send_time,
            "emails": email_list if isinstance(email_list, list) else [email_list],
            "subject": subject
        }
        _save_tasks()

        print(f"Email scheduled (Task ID: {tid}) for {send_time}")

    except ValueError as e:
        print(f"Invalid date format: {e}")


def list_scheduled_emails(return_dict=False):
    if not scheduled_tasks:
        print("No emails scheduled.")
        return {} if return_dict else None

    print("\nScheduled Emails:")
    for task_id, task in scheduled_tasks.items():
        print(f"  - [{task_id}] {task['time']} -> {len(task['emails'])} recipients | Subject: {task['subject']}")

    if return_dict:
        return scheduled_tasks


def cancel_scheduled_email(task_id):
    if task_id in scheduled_tasks:
        scheduled_tasks.pop(task_id)
        _save_tasks()
        print(f"Canceled scheduled email: {task_id}")
    else:
        print(f"Task ID {task_id} not found.")


def start_scheduler():
    t = threading.Thread(target=_scheduler_loop, daemon=True)
    t.start()
    return t

def _scheduler_loop():
    while True:
        time.sleep(60)


_scheduler_thread = None

if __name__ == "__main__":
    list_scheduled_emails()

    future_time = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")
    schedule_email(
        send_time=future_time,
        email_list=["test@example.com"],
        subject="Scheduled Email Test",
        body="This is a test email sent using the scheduler."
    )
