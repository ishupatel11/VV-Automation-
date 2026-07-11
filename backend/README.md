# V.V. Automation — Contact System API

## Overview

Production-ready FastAPI backend for the V.V. Automation contact form.  
Every submission is **saved to MySQL** and **emailed to your Gmail** automatically.

---

## Folder Structure

```
backend/
├── main.py              ← FastAPI app (CORS, health check, router)
├── config.py            ← Settings loaded from .env
├── database.py          ← SQLAlchemy engine + session
├── models.py            ← ContactMessage ORM model
├── schemas.py           ← Pydantic validation + bleach sanitization
├── router.py            ← POST /api/contact endpoint
├── email_service.py     ← Gmail SMTP HTML email sender
├── rate_limiter.py      ← IP-based sliding window rate limiter
├── logger.py            ← Structured logging
├── requirements.txt     ← Python dependencies
├── .env.example         ← Environment variable template
├── .gitignore           ← Excludes .env and __pycache__
├── schema.sql           ← MySQL table DDL
├── Procfile             ← Railway/Render deployment command
└── tests/
    └── test_contact.py  ← Pytest test suite
```

---

## API Reference

### `POST /api/contact`

Submit a contact form message.

**Request Body (JSON)**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "subject": "Machine Inquiry",
  "message": "I would like to know more about your CNC machines."
}
```

**Success Response (200)**
```json
{
  "success": true,
  "message": "Thank you! Your message has been received. We'll get back to you within 24 hours.",
  "id": 42
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 422 | Validation failed (missing/invalid fields) |
| 429 | Rate limit exceeded (5 requests/minute per IP) |
| 500 | Server error (DB or SMTP failure) |

### `GET /health`

Health probe for uptime monitors.

```json
{ "status": "ok", "service": "VV Automation Contact API", "version": "1.0.0" }
```

### `GET /docs`

Interactive Swagger UI (available in development mode only).

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- MySQL 8.0+ (local install or Docker)
- Gmail account with 2-Step Verification enabled

### Step 1 — Set up environment

```bash
cd "Yagnik 2/backend"
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Step 2 — Configure `.env`

Open `.env` and fill in your values:

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/vv_automation
GMAIL_USER=your_gmail@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
RECIPIENT_EMAIL=your_gmail@gmail.com
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
APP_ENV=development
```

> **Gmail App Password**: Go to myaccount.google.com/apppasswords
> Select Mail → Other (custom name) → type "VV Automation" → Generate

### Step 3 — Create the MySQL database

```bash
mysql -u root -p < schema.sql
```

### Step 4 — Run the backend

```bash
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000/docs to test interactively.

### Step 5 — Test the contact form

Open http://localhost:3000/contact.html — the form will POST to http://localhost:8000/api/contact.

---

## Production Deployment

### Railway (Recommended)

#### 1. Deploy MySQL on Railway

1. Go to railway.app → New Project → Provision MySQL
2. Copy the MYSQL_URL from Variables tab
3. Convert to: mysql+pymysql://root:password@host:PORT/railway
4. Run schema: mysql -h HOST -P PORT -u root -p railway < schema.sql

#### 2. Deploy FastAPI on Railway

1. New Service → GitHub Repo → select your repo
2. Set Root Directory to: backend
3. Railway auto-detects the Procfile
4. Add all Variables from your .env:
   - DATABASE_URL, GMAIL_USER, GMAIL_APP_PASSWORD
   - RECIPIENT_EMAIL, ALLOWED_ORIGINS, APP_ENV=production
5. Deploy → get URL like: https://vv-contact-api.railway.app

#### 3. Update contact.html

Find this line in contact.html (~line 233):
  : 'https://YOUR_API_URL.railway.app';

Replace with your Railway URL:
  : 'https://vv-contact-api.railway.app';

---

### Deploy the Frontend

#### Netlify
1. Drag and drop the Yagnik 2 folder to app.netlify.com
2. Add your Netlify URL to Railway's ALLOWED_ORIGINS variable
3. Custom domain: Domain settings → Add your domain

#### Vercel
1. Push to GitHub → Import at vercel.com
2. No framework preset (static site)

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pip install pytest httpx
pytest tests/ -v
```

---

## Security Checklist

- SQL injection — SQLAlchemy ORM parameterized queries
- XSS — bleach.clean() on all user inputs
- Spam — IP-based rate limiting (5/min)
- CORS — Whitelist-only frontend origins
- Credentials — .env excluded from Git
- Email header injection — Pydantic EmailStr validation
- Large payloads — Max lengths enforced on all fields
- Proxy-aware IP detection — X-Forwarded-For header support

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| DATABASE_URL | YES | MySQL connection string |
| GMAIL_USER | YES | Gmail address to send from |
| GMAIL_APP_PASSWORD | YES | Gmail App Password |
| RECIPIENT_EMAIL | YES | Email address to receive notifications |
| ALLOWED_ORIGINS | YES | Comma-separated frontend URLs |
| RATE_LIMIT_PER_MINUTE | NO | Requests per IP per minute (default: 5) |
| APP_ENV | NO | development or production (default: development) |
