"""FastAPI application entry point."""

from fastapi import FastAPI

from app.routers import matching

app = FastAPI(
    title="Matching-Singer-song",
    description="Rates how well a singer fits a song — the Olddies song-matching tool.",
    version="0.1.0",
)

app.include_router(matching.router)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "app": "Matching-Singer-song",
        "docs": "/docs",
        "health": "ok",
    }


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}