"""Game board and match-check endpoints.

The answer key is re-read from the ``songs/`` folder on every request, so the
host can edit the CSV files and the very next round picks up the changes.
"""

from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.schemas import GameBoard, MatchAttempt, MatchCheck
from app.services.game import ROUND_SIZE, load_answer_key, sample_board

router = APIRouter(prefix="/game", tags=["game"])


@router.get("/board", response_model=GameBoard, summary="Get a shuffled game board")
def get_board(
    size: int = Query(default=ROUND_SIZE, ge=1, le=30),
    language: Literal["mixed", "chinese"] = "mixed",
) -> GameBoard:
    """Returns shuffled song titles and singer names — never the pairing.

    ``size`` lets the client ask for bigger rounds (e.g. 15 in Advance mode);
    ``language="chinese"`` draws only Chinese-titled songs. Counts are capped
    by what's available.
    """
    try:
        key, notes = load_answer_key()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return sample_board(key, notes=notes, size=size, chinese_only=language == "chinese")


@router.post("/match", response_model=MatchCheck, summary="Check a song↔singer match")
def check_match(payload: MatchAttempt) -> MatchCheck:
    """Tells the client whether the chosen singer performs that song."""
    try:
        key, _ = load_answer_key()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    expected = key.get(payload.song)
    if expected is None:
        raise HTTPException(status_code=404, detail=f"Unknown song: {payload.song!r}")
    return MatchCheck(
        song=payload.song,
        singer=payload.singer,
        correct=expected == payload.singer,
    )