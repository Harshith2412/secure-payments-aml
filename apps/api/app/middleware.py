import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
import structlog

log = structlog.get_logger()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window-ish rate limiter using Redis INCR + EXPIRE.
    Policy: max_requests per window_seconds per (ip + path).
    """
    def __init__(self, app, redis_url: str, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)
        self.max = max_requests
        self.win = window_seconds

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        key = f"rl:{ip}:{request.url.path}:{int(time.time() // self.win)}"
        cnt = self.r.incr(key)
        if cnt == 1:
            self.r.expire(key, self.win)

        if cnt > self.max:
            return JSONResponse(
                status_code=429,
                content={"detail": "rate_limited"},
                headers={"Retry-After": str(self.win)},
            )
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # “WAF-ready” baseline headers (tune CSP to your frontend)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
