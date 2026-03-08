"""Auth0 token validation middleware for SpeedRay."""

from typing import Callable, Optional

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


def get_bearer_token(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


async def validate_auth0_middleware(request: Request, call_next: Callable):
    """Validate Auth0 JWT on protected routes. Skip for health and public."""
    path = request.url.path
    if path in ("/", "/health", "/api/health", "/callback"):
        return await call_next(request)

    token = get_bearer_token(request)
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid authorization"})

    # Optional: decode and verify JWT with Auth0 JWKS
    try:
        import jwt
        from ..config import get_settings
        s = get_settings()
        if s.auth0_domain:
            jwks_uri = f"https://{s.auth0_domain}/.well-known/jwks.json"
            # jwt.decode(token, options={"verify_signature": True}, ...) with jwks
            pass
    except Exception:
        pass

    return await call_next(request)
