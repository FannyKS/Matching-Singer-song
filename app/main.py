"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routers import game, images, matching

app = FastAPI(
    title="Matching-Singer-song",
    description="A singer↔song matching game, plus a singer-fit analyzer — the Olddies toolbox.",
    version="0.6.0",
)

# Allow the in-browser pages to call the API from any origin (dev convenience).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matching.router)
app.include_router(game.router)
app.include_router(images.router)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

# Serve the pages without letting browsers cache them, so fresh edits always
# show after a reload (no stale HTML surprises).
_NO_CACHE = {"Cache-Control": "no-store, no-cache, must-revalidate"}


@app.get("/", tags=["meta"], response_class=FileResponse)
def root() -> FileResponse:
    """Land on the level picker (Easy / Advance) launcher."""
    return FileResponse(WEB_DIR / "landing.html", headers=_NO_CACHE)


@app.get("/game", tags=["meta"], response_class=FileResponse)
def game_page() -> FileResponse:
    """Serve the matching game board."""
    return FileResponse(WEB_DIR / "index.html", headers=_NO_CACHE)


@app.get("/analyzer", tags=["meta"], response_class=FileResponse)
def analyzer_page() -> FileResponse:
    """Serve the singer-fit analyzer (score how well a singer fits a song)."""
    return FileResponse(WEB_DIR / "analyzer.html", headers=_NO_CACHE)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}