"""Shared rate limiter instance — importable without circular dependencies."""

from __future__ import annotations

from starlette.requests import Request
from slowapi import Limiter

from api.config import RATE_LIMIT_DEFAULT, TRUST_PROXY


def _get_real_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For only when behind a trusted proxy."""
    if TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "127.0.0.1"


limiter = Limiter(key_func=_get_real_ip, default_limits=[RATE_LIMIT_DEFAULT])
