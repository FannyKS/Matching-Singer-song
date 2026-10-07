"""Matching endpoints."""

from fastapi import APIRouter

from app.schemas import MatchRequest, MatchResult
from app.services.matcher import compute_match

router = APIRouter(prefix="/match", tags=["matching"])


@router.post(
    "",
    response_model=MatchResult,
    summary="Score how well a singer fits a song",
    description=(
        "Takes a singer profile and a song profile and returns a 0–100 match score "
        "with a breakdown of the range, style and energy components."
    ),
)
def create_match(payload: MatchRequest) -> MatchResult:
    return compute_match(payload.singer, payload.song)