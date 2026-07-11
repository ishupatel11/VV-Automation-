"""
config.py — Application settings loaded from environment variables.

All sensitive credentials are read from a .env file (local dev) or
from the host platform's environment (Railway / Render in production).

Never commit the .env file — only commit .env.example.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────
    # Full MySQL DSN, e.g.:
    #   mysql+pymysql://user:password@host:3306/dbname
    DATABASE_URL: str

    # ── Gmail SMTP ────────────────────────────────────────────────────────
    # The Gmail address used to SEND the emails (your Google account)
    GMAIL_USER: str

    # Gmail App Password (NOT your regular password).
    # Generate at: https://myaccount.google.com/apppasswords
    GMAIL_APP_PASSWORD: str

    # The Gmail address where contact submissions are DELIVERED
    RECIPIENT_EMAIL: str

    # ── CORS ──────────────────────────────────────────────────────────────
    # Comma-separated list of allowed frontend origins.
    # Example: "https://vvautomation.netlify.app,https://www.vvautomation.com"
    # Use "*" only for local development; never in production.
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ── Rate Limiting ─────────────────────────────────────────────────────
    # Maximum contact form submissions allowed per IP per minute
    RATE_LIMIT_PER_MINUTE: int = 5

    # ── App Meta ──────────────────────────────────────────────────────────
    APP_ENV: str = "development"  # "development" | "production"
    APP_NAME: str = "VV Automation Contact API"
    APP_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Return ALLOWED_ORIGINS as a Python list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached singleton — settings are read once at startup.
    Use FastAPI's Depends(get_settings) to inject into routes.
    """
    return Settings()
