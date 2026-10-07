"""Helpers for working with musical notes as numbers.

Notes use scientific pitch notation (e.g. C4 = middle C) and are converted
to absolute semitone numbers so ranges can be compared arithmetically.
"""

from __future__ import annotations

import re

NOTE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_NOTE_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d)$")


def note_to_semitone(note: str) -> int:
    """Convert a note like 'C4' or 'Bb3' to an absolute semitone number."""
    match = _NOTE_RE.match(note.strip())
    if not match:
        raise ValueError(f"Invalid note: {note!r} (expected e.g. C4 or Bb3)")
    letter, accidental, octave = match.groups()
    semitone = NOTE_OFFSETS[letter.upper()] + 12 * int(octave)
    if accidental == "#":
        semitone += 1
    elif accidental == "b":
        semitone -= 1
    return semitone