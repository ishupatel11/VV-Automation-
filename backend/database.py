"""
database.py — SQLAlchemy database engine, session factory, and Base model.

Uses synchronous PyMySQL driver (mysql+pymysql) which is simpler to deploy
on Railway/Render than async drivers and avoids additional async complexity.

The `get_db` dependency is injected into FastAPI route handlers via Depends().
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import get_settings
from logger import get_logger

log = get_logger(__name__)

settings = get_settings()


# ── Engine ────────────────────────────────────────────────────────────────────
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_engine(
    settings.DATABASE_URL,
    # SQLite needs check_same_thread=False for FastAPI's threading model
    connect_args={"check_same_thread": False} if is_sqlite else {},
    # Connection pool settings (SQLite doesn't support pool_size/max_overflow)
    **({} if is_sqlite else {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }),
    echo=not settings.is_production,
)

# ── Session Factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ── Declarative Base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """All ORM models inherit from this."""
    pass


# ── FastAPI Dependency ────────────────────────────────────────────────────────
def get_db():
    """
    Yield a database session scoped to a single request.
    The session is always closed — even if an exception occurs.

    Usage in routes:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Init ──────────────────────────────────────────────────────────────────────
def init_db():
    """
    Create all tables if they don't exist.
    Called once at application startup.
    In production prefer running schema.sql manually for full control.
    """
    from models import ContactMessage  # noqa: F401 — import triggers table registration
    Base.metadata.create_all(bind=engine)
    log.info("Database tables verified / created successfully.")
