from fastapi import FastAPI, Request
import structlog

from .routes import router
from .settings import settings
from .middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestIdMiddleware
from .logging_config import configure_logging

configure_logging()
log = structlog.get_logger()

app = FastAPI(title="Secure Payments API", version="1.0.0")

# Middleware order matters
app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, redis_url=settings.redis_url, max_requests=60, window_seconds=60)

@app.middleware("http")
async def access_log(request: Request, call_next):
    rid = getattr(request.state, "request_id", None)
    response = await call_next(request)
    log.info(
        "http_request",
        request_id=rid,
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
    )
    return response

app.include_router(router)
