from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Redis-backed rate limiter — required for multi-process and Vercel serverless.
# Falls back to in-memory if REDIS_URL is not set (local dev without Redis).
_storage_uri = getattr(settings, "REDIS_URL", None) or "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri,
    default_limits=[],  # no global default; limits are set per-route
)
