"""Scoring engine for singer-song matches.

The overall score (0–100) is a weighted combination of three components:

* **range_fit**  (50%) — how much of the song's required pitch range the
  singer's vocal range covers.
* **style_fit**  (30%) — how well the singer's vocal style matches the
  song's genre.
* **energy_fit** (20%) — how close the singer's energy is to what the
  song demands.
"""

from __future__ import annotations

from app.schemas import MatchBreakdown, MatchResult, SingerProfile, SongProfile
from app.services.notes import note_to_semitone

WEIGHTS = {
    "range": 0.5,
    "style": 0.3,
    "energy": 0.2,
}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def range_fit(singer_range: tuple[int, int], song_range: tuple[int, int]) -> float:
    """Share of the song's required range the singer can cover."""
    s_low, s_high = singer_range
    r_low, r_high = song_range
    song_span = r_high - r_low
    if song_span == 0:
        # A single-note requirement: the singer either has it or not.
        return 100.0 if s_low <= r_low <= s_high else 0.0
    overlap = min(s_high, r_high) - max(s_low, r_low)
    if overlap <= 0:
        return 0.0
    return _clamp(overlap / song_span * 100.0)


def style_fit(singer_style: str, song_genre: str) -> float:
    style, genre = singer_style.strip().lower(), song_genre.strip().lower()
    if style == genre:
        return 100.0
    if not style or not genre:
        return 50.0
    if style in genre or genre in style:
        return 80.0
    return 40.0


def energy_fit(singer_energy: int, song_energy: int) -> float:
    """100 minus 10 points per point of energy difference."""
    return _clamp(100.0 - abs(singer_energy - song_energy) * 10.0)


def compute_match(singer: SingerProfile, song: SongProfile) -> MatchResult:
    """Score how well *singer* fits *song* on a 0–100 scale."""
    singer_range = (
        note_to_semitone(singer.vocal_range_low),
        note_to_semitone(singer.vocal_range_high),
    )
    song_range = (
        note_to_semitone(song.required_range_low),
        note_to_semitone(song.required_range_high),
    )

    scores = {
        "range": range_fit(singer_range, song_range),
        "style": style_fit(singer.vocal_style, song.genre),
        "energy": energy_fit(singer.energy, song.energy),
    }
    overall = _clamp(sum(scores[key] * WEIGHTS[key] for key in WEIGHTS))

    if overall >= 80:
        verdict = "Excellent match"
    elif overall >= 60:
        verdict = "Good match"
    elif overall >= 40:
        verdict = "Fair match"
    else:
        verdict = "Poor fit"

    return MatchResult(
        singer=singer.name,
        song=song.title,
        overall_score=round(overall, 1),
        verdict=verdict,
        breakdown=MatchBreakdown(
            range_fit=round(scores["range"], 1),
            style_fit=round(scores["style"], 1),
            energy_fit=round(scores["energy"], 1),
        ),
    )