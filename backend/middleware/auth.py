"""
Ultron Empire — API Key & JWT Authentication Middleware
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from backend.config import settings

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

# Paths that never require authentication
PUBLIC_PATHS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/token",
}


def _is_public_path(path: str) -> bool:
    """Check if the request path is public (no auth required)."""
    # Exact match
    if path in PUBLIC_PATHS:
        return True
    # Docs sub-paths served by FastAPI/Swagger
    if path.startswith("/docs") or path.startswith("/redoc"):
        return True
    return False


def _is_dev_mode() -> bool:
    """Return True when running in development mode (auth is optional)."""
    return settings.APP_ENV.lower() == "development"


def _get_valid_api_keys() -> set[str]:
    """Parse comma-separated API keys from settings."""
    raw = settings.API_KEYS.strip()
    if not raw:
        return set()
    return {k.strip() for k in raw.split(",") if k.strip()}


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def verify_jwt_token(token: str) -> dict:
    """Verify and decode a JWT token.  Raises HTTPException on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

async def get_current_user(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    """
    Dependency that authenticates the caller via:
      1. X-API-Key header  (shared key)
      2. Authorization: Bearer <jwt>

    In development mode (APP_ENV=development), auth is skipped and a
    default dev user is returned.

    Public paths are handled by the caller (router-level), but this
    dependency still short-circuits in dev mode for convenience.
    """
    # Dev mode — skip auth entirely
    if _is_dev_mode():
        return {"sub": "dev-user", "role": "admin", "dev_mode": True}

    # --- API key auth ---
    if api_key:
        valid_keys = _get_valid_api_keys()
        if valid_keys and api_key in valid_keys:
            return {"sub": "api-key-user", "role": "service"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # --- JWT bearer auth ---
    if bearer:
        payload = verify_jwt_token(bearer.credentials)
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing 'sub' claim",
            )
        return payload

    # No credentials supplied
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication credentials. "
               "Provide X-API-Key header or Authorization: Bearer <token>.",
        headers={"WWW-Authenticate": "Bearer"},
    )
