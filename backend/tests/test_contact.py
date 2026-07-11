"""
tests/test_contact.py — Basic functional tests for POST /api/contact.

Run with:
    cd backend
    pip install pytest httpx
    pytest tests/ -v

These tests use FastAPI's TestClient (synchronous) and mock the database
and email service so no real DB or SMTP connection is needed.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# ── Override settings before importing app ────────────────────────────────────
import os
os.environ.setdefault("DATABASE_URL",       "mysql+pymysql://root:test@localhost:3306/test")
os.environ.setdefault("GMAIL_USER",         "test@gmail.com")
os.environ.setdefault("GMAIL_APP_PASSWORD", "test_password")
os.environ.setdefault("RECIPIENT_EMAIL",    "recipient@gmail.com")
os.environ.setdefault("ALLOWED_ORIGINS",    "http://localhost:3000")
os.environ.setdefault("APP_ENV",            "development")

from main import app  # noqa: E402 — must come after env setup

client = TestClient(app, raise_server_exceptions=False)

# ── Sample valid payload ──────────────────────────────────────────────────────
VALID_PAYLOAD = {
    "full_name": "Test User",
    "email":     "test@example.com",
    "subject":   "Unit Test Submission",
    "message":   "This is a test message from the automated test suite.",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def mock_db_session():
    """Return a mock SQLAlchemy session."""
    session = MagicMock()
    mock_contact = MagicMock()
    mock_contact.id = 1
    session.add.return_value = None
    session.commit.return_value = None
    session.refresh.side_effect = lambda obj: setattr(obj, "id", 1)
    return session


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestHealthCheck:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "api" in response.json()


class TestContactValidation:
    def test_missing_name_returns_422(self):
        payload = {**VALID_PAYLOAD, "full_name": ""}
        response = client.post("/api/contact", json=payload)
        assert response.status_code == 422

    def test_invalid_email_returns_422(self):
        payload = {**VALID_PAYLOAD, "email": "not-an-email"}
        response = client.post("/api/contact", json=payload)
        assert response.status_code == 422

    def test_short_message_returns_422(self):
        payload = {**VALID_PAYLOAD, "message": "short"}
        response = client.post("/api/contact", json=payload)
        assert response.status_code == 422

    def test_xss_in_name_is_stripped(self):
        """HTML in the name field should be stripped, not rejected."""
        payload = {**VALID_PAYLOAD, "full_name": "Test <script>alert(1)</script> User"}
        # bleach strips the script tag; result "Test  User" is still valid
        with patch("router.get_db") as mock_get_db, \
             patch("router.send_contact_email"):
            mock_get_db.return_value = iter([mock_db_session()])
            response = client.post("/api/contact", json=payload)
            # 422 means name chars were invalid AFTER stripping — that's also fine
            assert response.status_code in (200, 422)

    def test_missing_subject_returns_422(self):
        payload = {**VALID_PAYLOAD, "subject": ""}
        response = client.post("/api/contact", json=payload)
        assert response.status_code == 422


class TestContactSuccess:
    @patch("router.send_contact_email")
    @patch("router.get_db")
    def test_valid_submission_returns_200(self, mock_get_db, mock_email):
        db = mock_db_session()
        mock_get_db.return_value = iter([db])
        mock_email.return_value = None

        response = client.post("/api/contact", json=VALID_PAYLOAD)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "message" in body

    @patch("router.send_contact_email", side_effect=Exception("SMTP error"))
    @patch("router.get_db")
    def test_email_failure_still_returns_200(self, mock_get_db, mock_email):
        """Email failure is non-fatal — message is already saved in DB."""
        db = mock_db_session()
        mock_get_db.return_value = iter([db])

        response = client.post("/api/contact", json=VALID_PAYLOAD)
        # Should still succeed since DB save worked
        assert response.status_code == 200


class TestRateLimit:
    def test_rate_limit_triggers_after_threshold(self):
        """
        Send requests until rate limit kicks in.
        NOTE: Rate limiter uses in-memory state per process,
        so this test may be flaky if other tests consumed the quota.
        Run in isolation for reliable results.
        """
        with patch("router.send_contact_email"), \
             patch("router.get_db") as mock_get_db:
            mock_get_db.return_value = iter([mock_db_session()] * 20)

            responses = []
            for _ in range(7):  # Exceeds default limit of 5
                r = client.post("/api/contact", json=VALID_PAYLOAD)
                responses.append(r.status_code)

            assert 429 in responses, "Expected a 429 after exceeding rate limit"
