"""
Activity Logger Service

FastAPI middleware that automatically captures all API requests and logs them
to the MongoDB `activity_logs` collection. Provides minimal-level detail:
action type, user (if authenticated), timestamp, status code, and endpoint.

Decodes the JWT cookie directly rather than relying on request.state, since
FastAPI dependencies resolve per-route and don't set state at the middleware level.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.database import get_activities_collection

logger = logging.getLogger(__name__)

# ---------- Paths to exclude (avoid recursive logging of activity-log queries) ----------
EXCLUDED_PREFIXES = {
    "/docs",
    "/openapi",
    "/redoc",
    "/api/activities",
}


def _should_log(path: str) -> bool:
    """Return True if the request path should be logged."""
    for prefix in EXCLUDED_PREFIXES:
        if path.startswith(prefix):
            return False
    return True


def _decode_user_from_cookie(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Try to decode the JWT cookie to extract user_id and username.

    Directly decodes the access_token cookie so we can capture the user
    even though FastAPI dependencies haven't run yet at the middleware level.
    Returns (user_id, username) — both may be None for unauthenticated requests.
    """
    try:
        from app.services.auth import decode_access_token
        from app.database import get_users_collection
        import asyncio

        token = request.cookies.get("access_token")
        if not token:
            return None, None

        payload = decode_access_token(token)
        if payload is None:
            return None, None

        user_id = payload.get("sub")
        if user_id is None:
            return None, None

        # We can't easily run an async query here (this runs in sync context),
        # so return the user_id from the token. Username lookup would require
        # restructuring, so we skip it for performance.
        return user_id, None
    except Exception:
        return None, None


class ActivityLoggerMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that logs every API request to the activity_logs collection.

    Captures: HTTP method, endpoint path, status code, user (from JWT cookie),
    execution duration, and an optional detail/error string.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip excluded paths early
        if not _should_log(request.url.path):
            return await call_next(request)

        # Extract user info from JWT cookie before the request is processed
        user_id, username = _decode_user_from_cookie(request)

        start_time = time.perf_counter()
        detail: Optional[str] = None
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            detail = f"{type(exc).__name__}: {str(exc)}"
            status_code = getattr(exc, "status_code", 500)
            raise
        finally:
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            # Build the log document
            log_doc = {
                "user_id": user_id,
                "username": username,
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "detail": detail,
                "created_at": datetime.now(timezone.utc),
            }

            # Fire-and-forget insert
            try:
                col = await get_activities_collection()
                await col.insert_one(log_doc)
            except Exception as e:
                logger.warning(f"Failed to write activity log: {e}")
