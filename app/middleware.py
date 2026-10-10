import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import RATE_LIMIT_SIGHTINGS_PER_MINUTE, RATE_LIMIT_REPORTS_PER_MINUTE
from app.utils import hash_client_ip

class SimpleRateLimiter:
    """Sliding window in-memory rate limiter per hashed IP."""
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.time()
        timestamps = self.requests[key]
        # Remove timestamps outside window
        self.requests[key] = [t for t in timestamps if now - t < window_seconds]
        if len(self.requests[key]) >= max_requests:
            return False
        self.requests[key].append(now)
        return True

limiter = SimpleRateLimiter()

def enforce_public_rate_limit(request: Request, endpoint_type: str = "sightings"):
    client_ip = request.client.host if request.client else "127.0.0.1"
    hashed_ip = hash_client_ip(client_ip)
    limit = RATE_LIMIT_SIGHTINGS_PER_MINUTE if endpoint_type == "sightings" else RATE_LIMIT_REPORTS_PER_MINUTE
    key = f"{endpoint_type}:{hashed_ip}"
    if not limiter.check_rate_limit(key, max_requests=limit, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment before submitting again to prevent duplicate submissions.",
        )

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
