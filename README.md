# 🚀 Email Automator

> A Python-based email automation tool with CLI and web interface for sending, scheduling, and managing emails.

---

## 📌 Overview

Email Automator is a self-contained email automation system that lets you send single or bulk emails, schedule future deliveries, manage multiple accounts, auto-reply to inbox messages, and encrypt sensitive content — all from a terminal menu or a modern Streamlit web UI.

---

## ✨ Features

- Send Single / Bulk / HTML Emails
- CSV-Based Recipient Personalization (`{name}` placeholders)
- Email Scheduling with JSON Persistence
- Multi-Account Support (Up to 2 accounts)
- Auto-Reply via IMAP Inbox Checking
- Fernet Symmetric Encryption / Decryption
- PDF Generation for Testing Attachments
- File Attachment Validation (PDF, JPG, PNG, DOCX, XLSX)
- Light / Dark Theme Toggle
- Dashboard with Real-Time Metrics

---

## 🛠️ Tech Stack

### Frontend
- Streamlit
- HTML5 / CSS3
- JavaScript (via Streamlit)

### Backend
- Python 3.x
- smtplib (SMTP)
- imaplib (IMAP)

### Database / Storage
- JSON (Scheduled Tasks)
- File System (Encrypted Messages, PDFs, CSVs)

---

## 📂 Folder Structure

```bash
email-automator/
│
├── app/
│   ├── __init__.py
│   ├── smtp_client.py
│   ├── bulk_sender.py
│   ├── email_composer.py
│   ├── attachment_handler.py
│   ├── scheduler.py
│   ├── multi_account.py
│   ├── auto_reply.py
│   ├── security.py
│   ├── generate_pdf.py
│   └── config.py
│
├── frontend/
│   └── app.py
│
├── data/
│   ├── recipients.csv
│   ├── scheduled_tasks.json
│   ├── secret.key
│   └── demo_invoice.pdf
│
├── main.py
├── requirements.txt
├── setup_demo.py
├── test_e2e.py
├── test_env.py
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Installation Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sathvikagudise/email-automator.git
```

### 2️⃣ Navigate to Project Directory

```bash
cd email-automator
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

```bash
cp .env.example .env
# Edit .env with your email credentials
```

### 5️⃣ Run Demo Setup (Optional)

```bash
python setup_demo.py
```

### 6️⃣ Start the Application

**CLI Mode:**
```bash
python main.py
```

**Web Interface:**
```bash
streamlit run frontend/app.py
```

---

## 🌐 Environment Variables

Create a `.env` file in the root directory and add:

```env
EMAIL_USER_1=your_email@gmail.com
EMAIL_PASSWORD_1=your_app_password
EMAIL_USER_2=your_second_email@gmail.com
EMAIL_PASSWORD_2=your_second_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
IMAP_SERVER=imap.gmail.com
```

---

## 🧪 Testing

Run the full test suite:

```bash
python test_e2e.py
```

Verify environment configuration:

```bash
python test_env.py
```

---

## 🤝 Contributing

Contributions are welcome.

### Steps to Contribute

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Added new feature"
```

4. Push to GitHub

```bash
git push origin feature-name
```

5. Create a Pull Request

---

## 🔒 Security

- SMTP with TLS Encryption
- Fernet Symmetric Key Encryption
- App Passwords (no plain-text login)
- `.env` excluded from version control
- Attachment Type & Size Validation

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

### Gudise Sathvika

- GitHub: https://github.com/sathvikagudise
- LinkedIn: https://linkedin.com/in/sathvikayadav
- Email: sathvikayadav3@gmail.com

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub.
