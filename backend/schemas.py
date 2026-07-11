"""
schemas.py — Pydantic request and response schemas with input sanitization.

Security measures applied to every field:
  • bleach.clean() strips ALL HTML tags (XSS protection)
  • Length limits enforced (large payload protection)
  • Email validated with pydantic's EmailStr (RFC 5322)
  • Name restricted to letters, spaces, hyphens, apostrophes
  • Whitespace normalised (strip leading/trailing)
"""

import re
import bleach
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, model_validator, Field


# ── Helpers ───────────────────────────────────────────────────────────────────

def sanitize(value: str) -> str:
    """Strip all HTML tags and attributes using bleach."""
    return bleach.clean(value, tags=[], attributes={}, strip=True).strip()


# ── Request ───────────────────────────────────────────────────────────────────

class ContactRequest(BaseModel):
    """
    Validated + sanitized input from the contact form.
    FastAPI automatically returns 422 if any validation fails.
    """

    full_name: str = Field(..., min_length=2, max_length=150)
    email:     EmailStr
    subject:   str = Field(..., min_length=3, max_length=300)
    message:   str = Field(..., min_length=10, max_length=5000)

    # ── Sanitization validators ───────────────────────────────────────────

    @field_validator("full_name", mode="before")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        v = sanitize(v)
        if not re.match(r"^[\w\s\-'.]+$", v, re.UNICODE):
            raise ValueError(
                "Name may only contain letters, spaces, hyphens, and apostrophes."
            )
        return v

    @field_validator("subject", mode="before")
    @classmethod
    def sanitize_subject(cls, v: str) -> str:
        return sanitize(v)

    @field_validator("message", mode="before")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        return sanitize(v)

    @field_validator("email", mode="before")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        return v.strip().lower()


# ── Response ──────────────────────────────────────────────────────────────────

class ContactResponse(BaseModel):
    """Successful API response body."""
    success: bool = True
    message: str
    id: int  # ID of the saved database record


class ErrorResponse(BaseModel):
    """Error API response body."""
    success: bool = False
    message: str
    detail: str | None = None
