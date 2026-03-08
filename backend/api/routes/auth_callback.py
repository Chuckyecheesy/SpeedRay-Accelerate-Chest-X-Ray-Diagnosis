"""Auth0 callback handling (SpeedRay)."""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["auth"])


@router.get("/callback")
def auth_callback(code: str = "", state: str = ""):
    # Frontend handles Auth0 callback; backend may validate code and issue session
    return RedirectResponse(url="/")
