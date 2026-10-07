# Matching-Singer-song

Rates how well a singer fits a song — the **Olddies** song-matching tool.

A FastAPI service that takes a singer profile and a song profile and returns a
0–100 match score with a breakdown of three components:

| Component  | Weight | What it measures                                      |
| ---------- | ------ | ----------------------------------------------------- |
| Range fit  | 50%    | How much of the song's required pitch range the singer covers |
| Style fit  | 30%    | How well the singer's vocal style matches the song's genre    |
| Energy fit | 20%    | How close the singer's energy (1–10) is to the song's         |

## Project layout

```
.
├── app/
│   ├── main.py              # FastAPI app and meta endpoints
│   ├── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   └── matching.py      # POST /match endpoint
│   └── services/
│       ├── notes.py         # Note → semitone conversion
│       └── matcher.py       # Scoring engine
├── tests/
│   └── test_matching.py
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

# 3. Run the API (http://127.0.0.1:8000, interactive docs at /docs)
uvicorn app.main:app --reload
```

## Example request

```bash
curl -X POST http://127.0.0.1:8000/match \
  -H "Content-Type: application/json" \
  -d '{
    "singer": {
      "name": "Mary J.",
      "vocal_range_low": "C3",
      "vocal_range_high": "C6",
      "vocal_style": "pop",
      "energy": 5
    },
    "song": {
      "title": "Time After Time",
      "genre": "pop",
      "required_range_low": "G3",
      "required_range_high": "E5",
      "energy": 5
    }
  }'
```

Example response:

```json
{
  "singer": "Mary J.",
  "song": "Time After Time",
  "overall_score": 100.0,
  "verdict": "Excellent match",
  "breakdown": { "range_fit": 100.0, "style_fit": 100.0, "energy_fit": 100.0 }
}
```

Notes use [scientific pitch notation](https://en.wikipedia.org/wiki/Scientific_pitch_notation),
e.g. `C4` (middle C), with `#`/`b` accidentals like `F#5` or `Bb2` supported.

## Running tests

```bash
pytest
```