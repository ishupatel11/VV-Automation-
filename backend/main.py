"""
main.py — FastAPI application entry point.

Configures:
  • CORS           — Only allows requests from whitelisted frontend origins
  • Trusted hosts  — Prevents host header injection in production
  • Startup event  — Initialises database tables on first boot
  • Health check   — GET /health for uptime monitors (Railway, UptimeRobot)
  • API router     — Mounts contact routes under /api prefix
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import init_db
from router import router
from logger import get_logger

log = get_logger(__name__)
settings = get_settings()


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run setup tasks before the server starts accepting requests."""
    log.info("=== %s v%s starting ===", settings.APP_NAME, settings.APP_VERSION)
    log.info("Environment : %s", settings.APP_ENV)
    log.info("Allowed origins: %s", settings.allowed_origins_list)

    # Create DB tables if they don't exist
    # (Harmless if tables already exist — does NOT drop or alter data)
    init_db()

    yield  # Server is running

    log.info("=== %s shutting down ===", settings.APP_NAME)


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production REST API for the V.V. Automation contact form. "
        "Stores submissions in MySQL and sends Gmail notifications."
    ),
    docs_url="/docs" if not settings.is_production else None,   # Disable Swagger in prod
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)


# ── Middleware ────────────────────────────────────────────────────────────────

# CORS — must be registered before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],   # Only what we need
    allow_headers=["Content-Type"],
)

# Trusted hosts — prevents host header injection attacks in production
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        # Add your Railway/Render domain and frontend domain here:
        # e.g. ["vv-contact-api.railway.app", "vvautomation.netlify.app"]
        allowed_hosts=["*"],  # Update with your actual domain before going live
    )


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")


import socket

def test_tcp_port(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], include_in_schema=False)
async def health_check():
    """
    Simple health probe for Railway / Render / UptimeRobot.
    Returns 200 OK when the service is running.
    """
    return JSONResponse(
        content={
            "status": "ok",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "smtp_465_reachable": test_tcp_port("smtp.gmail.com", 465),
            "smtp_587_reachable": test_tcp_port("smtp.gmail.com", 587),
        }
    )


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    return JSONResponse(
        content={
            "message": f"Welcome to {settings.APP_NAME}",
            "docs": "/docs",
            "health": "/health",
            "api": "/api/contact",
        }
    )
