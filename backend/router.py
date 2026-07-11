"""
router.py — POST /api/contact endpoint.

Request lifecycle:
  1. Rate limit check       (IP-based, 5 req/min)
  2. Input validation       (Pydantic schema — 422 on failure)
  3. Input sanitization     (bleach — applied inside schema validators)
  4. Save to MySQL          (SQLAlchemy ORM — parameterized, SQL-injection-safe)
  5. Send Gmail email       (async via thread pool — does NOT block response)
  6. Return JSON response   (200 success | 500 if DB fails)
"""

import asyncio
from datetime import datetime, timezone
from functools import partial

from fastapi import APIRouter, Depends, Request, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from config import get_settings
from database import get_db
from models import ContactMessage
from schemas import ContactRequest, ContactResponse, ErrorResponse
from rate_limiter import check_rate_limit
from email_service import send_contact_email
from logger import get_logger

log = get_logger(__name__)
settings = get_settings()

router = APIRouter()


def _get_client_ip(request: Request) -> str:
    """Extract real client IP respecting X-Forwarded-For proxy header."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _get_user_agent(request: Request) -> str:
    """Return User-Agent header, truncated to 500 chars."""
    ua = request.headers.get("User-Agent", "")
    return ua[:500]


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Submit a contact form message",
    description=(
        "Accepts a contact form submission, saves it to MySQL, "
        "and sends an email notification to the business owner."
    ),
)
async def submit_contact(
    payload: ContactRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _rate: None = Depends(check_rate_limit),  # Raises 429 if limit exceeded
) -> ContactResponse:
    """
    Main contact form submission handler.
    """
    ip_address = _get_client_ip(request)
    user_agent = _get_user_agent(request)
    submitted_at = datetime.now(timezone.utc).replace(tzinfo=None)

    log.info(
        "Contact form received | name=%s | email=%s | ip=%s",
        payload.full_name, payload.email, ip_address,
    )

    # ── 1. Persist to database ────────────────────────────────────────────
    try:
        contact = ContactMessage(
            full_name  = payload.full_name,
            email      = payload.email,
            subject    = payload.subject,
            message    = payload.message,
            ip_address = ip_address,
            user_agent = user_agent,
            created_at = submitted_at,
            status     = "new",
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        log.info("Saved to database | id=%d", contact.id)

    except Exception as exc:
        db.rollback()
        log.error("Database error | %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save your message. Please try again.",
        )

    # ── 2. Send email in background (does NOT block response) ─────────────
    # If SMTP fails or times out, the message is already saved in the database
    # and the visitor receives an instant success confirmation.
    background_tasks.add_task(
        send_contact_email,
        full_name    = payload.full_name,
        email        = payload.email,
        subject      = payload.subject,
        message      = payload.message,
        ip_address   = ip_address,
        submitted_at = submitted_at,
    )

    # ── 3. Return success ─────────────────────────────────────────────────
    return ContactResponse(
        success=True,
        message="Thank you! Your message has been received. We'll get back to you within 24 hours.",
        id=contact.id,
    )
