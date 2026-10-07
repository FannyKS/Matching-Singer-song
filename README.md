# Matching-Singer-song

The **Olddies** singing toolbox — two things in one FastAPI app:

1. 🎮 **Matching game** — a host-controlled board where players match face-down
   song cards to the singer who performs them.
2. 🎯 **Analyzer** — score how well a singer profile fits a song (range, style, energy).

## The matching game

- **Left column** — song cards, face down (flip one to reveal the title). Each
  card front shows its **number on a music note**, with bonus notes scattered
  at random spots so no two cards look alike.
- **Right column** — singer names, face up, each with a **real photo** pulled
  from Wikimedia (Chinese/English Wikipedia); singers without a photo get a
  letter avatar. A singer who performs several songs appears once per song.
- 🎭 **Stage view** — one click switches the board to a second layout with the
  song cards across the top and the singers below (perfect for a projector).
  Correct matches draw an animated glowing line between the pair.
- Pick a song, then pick a singer. A correct pair triggers a **"Match!"** popup
  with a confetti burst, and the pair stays frozen on the board with a green glow.
- **↻ Reload songs** — the host presses this after adding/editing/deleting songs
  in `songs/` to pull a fresh board immediately.
- **🎵 Music** — light synthesized background music (built into the page — no
  audio files, no copyright). Toggle it on/off anytime.
- Songs are **randomly selected** — 10 per round — from every CSV in the
  `songs/` folder.
- Press **⏹ Game Finish** to end the round: you get a summary (pairs, first-try
  score, attempts, time) and a button to start a **new board**.

The correct song→singer pairs are checked **server-side**, so the answer key is
never exposed to the browser.

### Editing the songs

Put your answer keys in the **`songs/` folder** — every `*.csv` there is read
and merged. Each file has two columns, `song,singer` (a header row is fine):

```csv
song,singer
紙船,許冠傑
鼓舞,陳百強
Crazy,Patsy Cline
```

Rules:

- Song titles must be unique across the folder (conflicting repeats are ignored
  with a warning).
- A singer may have any number of songs — they get that many cards on the board.
- Songs **without a singer** are skipped (with a warning on screen), so you can
  fill your spreadsheet in gradually.
- Quote any title containing a comma, e.g. `"Hello, Dolly!",Louis Armstrong`.
- Files saved by Excel (UTF-8 BOM, Big5, GB2312, CRLF line endings…) are decoded
  automatically — a fresh export from Excel "just works".
- Everything is re-read on every new board, so edits show up on the next
  Game Finish without restarting the server.

A sample file lives at `songs/english_oldies.csv` if you want a reference.

## The analyzer

`POST /match` takes a singer profile and a song profile and returns a 0–100 score:

| Component  | Weight | What it measures                                              |
| ---------- | ------ | ------------------------------------------------------------- |
| Range fit  | 50%    | How much of the song's required pitch range the singer covers |
| Style fit  | 30%    | How well the singer's vocal style matches the song's genre    |
| Energy fit | 20%    | How close the singer's energy (1–10) is to the song's         |

Notes use [scientific pitch notation](https://en.wikipedia.org/wiki/Scientific_pitch_notation),
e.g. `C4` (middle C); `#`/`b` accidentals like `F#5` or `Bb2` are supported.

## Project layout

```
.
├── app/
│   ├── main.py              # FastAPI app, page routes, meta endpoints
│   ├── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── matching.py      # POST /match (analyzer)
│   │   ├── game.py          # GET /game/board, POST /game/match
│   │   └── images.py        # GET /singer-image/{name} → Wikimedia photo
│   └── services/
│       ├── notes.py         # Note → semitone conversion
│       ├── matcher.py       # Analyzer scoring engine
│       ├── game.py          # Answer-key loading + board sampling
│       └── avatars.py       # Singer-photo lookup (zh→en fallback, cached)
├── songs/                     # The answer keys — put your CSV(s) here
├── web/
│   ├── index.html           # The matching game
│   └── analyzer.html        # The singer-fit analyzer
├── tests/
│   ├── test_matching.py
│   ├── test_game.py
│   └── test_avatars.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Getting started

Requires Python 3.9+.

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
uvicorn app.main:app --reload
```

Then open:

| URL                            | What                              |
| ------------------------------ | --------------------------------- |
| http://127.0.0.1:8000/game     | 🎮 the matching game              |
| http://127.0.0.1:8000/analyzer | 🎯 the singer-fit analyzer        |
| http://127.0.0.1:8000/docs     | interactive API docs              |

### No typing required 🎉

Double-click **`Start-Game.command`** (macOS): it starts the server if needed
and opens the game in your browser automatically. The game page also works if
you open `web/index.html` directly from Finder — it talks to the server at
`http://127.0.0.1:8000` on its own (the server just needs to be running).

## API summary

| Method | Path                     | Purpose                                             |
| ------ | ------------------------ | --------------------------------------------------- |
| GET    | `/game/board`            | Shuffled song titles + singer names (no pairing)     |
| POST   | `/game/match`            | `{song, singer}` → `{correct: true/false}`           |
| POST   | `/match`                 | Analyzer: singer + song profiles → 0–100 match score |
| GET    | `/singer-image/{name}`   | Redirect to the singer's Wikimedia photo (or 404)    |
| GET    | `/health`                | Health check                                         |

## Running tests

```bash
pytest
```