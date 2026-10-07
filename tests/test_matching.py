"""Tests for the matching API and scoring engine."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import SingerProfile, SongProfile
from app.services.matcher import compute_match
from app.services.notes import note_to_semitone

client = TestClient(app)


# --- note parsing -----------------------------------------------------------

def test_note_to_semitone():
    assert note_to_semitone("C4") == 48  # middle C
    assert note_to_semitone("A4") == 57
    assert note_to_semitone("Bb2") == 34
    assert note_to_semitone("F#5") == 66
    assert note_to_semitone("F#6") == 78


def test_note_to_semitone_rejects_garbage():
    with pytest.raises(ValueError):
        note_to_semitone("Hello")


# --- scoring engine ---------------------------------------------------------

PERFECT_SINGER = SingerProfile(
    name="Mary J.",
    vocal_range_low="C3",
    vocal_range_high="C6",
    vocal_style="pop",
    energy=5,
)

PERFECT_SONG = SongProfile(
    title="Time After Time",
    genre="pop",
    required_range_low="G3",
    required_range_high="E5",
    energy=5,
)


def test_perfect_match_scores_100():
    result = compute_match(PERFECT_SINGER, PERFECT_SONG)
    assert result.overall_score == 100.0
    assert result.verdict == "Excellent match"
    assert result.breakdown.range_fit == 100.0
    assert result.breakdown.style_fit == 100.0
    assert result.breakdown.energy_fit == 100.0


def test_completely_mismatched_singer_scores_low():
    singer = SingerProfile(
        name="Low-energy tenor",
        vocal_range_low="C3",
        vocal_range_high="C4",
        vocal_style="rock",
        energy=2,
    )
    song = SongProfile(
        title="Opera aria",
        genre="opera",
        required_range_low="C5",
        required_range_high="C6",
        energy=9,
    )
    result = compute_match(singer, song)
    assert result.overall_score < 40.0
    assert result.verdict == "Poor fit"


def test_range_is_weighted_most_heavily():
    # Same song, two singers: one with a small range, one with a huge range.
    narrow = SingerProfile(
        name="Narrow", vocal_range_low="C4", vocal_range_high="E4",
        vocal_style="pop", energy=5,
    )
    wide = SingerProfile(
        name="Wide", vocal_range_low="C2", vocal_range_high="C7",
        vocal_style="pop", energy=5,
    )
    song = PERFECT_SONG
    assert compute_match(wide, song).overall_score > compute_match(narrow, song).overall_score


# --- API --------------------------------------------------------------------

def test_match_endpoint_returns_score():
    payload = {
        "singer": PERFECT_SINGER.model_dump(),
        "song": PERFECT_SONG.model_dump(),
    }
    response = client.post("/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 100.0
    assert data["verdict"] == "Excellent match"


def test_match_endpoint_validates_bad_note():
    payload = {
        "singer": {
            "name": "Mary J.",
            "vocal_range_low": "not-a-note",
            "vocal_range_high": "C6",
            "vocal_style": "pop",
            "energy": 5,
        },
        "song": PERFECT_SONG.model_dump(),
    }
    response = client.post("/match", json=payload)
    assert response.status_code == 422


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}