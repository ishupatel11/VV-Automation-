"""
rate_limiter.py — IP-based sliding window rate limiter.

Uses an in-memory dictionary — suitable for a single-instance deployment.
For multi-instance deployments, swap the store for Redis (see note below).

Default: 5 requests per IP per 60-second window.
"""

import time
import threading
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from config import get_settings
from logger import get_logger

log = get_logger(__name__)
settings = get_settings()

# ── Thread-safe store ─────────────────────────────────────────────────────────
_lock = threading.Lock()
# ip_address → deque of timestamps (float, epoch seconds)
_request_log: dict[str, deque] = defaultdict(deque)

WINDOW_SECONDS = 60  # Sliding window duration


def _get_client_ip(request: Request) -> str:
    """
    Extract the real client IP, respecting common proxy headers.
    Railway and Render both set X-Forwarded-For.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Header may be a comma-separated list; take the first (client) IP
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(request: Request) -> None:
    """
    Sliding window rate limiter.
    Raises HTTP 429 if the client IP exceeds RATE_LIMIT_PER_MINUTE requests
    within the last 60 seconds.

    Call as a FastAPI dependency:
        Depends(check_rate_limit)
    """
    ip = _get_client_ip(request)
    now = time.monotonic()
    limit = settings.RATE_LIMIT_PER_MINUTE

    with _lock:
        window = _request_log[ip]

        # Drop timestamps outside the sliding window
        while window and now - window[0] > WINDOW_SECONDS:
            window.popleft()

        if len(window) >= limit:
            oldest = window[0]
            retry_after = int(WINDOW_SECONDS - (now - oldest)) + 1
            log.warning(
                "Rate limit exceeded | ip=%s | requests_in_window=%d | limit=%d",
                ip, len(window), limit,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Too many requests. "
                    f"Please wait {retry_after} seconds before trying again."
                ),
                headers={"Retry-After": str(retry_after)},
            )

        window.append(now)
        log.info("Rate limit OK | ip=%s | requests_in_window=%d/%d", ip, len(window), limit)


# ── NOTE: Redis-backed alternative ────────────────────────────────────────────
# If you scale to multiple FastAPI instances (rare for a contact form),
# replace _request_log with Redis using `redis-py` or `aioredis`:
#
#   import redis
#   r = redis.Redis.from_url(os.environ["REDIS_URL"])
#   pipe = r.pipeline()
#   pipe.lpush(ip, now)
#   pipe.expire(ip, WINDOW_SECONDS)
#   pipe.llen(ip)
#   _, _, count = pipe.execute()
#   if count > limit: raise HTTPException(429, ...)
