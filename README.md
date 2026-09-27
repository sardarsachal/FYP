# NextTrack — Music Recommendation API

NextTrack recommends the **next song to play**. You give it the songs you have
just listened to and, optionally, what you are in the mood for (genre, mood,
tempo, artist). It returns one recommended track together with a plain-English
explanation of why it was chosen.

It is **stateless**: there are no user accounts and nothing about the listener
is stored. Everything the recommender needs comes in with the request.

The project includes a web app with a built-in music player, so you can try
it in the browser without writing any code.

---

## How it works

1. **Catalogue.** The app ships with 395 real tracks (190 of them playable).
   Their details were collected ahead of time from MusicBrainz, AcousticBrainz,
   Last.fm, YouTube and the Cover Art Archive and saved as JSON. The running
   app never calls these services.
2. **Filtering.** Songs you have already heard are removed. If you choose a
   genre or mood, only matching songs are kept.
3. **Taste from history.** If you don't set any preferences, NextTrack works
   out your likely genre, mood and tempo from the songs you have just played.
   It also favours artists you've been playing and similar artists.
4. **Scoring.** Every remaining song gets a score between 0 and 1, built from
   five features:

   | Feature    | Default weight | How it is scored                           |
   |------------|----------------|--------------------------------------------|
   | Genre      | 0.40           | 1 if it matches, otherwise 0               |
   | Artist     | 0.20           | 1 if it matches, otherwise 0               |
   | Tempo      | 0.20           | Closer to the target BPM scores higher     |
   | Mood       | 0.10           | 1 if it matches, otherwise 0               |
   | Popularity | 0.10           | Popularity ÷ 100                           |

5. **Result.** The highest-scoring song is returned with its score, a
   breakdown per feature, an explanation and a few runner-up alternatives.

---

## Project structure

```text
FYP/
├── app/                        # The application
│   ├── main.py                 # Starts the FastAPI app
│   ├── config.py               # Scoring weights and settings
│   ├── feedback.py             # Saves user-study ratings
│   ├── api/routes.py           # API endpoints
│   ├── core/                   # Recommendation logic
│   │   ├── scoring.py          #   scores each feature
│   │   ├── recommender.py      #   filters, ranks and picks the next track
│   │   ├── similarity.py       #   similar-artist lookup
│   │   └── explain.py          #   writes the explanation text
│   ├── data/                   # Track catalogue (JSON) and data loader
│   ├── models/schemas.py       # Request / response formats
│   └── web/index.html          # Web app with music player
├── scripts/
│   ├── evaluate.py             # Offline evaluation
│   ├── analyze_feedback.py     # Analyses user-study ratings
│   ├── enrich_dataset.py       # Builds the catalogue from external sources
│   └── seed_tracks.py          # Starting list of tracks for enrichment
├── tests/                      # Automated tests (pytest)
├── results/                    # Saved evaluation, test and user-study output
├── sample_request.json         # Example request body
├── requirements.txt            # Python dependencies
└── .env.example                # Template for optional API keys
```

---

## Requirements

- **Python 3.12 or newer**
- `pip` (comes with Python)
- A web browser, to use the web app
- An internet connection, to play songs in the web app (they stream from YouTube)

No API keys or database are needed to run the app or the tests.

Python packages (installed in step 3 below): FastAPI, Uvicorn, Pydantic,
pytest, httpx, python-dotenv and SciPy. The exact versions are in
`requirements.txt`.

---

## How to run

The commands below are for macOS / Linux. Windows commands are shown where they
differ.

**1. Get the code**

```bash
git clone https://github.com/sardarsachal/FYP.git
cd FYP
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

**3. Install the dependencies**

```bash
pip install -r requirements.txt
```

**4. Start the server**

```bash
uvicorn app.main:app --port 8000
```

**5. Open the app**

| What                   | Address                        |
|------------------------|--------------------------------|
| Web app                | <http://localhost:8000>        |
| Interactive API docs   | <http://localhost:8000/docs>   |
| Health check           | <http://localhost:8000/health> |

> Use `localhost`, **not** `127.0.0.1`. YouTube will not play embedded videos
> on a page opened from a plain IP address.

To stop the server, press `Ctrl + C` in the terminal.

---

## Run the tests

```bash
pytest -q
```

All 98 tests should pass.

## Run the evaluation

```bash
python scripts/evaluate.py
```

This compares the recommender with random picks, tests how sensitive it is to
the weights, and compares history-aware recommendations with the baseline.
Saved output is in `results/`.

---

## Using the API directly

| Method | Endpoint     | Purpose                                   |
|--------|--------------|-------------------------------------------|
| GET    | `/health`    | Check the server is running               |
| POST   | `/recommend` | Get the next-track recommendation         |
| GET    | `/catalogue` | List all tracks, genres and moods         |
| POST   | `/feedback`  | Save a 1–5 rating (used in the user study)|

Example request, using the included sample file:

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

Example response (shortened):

```json
{
  "recommended_track": {
    "id": "t28", "title": "Wildfire", "artist": "The Hours",
    "genre": "rock", "tempo": 138, "mood": "energetic"
  },
  "score": 0.962,
  "explanation": "Recommended \"Wildfire\" because it matches the preferred genre rock, matches the energetic mood, matches the preferred artist The Hours, is close to the target tempo, and is a popular track.",
  "score_breakdown": { "genre": 0.4, "artist": 0.2, "tempo": 0.19, "mood": 0.1, "popularity": 0.072 }
}
```

---

## Rebuilding the catalogue (optional)

You only need this if you want to rebuild the track data yourself. The app
already includes the finished catalogue.

```bash
cp .env.example .env      # then add your Last.fm and YouTube API keys
python scripts/enrich_dataset.py --per-genre 40 --similar --apply
```

The keys are optional. Without them the script still runs, but it won't add
popularity figures or playable videos.
