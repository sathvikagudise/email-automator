import os
import sys
import tempfile
from datetime import datetime, timedelta

import streamlit as st

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.smtp_client import send_email
from app.bulk_sender import send_bulk_emails, load_recipients
from app.scheduler import schedule_email, list_scheduled_emails, cancel_scheduled_email
from app.security import encrypt_message, decrypt_message
from app.multi_account import send_email_multi, ACCOUNTS
from app.auto_reply import check_inbox
from app.generate_pdf import generate_sample_pdf
from app.config import EMAIL_ADDRESS, SMTP_SERVER, SMTP_PORT, ALLOWED_EXTENSIONS

st.set_page_config(page_title="Automatic Email Generator", page_icon="📧", layout="wide", initial_sidebar_state="expanded")

# ─── Theme Toggle ────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ─── Theme CSS ───────────────────────────────────────────────────────────
LIGHT_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
    .block-container { padding: 1rem 2rem !important; max-width: 1200px !important; margin: 0 auto !important; }
    footer { display: none !important; }

    div[data-testid="stSidebar"] { background: #f5efe6 !important; border-right: 2px solid #d4c8b5 !important; min-width: 250px !important; }
    div[data-testid="stSidebar"] h1 { color: #2a1a0a !important; font-size: 1.2rem !important; font-weight: 700 !important; }
    div[data-testid="stSidebar"] p { font-size: 0.85rem !important; color: #3a2a1a !important; font-weight: 500 !important; }
    div[data-testid="stSidebar"] .st-emotion-cache-1v7f65g { font-size: 0.9rem !important; color: #2a1a0a !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] .stRadio label { font-size: 0.9rem !important; padding: 0.4rem 0.6rem !important; border-radius: 6px !important; color: #2a1a0a !important; font-weight: 500 !important; }
    section[data-testid="stSidebar"] .stRadio label:hover { background: #e0d5c1 !important; }
    section[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p { font-size: 0.9rem !important; color: #2a1a0a !important; font-weight: 500 !important; }
    section[data-testid="stSidebar"] .st-bq { color: #2a1a0a !important; }
    section[data-testid="stSidebar"] .st-emotion-cache-1v7f65g p { font-size: 0.9rem !important; color: #2a1a0a !important; font-weight: 500 !important; }

    .card { background: #fdfaf5 !important; border: 1px solid #e0d5c1 !important; border-radius: 8px !important; padding: 1.2rem !important; margin-bottom: 0.8rem !important; }
    .card h3 { font-size: 1rem !important; font-weight: 600 !important; margin-bottom: 0.5rem !important; color: #4a3728 !important; }
    .card p, .card li { font-size: 0.85rem !important; color: #5a4a3a !important; }
    .card ol { padding-left: 1.2rem !important; }
    .card ol li { margin-bottom: 0.3rem !important; }

    h1 { font-size: 1.5rem !important; font-weight: 700 !important; margin-bottom: 0.3rem !important; color: #3a2a1a !important; }
    h2 { font-size: 1.2rem !important; font-weight: 600 !important; margin-bottom: 0.3rem !important; color: #4a3728 !important; }

    div.stButton > button { font-size: 0.85rem !important; font-weight: 500 !important; padding: 0.4rem 1rem !important; border-radius: 6px !important; }
    div.stButton > button[kind="primary"] { background: #4a6cf7 !important; color: white !important; border: none !important; }
    div.stButton > button[kind="primary"]:hover { background: #5b7df8 !important; }

    .stTextInput input, .stTextArea textarea, .stSelectbox, .stDateInput input, .stTimeInput input { font-size: 0.85rem !important; border-radius: 6px !important; background: #fdfaf5 !important; display: block !important; width: 100% !important; }

    /* File Uploader Master Fix */
    div[data-testid="stFileUploader"] { font-size: 0.85rem !important; margin-bottom: 2rem !important; display: block !important; clear: both !important; }
    div[data-testid="stFileUploader"] section { padding: 1.2rem !important; border: 1px dashed #c4b5a0 !important; border-radius: 6px !important; background: #fdfaf5 !important; margin-bottom: 1rem !important; display: block !important; clear: both !important; position: relative !important; overflow: visible !important; }
    div[data-testid="stFileUploader"] button { font-size: 0.8rem !important; padding: 0.5rem 1rem !important; background: #f0e8dc !important; color: #4a3728 !important; border: 1px solid #d4c8b5 !important; border-radius: 4px !important; margin-right: 0.8rem !important; margin-bottom: 1rem !important; display: inline-block !important; position: relative !important; }
    div[data-testid="stFileUploader"] button:hover { background: #e5dac8 !important; }
    div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] { font-size: 0.8rem !important; color: #6b5a4a !important; margin-bottom: 0.8rem !important; display: block !important; }
    div[data-testid="stFileUploader"] ul, div[data-testid="stFileUploader"] li { margin-bottom: 0.5rem !important; }
    .stForm > button { margin-top: 1rem !important; }

    div[data-testid="stMetric"] { background: #fdfaf5 !important; border: 1px solid #e0d5c1 !important; border-radius: 8px !important; padding: 0.8rem !important; }
    div[data-testid="stMetric"] label { font-size: 0.75rem !important; color: #6b5a4a !important; }
    div[data-testid="stMetric"] div { font-size: 1.1rem !important; font-weight: 600 !important; color: #3a2a1a !important; }

    .stAlert { font-size: 0.85rem !important; border-radius: 6px !important; }
    div[data-testid="stDataFrame"] { font-size: 0.8rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 0 !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem !important; padding: 0.4rem 1rem !important; }
    .st-emotion-cache-1n76uvr, .st-emotion-cache-1wivap2, .st-emotion-cache-1aezh81, .st-emotion-cache-10trblm, .st-bq { font-size: 0.85rem !important; }
</style>
"""

DARK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
    .block-container { padding: 1rem 2rem !important; max-width: 1200px !important; margin: 0 auto !important; }
    footer { display: none !important; }

    div[data-testid="stSidebar"] { background: #1a1a2e !important; border-right: 2px solid #2a2a4a !important; min-width: 250px !important; }
    div[data-testid="stSidebar"] h1 { color: #ffffff !important; font-size: 1.2rem !important; font-weight: 700 !important; }
    div[data-testid="stSidebar"] p { font-size: 0.85rem !important; color: #d0d0e0 !important; font-weight: 500 !important; }
    div[data-testid="stSidebar"] .st-emotion-cache-1v7f65g { font-size: 0.9rem !important; color: #ffffff !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] .stRadio label { font-size: 0.9rem !important; padding: 0.4rem 0.6rem !important; border-radius: 6px !important; color: #d0d0e0 !important; font-weight: 500 !important; }
    section[data-testid="stSidebar"] .stRadio label:hover { background: #2a2a4a !important; }
    section[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p { font-size: 0.9rem !important; color: #d0d0e0 !important; font-weight: 500 !important; }
    section[data-testid="stSidebar"] .st-bq { color: #d0d0e0 !important; }
    section[data-testid="stSidebar"] .st-emotion-cache-1v7f65g p { font-size: 0.9rem !important; color: #d0d0e0 !important; font-weight: 500 !important; }

    .card { background: #1e1e36 !important; border: 1px solid #2d2d50 !important; border-radius: 8px !important; padding: 1.2rem !important; margin-bottom: 0.8rem !important; }
    .card h3 { font-size: 1rem !important; font-weight: 600 !important; margin-bottom: 0.5rem !important; color: #e0e0e0 !important; }
    .card p, .card li { font-size: 0.85rem !important; color: #ccc !important; }
    .card ol { padding-left: 1.2rem !important; }
    .card ol li { margin-bottom: 0.3rem !important; }

    h1 { font-size: 1.5rem !important; font-weight: 700 !important; margin-bottom: 0.3rem !important; color: #f0f0f0 !important; }
    h2 { font-size: 1.2rem !important; font-weight: 600 !important; margin-bottom: 0.3rem !important; color: #e0e0e0 !important; }

    div.stButton > button { font-size: 0.85rem !important; font-weight: 500 !important; padding: 0.4rem 1rem !important; border-radius: 6px !important; }
    div.stButton > button[kind="primary"] { background: #4a6cf7 !important; color: white !important; border: none !important; }
    div.stButton > button[kind="primary"]:hover { background: #5b7df8 !important; }

    .stTextInput input, .stTextArea textarea, .stSelectbox, .stDateInput input, .stTimeInput input { font-size: 0.85rem !important; border-radius: 6px !important; display: block !important; width: 100% !important; }

    /* File Uploader Master Fix */
    div[data-testid="stFileUploader"] { font-size: 0.85rem !important; margin-bottom: 2rem !important; display: block !important; clear: both !important; }
    div[data-testid="stFileUploader"] section { padding: 1.2rem !important; border: 1px dashed #4a4a6a !important; border-radius: 6px !important; margin-bottom: 1rem !important; display: block !important; clear: both !important; position: relative !important; overflow: visible !important; }
    div[data-testid="stFileUploader"] button { font-size: 0.8rem !important; padding: 0.5rem 1rem !important; border-radius: 4px !important; margin-right: 0.8rem !important; margin-bottom: 1rem !important; display: inline-block !important; position: relative !important; }
    div[data-testid="stFileUploader"] button:hover { opacity: 0.9 !important; }
    div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] { font-size: 0.8rem !important; margin-bottom: 0.8rem !important; display: block !important; }
    div[data-testid="stFileUploader"] ul, div[data-testid="stFileUploader"] li { margin-bottom: 0.5rem !important; }
    .stForm > button { margin-top: 1rem !important; }

    div[data-testid="stMetric"] { background: #1e1e36 !important; border: 1px solid #2d2d50 !important; border-radius: 8px !important; padding: 0.8rem !important; }
    div[data-testid="stMetric"] label { font-size: 0.75rem !important; color: #aaa !important; }
    div[data-testid="stMetric"] div { font-size: 1.1rem !important; font-weight: 600 !important; }

    .stAlert { font-size: 0.85rem !important; border-radius: 6px !important; }
    div[data-testid="stDataFrame"] { font-size: 0.8rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 0 !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem !important; padding: 0.4rem 1rem !important; }
    .st-emotion-cache-1n76uvr, .st-emotion-cache-1wivap2, .st-emotion-cache-1aezh81, .st-emotion-cache-10trblm, .st-bq { font-size: 0.85rem !important; }
</style>
"""

st.markdown(LIGHT_CSS if st.session_state.theme == "light" else DARK_CSS, unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────

st.sidebar.title("Email Generator")
st.sidebar.markdown(f"**Account:** {EMAIL_ADDRESS or 'Not set'}")
st.sidebar.markdown(f"**Server:** {SMTP_SERVER}:{SMTP_PORT}")

st.sidebar.divider()

page = st.sidebar.radio("Navigate", [
    "Dashboard",
    "Send Email",
    "Send Bulk Emails",
    "Schedule Email",
    "View Scheduled",
    "Multi-Account",
    "Encrypt / Decrypt",
    "Auto-Reply",
    "Utilities",
])

st.sidebar.divider()

# Theme toggle
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Light" if st.session_state.theme == "dark" else "Light",
                 use_container_width=True, disabled=st.session_state.theme == "light"):
        st.session_state.theme = "light"
        st.rerun()
with col2:
    if st.button("Dark" if st.session_state.theme == "light" else "Dark",
                 use_container_width=True, disabled=st.session_state.theme == "dark"):
        st.session_state.theme = "dark"
        st.rerun()

st.sidebar.caption("v2.0")


# ─── Helper ────────────────────────────────────────────────────────────────

def save_attachments(uploaded_files):
    paths = []
    if uploaded_files:
        for f in uploaded_files:
            tmp = os.path.join(tempfile.gettempdir(), f.name)
            with open(tmp, "wb") as out:
                out.write(f.getbuffer())
            paths.append(tmp)
    return paths or None


# ─── Dashboard ─────────────────────────────────────────────────────────────

if page == "Dashboard":
    st.title("Dashboard")
    st.markdown("Overview of your email system configuration and status.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Email Account", EMAIL_ADDRESS or "Not configured")
    with col2:
        st.metric("SMTP Server", f"{SMTP_SERVER}:{SMTP_PORT}")
    with col3:
        st.metric("Active Accounts", sum(1 for a in ACCOUNTS if a["email"]))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Attachment Settings**")
        st.markdown(f"Allowed: `{', '.join(sorted(ALLOWED_EXTENSIONS))}`  \nMax size: 5 MB")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Scheduled Emails**")
        tasks = list_scheduled_emails(return_dict=True) or {}
        if tasks:
            for tid, task in tasks.items():
                st.markdown(f"`{tid}` -- {task['time']} ({len(task['emails'])} recipients)")
        else:
            st.markdown("No emails scheduled.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <h3>Quick Start</h3>
    <ol>
        <li><b>Send Email</b> -- Compose and send a single email with optional attachments</li>
        <li><b>Send Bulk</b> -- Send to multiple recipients via CSV or manual entry</li>
        <li><b>Schedule</b> -- Set a date/time for automatic delivery</li>
        <li><b>Multi-Account</b> -- Switch between configured email accounts</li>
        <li><b>Auto-Reply</b> -- Check inbox and send automatic replies</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)


# ─── Send Email ────────────────────────────────────────────────────────────

elif page == "Send Email":
    st.title("Send Email")
    st.markdown("Compose and send a single email.")

    with st.form("send_form"):
        recipient = st.text_input("Recipient Email")
        subject = st.text_input("Subject")
        use_html = st.checkbox("Send as HTML")
        body = st.text_area("Body", height=250,
                            help="Write your message here. If HTML is checked, use raw HTML.")
        attach_files = st.file_uploader("Attachments", accept_multiple_files=True, key="send_attach")

        submitted = st.form_submit_button("Send Email", use_container_width=True, type="primary")

    if submitted:
        if not recipient or not subject or not body:
            st.error("Please fill in recipient, subject, and body.")
        else:
            with st.spinner("Sending..."):
                send_email(recipient, subject, body, save_attachments(attach_files), html=use_html)
            st.success(f"Email sent to **{recipient}**!")


# ─── Send Bulk ─────────────────────────────────────────────────────────────

elif page == "Send Bulk Emails":
    st.title("Send Bulk Emails")
    st.markdown("Send emails to multiple recipients using a CSV file or manual entry.")

    mode = st.radio("Input mode", ["Manual Entry", "Upload CSV"], horizontal=True)

    if mode == "Upload CSV":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**CSV format:** `name,email` (one per line, header row optional)")
        csv_file = st.file_uploader("Choose CSV file", type="csv", key="bulk_csv_file")
        st.markdown("</div>", unsafe_allow_html=True)

        recipients = []
        if csv_file:
            tmp_path = os.path.join(tempfile.gettempdir(), "uploaded_recipients.csv")
            with open(tmp_path, "wb") as f:
                f.write(csv_file.getbuffer())
            recipients = load_recipients(tmp_path)
            if recipients:
                st.info(f"Loaded {len(recipients)} recipients")
                st.dataframe({"Name": [r["name"] for r in recipients],
                              "Email": [r["email"] for r in recipients]})
            else:
                st.warning("No recipients found in file.")

        with st.form("bulk_csv_form"):
            subject = st.text_input("Subject")
            use_html = st.checkbox("Send as HTML")
            body = st.text_area("Body", height=200,
                                help="Use {name} for personalization")
            attach_files = st.file_uploader("Attachment Files", accept_multiple_files=True, key="bulk_csv_attach")
            submitted = st.form_submit_button("Send Bulk Emails", use_container_width=True, type="primary")

        if submitted and recipients:
            with st.spinner(f"Sending to {len(recipients)} recipients..."):
                send_bulk_emails(recipients, subject, body, save_attachments(attach_files), html=use_html)
            st.success(f"Bulk emails sent to {len(recipients)} recipients!")
    else:
        with st.form("bulk_manual_form"):
            emails_input = st.text_area("Recipient Emails (one per line)", height=120)
            subject = st.text_input("Subject")
            use_html = st.checkbox("Send as HTML")
            body = st.text_area("Body", height=200,
                                help="Use {name} for personalization (name will be empty)")
            attach_files = st.file_uploader("Attachment Files", accept_multiple_files=True, key="bulk_manual_attach")
            submitted = st.form_submit_button("Send Bulk Emails", use_container_width=True, type="primary")

        if submitted:
            emails = [e.strip() for e in emails_input.split("\n") if e.strip()]
            if not emails:
                st.error("Enter at least one recipient email.")
            elif not subject or not body:
                st.error("Please fill in subject and body.")
            else:
                with st.spinner(f"Sending to {len(emails)} recipients..."):
                    send_bulk_emails(emails, subject, body, save_attachments(attach_files), html=use_html)
                st.success(f"Bulk emails sent to {len(emails)} recipients!")


# ─── Schedule ──────────────────────────────────────────────────────────────

elif page == "Schedule Email":
    st.title("Schedule Email")
    st.markdown("Set a specific date and time for your email to be sent automatically.")

    with st.form("schedule_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", min_value=datetime.today())
        with col2:
            time = st.time_input("Time")

        st.markdown("**Recipients**")
        emails_input = st.text_area("Recipient Emails (one per line or comma-separated)", height=100)
        subject = st.text_input("Subject")
        use_html = st.checkbox("Send as HTML")
        body = st.text_area("Body", height=200)
        attach_files = st.file_uploader("Attachment Files", accept_multiple_files=True, key="schedule_attach")

        submitted = st.form_submit_button("Schedule Email", use_container_width=True, type="primary")

    if submitted:
        dt = datetime.combine(date, time)
        if dt <= datetime.now():
            st.error("Scheduled time must be in the future!")
        else:
            send_time = dt.strftime("%Y-%m-%d %H:%M")
            emails = [e.strip() for e in emails_input.replace(",", "\n").split("\n") if e.strip()]
            if not emails:
                st.error("Enter at least one recipient.")
            else:
                with st.spinner("Scheduling..."):
                    schedule_email(send_time, emails, subject, body,
                                   save_attachments(attach_files), single_recipient=len(emails) == 1)
                st.success(f"Email scheduled for **{send_time}**!")


# ─── View Scheduled ────────────────────────────────────────────────────────

elif page == "View Scheduled":
    st.title("Scheduled Emails")
    st.markdown("View and cancel your scheduled emails.")

    tasks = list_scheduled_emails(return_dict=True) or {}
    if not tasks:
        st.info("No emails currently scheduled.")
    else:
        for tid, task in tasks.items():
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                cols = st.columns([3, 2, 2, 1])
                cols[0].markdown(f"**Task:** `{tid}`")
                cols[1].write(task["time"])
                cols[2].write(f"{len(task['emails'])} recipient(s)")
                if cols[3].button("Cancel", key=f"cancel_{tid}"):
                    cancel_scheduled_email(tid)
                    st.rerun()
                cols[0].write(f"**Subject:** {task['subject']}")
                st.markdown("</div>", unsafe_allow_html=True)


# ─── Multi-Account ─────────────────────────────────────────────────────────

elif page == "Multi-Account":
    st.title("Multi-Account")
    st.markdown("Send emails using different configured accounts.")

    active_accounts = [(i, a) for i, a in enumerate(ACCOUNTS) if a["email"]]
    if not active_accounts:
        st.warning("No email accounts configured. Add them to your `.env` file.")
    else:
        account_labels = [f"[{i}] {a['email']}" for i, a in active_accounts]
        selected = st.selectbox("Select sender account", account_labels)
        idx = int(selected.split("]")[0].strip("["))
        sender_email = ACCOUNTS[idx]["email"]
        st.info(f"Sending as: **{sender_email}**")

        with st.form("multi_form"):
            col1, col2 = st.columns(2)
            with col1:
                emails_input = st.text_area("Recipient emails (one per line)", height=100)
            with col2:
                subject = st.text_input("Subject")
            body = st.text_area("Body", height=200)
            use_html = st.checkbox("Send as HTML")
            submitted = st.form_submit_button("Send", use_container_width=True, type="primary")

        if submitted:
            recipients = [e.strip() for e in emails_input.split("\n") if e.strip()]
            if recipients:
                with st.spinner(f"Sending from {sender_email}..."):
                    send_email_multi(idx, recipients, subject, body, html=use_html)
                st.success(f"Sent to {len(recipients)} recipient(s) from {sender_email}!")
            else:
                st.error("Enter at least one recipient.")


# ─── Encrypt / Decrypt ─────────────────────────────────────────────────────

elif page == "Encrypt / Decrypt":
    st.title("Encrypt / Decrypt")
    st.markdown("Securely encrypt and decrypt messages using Fernet symmetric encryption.")

    tab1, tab2 = st.tabs(["Encrypt", "Decrypt"])

    with tab1:
        with st.form("encrypt_form"):
            msg = st.text_area("Message to encrypt", height=150)
            submitted = st.form_submit_button("Encrypt", use_container_width=True, type="primary")
        if submitted and msg:
            enc = encrypt_message(msg)
            st.success("Encrypted successfully!")
            st.code(enc, language="text")
            st.download_button("Download encrypted text", enc, file_name="encrypted.txt")

    with tab2:
        with st.form("decrypt_form"):
            enc_input = st.text_area("Encrypted message to decrypt", height=150)
            submitted = st.form_submit_button("Decrypt", use_container_width=True, type="primary")
        if submitted and enc_input:
            try:
                dec = decrypt_message(enc_input)
                st.success("Decrypted successfully!")
                st.code(dec, language="text")
            except Exception as e:
                st.error(f"Decryption failed: {e}")


# ─── Auto-Reply ────────────────────────────────────────────────────────────

elif page == "Auto-Reply":
    st.title("Auto-Reply")
    st.markdown("Check your inbox for unread emails and send automatic replies.")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**How it works:** Connects to your IMAP inbox, finds unread emails, and sends an automatic reply to each one.")
    st.markdown("Unread emails will be marked as seen after replying.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Check Inbox & Send Replies", type="primary", use_container_width=True):
        with st.spinner("Checking inbox..."):
            check_inbox()
        st.success("Auto-reply check complete!")


# ─── Utilities ─────────────────────────────────────────────────────────────

elif page == "Utilities":
    st.title("Utilities")
    st.markdown("Additional tools and utilities.")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Generate Sample PDF**")
    st.markdown("Generate a sample PDF file for testing attachments.")
    pdf_name = st.text_input("Filename", value="sample.pdf")
    if st.button("Generate PDF", key="gen_pdf"):
        path = generate_sample_pdf(pdf_name)
        st.success(f"PDF generated: `{path}`")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Load Recipients from CSV**")
    csv_file = st.file_uploader("Upload CSV to preview", type="csv", key="util_csv")
    if csv_file:
        tmp = os.path.join(tempfile.gettempdir(), "util_recipients.csv")
        with open(tmp, "wb") as f:
            f.write(csv_file.getbuffer())
        recipients = load_recipients(tmp)
        if recipients:
            st.dataframe(recipients)
            st.info(f"Total: {len(recipients)} recipients")
        else:
            st.warning("No recipients found.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Configuration**")
    config_data = {
        "Email Address": EMAIL_ADDRESS or "Not set",
        "SMTP Server": f"{SMTP_SERVER}:{SMTP_PORT}",
        "Allowed Extensions": ", ".join(sorted(ALLOWED_EXTENSIONS)),
        "Max Attachment Size": "5 MB",
    }
    for k, v in config_data.items():
        st.markdown(f"**{k}:** {v}")
    st.markdown("</div>", unsafe_allow_html=True)
