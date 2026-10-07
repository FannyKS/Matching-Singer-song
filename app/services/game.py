"""Game data: answer-key loading and board sampling.

The answer key lives in the ``songs/`` folder — every ``*.csv`` in it is read
and merged. Each file should have two columns: ``song,singer``. The mapping of
*which singer performs which song* is the source of truth for the game.

The loader is deliberately lenient so a half-finished spreadsheet still makes a
playable board:

* rows without a singer are skipped (they can't be matched yet),
* duplicate song titles are ignored (with a warning),
* files saved by Excel (UTF-8 BOM, Big5, GB2312…) are decoded automatically.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

from app.schemas import GameBoard

SONGS_DIR = Path(__file__).resolve().parent.parent.parent / "songs"
# How many songs go on each round's board (fewer if fewer are available).
ROUND_SIZE = 10

# Excel writes a UTF-8 BOM; older Mac/Windows spreadsheets may be Big5/GB2312.
_ENCODINGS = ("utf-8-sig", "big5", "gb18030")


def _decode(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in _ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path.name} — is it a text/CSV file?")


def load_answer_key(directory: Path = SONGS_DIR) -> tuple[dict[str, str], list[str]]:
    """Read every CSV in *directory*.

    Returns ``(key, notes)`` where ``key`` maps song → singer and ``notes`` is
    a list of human-readable warnings for the host (skipped rows, duplicates).
    """
    files = sorted(directory.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No .csv files found in {directory}")

    key: dict[str, str] = {}
    notes: list[str] = []

    for path in files:
        skipped = 0
        ignored_dupe = 0
        unquoted_commas = 0
        first_data_row = True

        for row in csv.reader(_decode(path).splitlines()):
            if not row or all(not cell.strip() for cell in row):
                continue

            cells = [cell.strip() for cell in row]

            # Header row: "Song,Singer" (any case) on the first data row.
            if first_data_row and cells[0].lower() == "song":
                first_data_row = False
                continue
            first_data_row = False

            # No singer → can't form a pair yet, skip with a warning.
            if len(cells) < 2 or not cells[-1]:
                skipped += 1
                continue

            if len(cells) == 2:
                song, singer = cells
            else:
                # Extra columns almost always mean an unquoted comma in the
                # title (e.g. "Hello, Dolly!"). Take the last cell as singer.
                song, singer = ",".join(cells[:-1]), cells[-1]
                unquoted_commas += 1

            if song in key:
                if key[song] != singer:
                    notes.append(
                        f"{path.name}: '{song}' repeats with a different singer —"
                        " keeping the first one."
                    )
                ignored_dupe += 1
                continue

            key[song] = singer

        if unquoted_commas:
            notes.append(
                f"{path.name}: {unquoted_commas} title(s) contain a comma —"
                " wrap them in quotes, e.g. \"Song, Title\",Singer"
            )
        if skipped:
            notes.append(
                f"{path.name}: {skipped} song(s) skipped — no singer filled in yet"
            )
        if ignored_dupe:
            notes.append(f"{path.name}: {ignored_dupe} duplicate song title(s) ignored")

    if not key:
        raise ValueError(
            f"No usable songs with singers found in {directory} — "
            "fill in the singer column of your CSV and try again."
        )
    return key, notes


def sample_board(
    key: dict[str, str],
    notes: list[str] | None = None,
    size: int = ROUND_SIZE,
    rng: random.Random | None = None,
) -> GameBoard:
    """Randomly pick a round's worth of entries and shuffle both columns.

    Singers repeat in the right column exactly as often as they perform songs
    in the answer key, so a singer with several songs gets several cards.
    """
    rng = rng or random
    picked = rng.sample(sorted(key.keys()), k=min(size, len(key)))

    songs = list(picked)
    singers = [key[song] for song in picked]
    rng.shuffle(songs)
    rng.shuffle(singers)
    return GameBoard(
        songs=songs,
        singers=singers,
        size=len(songs),
        available=len(key),
        warnings=list(notes or []),
    )