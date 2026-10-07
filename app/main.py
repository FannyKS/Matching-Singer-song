"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routers import game, matching

app = FastAPI(
    title="Matching-Singer-song",
    description="A singer↔song matching game, plus a singer-fit analyzer — the Olddies toolbox.",
    version="0.3.0",
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

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "app": "Matching-Singer-song",
        "game": "/game",
        "analyzer": "/analyzer",
        "docs": "/docs",
        "health": "ok",
    }


@app.get("/game", tags=["meta"], response_class=FileResponse)
def game_page() -> FileResponse:
    """Serve the matching game board."""
    return FileResponse(WEB_DIR / "index.html")


@app.get("/analyzer", tags=["meta"], response_class=FileResponse)
def analyzer_page() -> FileResponse:
    """Serve the singer-fit analyzer (score how well a singer fits a song)."""
    return FileResponse(WEB_DIR / "analyzer.html")


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}