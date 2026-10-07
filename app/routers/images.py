"""Singer photo endpoint — redirects the browser to the Wikimedia image."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.services.avatars import singer_image

router = APIRouter(prefix="/singer-image", tags=["images"])


@router.get(
    "/{name}",
    response_class=RedirectResponse,
    summary="Photo for a singer (redirects to Wikimedia)",
)
def get_singer_image(name: str):
    url = singer_image(name)
    if not url:
        raise HTTPException(status_code=404, detail=f"No photo found for {name!r}")
    return RedirectResponse(url)