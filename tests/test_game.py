"""Tests for the matching game board and answer-key logic."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.game import load_answer_key, sample_board

client = TestClient(app)


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


# --- answer key loading -----------------------------------------------------

def test_load_answer_key_reads_pairs(tmp_path):
    _write(tmp_path, "a.csv", "song,singer\nTennessee Waltz,Patsy Cline\nCrazy,Patsy Cline\n")
    key, notes = load_answer_key(tmp_path)
    assert key == {"Tennessee Waltz": "Patsy Cline", "Crazy": "Patsy Cline"}
    assert notes == []


def test_load_answer_key_skips_rows_without_singer(tmp_path):
    _write(tmp_path, "a.csv", "song,singer\nCrazy,Patsy Cline\nA Song Without A Singer,\n")
    key, notes = load_answer_key(tmp_path)
    assert key == {"Crazy": "Patsy Cline"}
    assert any("no singer" in note for note in notes)


def test_load_answer_key_ignores_duplicate_songs(tmp_path):
    _write(tmp_path, "a.csv", "song,singer\nCrazy,Patsy Cline\nCrazy,Patsy Cline\n")
    key, _ = load_answer_key(tmp_path)
    assert key == {"Crazy": "Patsy Cline"}


def test_load_answer_key_warns_on_conflicting_duplicates(tmp_path):
    _write(tmp_path, "a.csv", "song,singer\nCrazy,Patsy Cline\nCrazy,Someone Else\n")
    key, notes = load_answer_key(tmp_path)
    assert key == {"Crazy": "Patsy Cline"}
    assert any("different singer" in note for note in notes)


def test_load_answer_key_merges_multiple_files(tmp_path):
    _write(tmp_path, "a.csv", "song,singer\nCrazy,Patsy Cline\n")
    _write(tmp_path, "b.csv", "song,singer\nMy Girl,The Temptations\n")
    key, _ = load_answer_key(tmp_path)
    assert key == {"Crazy": "Patsy Cline", "My Girl": "The Temptations"}


def test_load_answer_key_reads_excel_bom_and_crlf(tmp_path):
    path = tmp_path / "a.csv"
    path.write_bytes(b"\xef\xbb\xbfsong,singer\r\nCrazy,Patsy Cline\r\n")
    key, _ = load_answer_key(tmp_path)
    assert key == {"Crazy": "Patsy Cline"}


def test_load_answer_key_handles_quoted_comma_in_title(tmp_path):
    _write(tmp_path, "a.csv", 'song,singer\n"Hello, Dolly!",Louis Armstrong\n')
    key, _ = load_answer_key(tmp_path)
    assert key == {"Hello, Dolly!": "Louis Armstrong"}


def test_load_answer_key_raises_when_nothing_usable(tmp_path):
    _write(tmp_path, "a.csv", "song,singer\nOnly Songs,\n")
    with pytest.raises(ValueError):
        load_answer_key(tmp_path)


def test_load_answer_key_raises_when_no_csv(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_answer_key(tmp_path)


# --- board sampling ---------------------------------------------------------

def test_sample_board_shape_and_subset():
    key = {f"Song {i}": f"Singer {i % 3}" for i in range(12)}
    board = sample_board(key, size=10)
    assert board.size == 10
    assert len(board.songs) == len(board.singers) == 10
    assert set(board.songs) <= set(key)
    assert board.available == 12


def test_sample_board_defaults_to_round_size_ten():
    key = {f"Song {i}": f"Singer {i}" for i in range(40)}
    board = sample_board(key)
    assert board.size == 10


def test_sample_board_repeats_singers_for_multi_song_artists():
    key = {f"Elvis {i}": "Elvis Presley" for i in range(4)}
    board = sample_board(key, size=4)
    assert board.singers.count("Elvis Presley") == 4


# --- API --------------------------------------------------------------------

def _load_key():
    key, _ = load_answer_key()
    return key


def test_match_endpoint_accepts_correct_pair():
    key = _load_key()
    song, singer = next(iter(key.items()))
    response = client.post("/game/match", json={"song": song, "singer": singer})
    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_match_endpoint_rejects_wrong_pair():
    key = _load_key()
    songs = list(key)
    if len(songs) < 2:
        pytest.skip("Need at least two songs to test a wrong pair")
    expected = key[songs[0]]
    wrong = next((key[s] for s in songs[1:] if key[s] != expected), None)
    if wrong is None:
        pytest.skip("Need a second, different singer to test a wrong pair")
    response = client.post("/game/match", json={"song": songs[0], "singer": wrong})
    assert response.status_code == 200
    assert response.json()["correct"] is False


def test_match_endpoint_returns_404_for_unknown_song():
    response = client.post(
        "/game/match",
        json={"song": "A Song That Does Not Exist", "singer": "Anyone"},
    )
    assert response.status_code == 404


def test_board_endpoint_does_not_leak_the_pairing():
    response = client.get("/game/board")
    assert response.status_code == 200
    data = response.json()
    assert data["size"] == len(data["songs"]) == len(data["singers"])
    assert isinstance(data["warnings"], list)
    assert data["available"] >= data["size"]
    assert "answer" not in data and "pairs" not in data


def test_board_endpoint_uses_ten_random_songs_when_available():
    key = _load_key()
    if len(key) < 10:
        pytest.skip("Sample data must have at least 10 songs for this check")
    response = client.get("/game/board")
    assert response.status_code == 200
    assert response.json()["size"] == 10