"""
Offline dataset enrichment for NextTrack.

Builds a catalogue of *real* tracks by taking a fixed seed list of
(artist, title, genre) queries (scripts/seed_tracks.py) and enriching each one
with metadata pulled from external music services:

    - MusicBrainz   (keyless) : canonical recording MBID, release year, genre tags
    - AcousticBrainz(keyless) : tempo (BPM) and mood, from community audio analysis
    - Last.fm       (API key) : popularity (listener counts)          [optional]
    - YouTube       (API key) : an embeddable video id for playback    [optional]
    - Cover Art Archive (keyless): album cover image url               [best-effort]

Design rules that keep this consistent with the project:

  * This runs OFFLINE and writes a static tracks.json. The live /recommend
    endpoint never calls these services, so it stays stateless and fast, and
    the demo never depends on network access or rate limits.
  * The output matches the exact schema the loader/scoring expect
    (id, title, artist, genre, tempo, mood, year, popularity) plus a few extra
    fields for the web app (youtube_id, mbid, cover_url, source). The loader
    ignores unknown fields, so the extras are harmless to the existing code.
  * Missing external data is never fatal: per-genre fallbacks fill tempo/mood,
    so every seed track yields a valid, schema-conformant record.

Run from the project root (the `nexttrack/` folder):

    # keyless dry run over a few tracks, prints results, writes nothing:
    python scripts/enrich_dataset.py --limit 5 --dry-run

    # full keyless build -> app/data/tracks.enriched.json (preview file):
    python scripts/enrich_dataset.py

    # with popularity + youtube ids (needs keys in .env), and merge the real
    # tracks into the bundled dataset (backs up the original first):
    python scripts/enrich_dataset.py --apply

Keys are read from environment variables or a .env file (see .env.example):
    LASTFM_API_KEY, YOUTUBE_API_KEY, MUSICBRAINZ_CONTACT
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import httpx

# Make `import app...` work when run as `python scripts/enrich_dataset.py`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:  # python-dotenv is optional; env vars still work without it
    pass

from app.models.schemas import Track  # noqa: E402  (after sys.path setup)
from scripts.seed_tracks import SEED_TRACKS  # noqa: E402

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DATA_DIR = PROJECT_ROOT / "app" / "data"
CURATED_FILE = DATA_DIR / "tracks.json"
PREVIEW_FILE = DATA_DIR / "tracks.enriched.json"
BACKUP_FILE = DATA_DIR / "tracks.curated.json"
SIMILARITY_FILE = DATA_DIR / "artist_similarity.json"
CACHE_DIR = Path(__file__).resolve().parent / ".cache"

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY", "").strip()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
MB_CONTACT = os.getenv("MUSICBRAINZ_CONTACT", "nexttrack-fyp@example.com").strip()
USER_AGENT = f"NextTrack-FYP/1.0 ( {MB_CONTACT} )"

# Controlled vocabulary — kept identical to the original curated dataset so the
# UI, tests, and scoring behave the same across curated and real tracks.
MOOD_VOCAB = ("calm", "energetic", "happy")

# Per-genre fallbacks, used only when AcousticBrainz has no analysis for a track.
GENRE_DEFAULT_TEMPO = {
    "ambient": 80, "country": 100, "edm": 128, "folk": 100, "hiphop": 90,
    "jazz": 110, "lofi": 75, "pop": 118, "rock": 125, "synthpop": 116,
}
GENRE_DEFAULT_MOOD = {
    "ambient": "calm", "country": "happy", "edm": "energetic", "folk": "calm",
    "hiphop": "energetic", "jazz": "calm", "lofi": "calm", "pop": "happy",
    "rock": "energetic", "synthpop": "energetic",
}

# Our controlled genre vocabulary -> the closest well-populated Last.fm tag,
# used to pull a larger real catalogue via tag.getTopTracks.
GENRE_LASTFM_TAG = {
    "ambient": "ambient", "country": "country", "edm": "electronic",
    "folk": "folk", "hiphop": "hip-hop", "jazz": "jazz", "lofi": "trip-hop",
    "pop": "pop", "rock": "rock", "synthpop": "synthpop",
}

# Minimum seconds between requests per host (be a good API citizen;
# MusicBrainz explicitly requires <= 1 request/second).
RATE_LIMITS = {
    "musicbrainz.org": 1.1,
    "acousticbrainz.org": 0.4,
    "ws.audioscrobbler.com": 0.25,
    "www.googleapis.com": 0.2,
    "coverartarchive.org": 0.3,
}
_last_call: dict[str, float] = {}
_USE_CACHE = True


# --------------------------------------------------------------------------- #
# HTTP layer: rate limiting + on-disk cache
# --------------------------------------------------------------------------- #

def _throttle(host: str) -> None:
    min_gap = RATE_LIMITS.get(host, 0.2)
    now = time.monotonic()
    wait = min_gap - (now - _last_call.get(host, 0.0))
    if wait > 0:
        time.sleep(wait)
    _last_call[host] = time.monotonic()


def _cache_path(url: str, params: dict | None) -> Path:
    key = url + "?" + json.dumps(params or {}, sort_keys=True)
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    host = httpx.URL(url).host or "misc"
    return CACHE_DIR / host / f"{digest}.json"


def get_json(url: str, params: dict | None = None, headers: dict | None = None,
             use_cache: bool = True) -> dict | None:
    """GET a URL and return parsed JSON, with rate limiting and disk caching.

    Returns None on any HTTP/parse error (callers treat that as "no data" and
    fall back), so one bad lookup never aborts a whole build.
    """
    cache_file = _cache_path(url, params)
    if use_cache and _USE_CACHE and cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except Exception:
            pass  # corrupt cache entry: fall through and re-fetch

    host = httpx.URL(url).host or "misc"
    _throttle(host)
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    try:
        resp = httpx.get(url, params=params, headers=hdrs, timeout=25,
                         follow_redirects=True)
        if resp.status_code != 200:
            return None
        data = resp.json()
    except Exception:
        return None

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(data))
    return data


# --------------------------------------------------------------------------- #
# Per-source lookups
# --------------------------------------------------------------------------- #

def _artist_matches(rec: dict, artist: str) -> bool:
    """True if a recording's artist credit matches the seed artist."""
    want = artist.lower()
    for credit in rec.get("artist-credit", []) or []:
        name = (credit.get("name") or "").lower()
        if want in name or name in want:
            return True
    return False


def mb_lookup(artist: str, title: str) -> dict:
    """Resolve a recording via MusicBrainz search.

    Returns {candidate_mbids, year, tags, release_mbid}. `candidate_mbids` are
    the artist-matched recordings in search-rank order, so the caller can probe
    AcousticBrainz across them and keep the first that actually has analysis.
    """
    query = f'artist:"{artist}" AND recording:"{title}"'
    data = get_json(
        "https://musicbrainz.org/ws/2/recording",
        params={"query": query, "fmt": "json", "limit": 10},
    )
    result: dict = {"candidate_mbids": [], "year": None, "tags": [],
                    "release_mbid": None}
    if not data or not data.get("recordings"):
        return result

    # Keep only recordings actually credited to the seed artist (drops covers
    # and same-title songs by other artists that pollute year/mbid selection).
    matched = [r for r in data["recordings"] if _artist_matches(r, artist)]
    if not matched:
        matched = data["recordings"]  # fall back to raw results if none matched

    result["candidate_mbids"] = [r["id"] for r in matched if r.get("id")]

    best = matched[0]
    result["tags"] = [t["name"] for t in best.get("tags", []) if "name" in t]
    releases0 = best.get("releases", []) or []
    if releases0:
        result["release_mbid"] = releases0[0].get("id")

    # Year: earliest year across the artist-matched recordings and their
    # releases. Minimum-across-candidates is far more likely to catch the
    # original release than trusting the top search hit (often a reissue).
    years: list[int] = []
    for rec in matched:
        for datestr in ([rec.get("first-release-date")]
                        + [rel.get("date") for rel in rec.get("releases", []) or []]):
            if datestr and len(datestr) >= 4 and datestr[:4].isdigit():
                y = int(datestr[:4])
                if 1900 <= y <= 2100:
                    years.append(y)
    if years:
        result["year"] = min(years)
    return result


def ab_features(mbid: str) -> dict:
    """Fetch tempo (BPM) and mood from AcousticBrainz for one recording MBID.

    Returns {tempo, mood} (either may be None if AcousticBrainz has no analysis).
    """
    out: dict = {"tempo": None, "mood": None, "mbid": mbid}
    if not mbid:
        return out

    low = get_json("https://acousticbrainz.org/api/v1/low-level",
                   params={"recording_ids": mbid})
    if low and mbid in low:
        bpm = low[mbid].get("0", {}).get("rhythm", {}).get("bpm")
        if isinstance(bpm, (int, float)) and 20 <= bpm <= 300:
            out["tempo"] = int(round(bpm))

    high = get_json("https://acousticbrainz.org/api/v1/high-level",
                    params={"recording_ids": mbid})
    if high and mbid in high:
        hl = high[mbid].get("0", {}).get("highlevel", {})
        out["mood"] = _mood_from_highlevel(hl)
    return out


def ab_features_best(candidate_mbids: list[str]) -> dict:
    """Probe AcousticBrainz across candidate recordings; keep the first with a
    real BPM. Maximises how many tracks get genuine audio features rather than
    per-genre fallbacks. Returns {tempo, mood, mbid}."""
    best_partial = {"tempo": None, "mood": None, "mbid": None}
    for mbid in candidate_mbids[:5]:  # cap probing to stay polite
        feats = ab_features(mbid)
        if feats["tempo"] is not None:
            return feats  # a fully-analysed recording — use it
        if best_partial["mbid"] is None:
            best_partial = feats  # remember the first probed mbid as fallback
    return best_partial


def _mood_from_highlevel(hl: dict) -> str | None:
    """Collapse AcousticBrainz high-level mood classifiers into calm/energetic/happy."""
    def is_(key: str, positive: str) -> bool:
        node = hl.get(key)
        return bool(node and node.get("value") == positive
                    and node.get("probability", 0) >= 0.5)

    if is_("mood_happy", "happy"):
        return "happy"
    if (is_("mood_aggressive", "aggressive") or is_("mood_party", "party")
            or is_("danceability", "danceable")):
        return "energetic"
    if is_("mood_relaxed", "relaxed") or is_("mood_sad", "sad"):
        return "calm"
    return None


def lastfm_popularity(artist: str, title: str) -> int | None:
    """Popularity in [0, 100] from Last.fm listener count (log-scaled)."""
    if not LASTFM_API_KEY:
        return None
    data = get_json(
        "https://ws.audioscrobbler.com/2.0/",
        params={"method": "track.getInfo", "api_key": LASTFM_API_KEY,
                "artist": artist, "track": title, "format": "json",
                "autocorrect": 1},
    )
    if not data or "track" not in data:
        return None
    try:
        listeners = int(data["track"].get("listeners", 0))
    except (ValueError, TypeError):
        return None
    if listeners <= 0:
        return None
    # ~3,000,000 listeners maps to 100; log scale so the low end isn't crushed.
    score = math.log10(listeners + 1) / math.log10(3_000_000) * 100
    return max(1, min(100, int(round(score))))


def lastfm_top_tracks(genre: str, limit: int) -> list[tuple[str, str, str]]:
    """Fetch popular real tracks for a genre via Last.fm tag.getTopTracks.

    Returns (artist, title, genre) tuples using our controlled genre label.
    """
    if not LASTFM_API_KEY:
        return []
    tag = GENRE_LASTFM_TAG.get(genre, genre)
    data = get_json(
        "https://ws.audioscrobbler.com/2.0/",
        params={"method": "tag.getTopTracks", "tag": tag, "limit": limit,
                "api_key": LASTFM_API_KEY, "format": "json"},
    )
    out: list[tuple[str, str, str]] = []
    for tr in (data or {}).get("tracks", {}).get("track", []):
        name = tr.get("name")
        artist = (tr.get("artist") or {}).get("name")
        if name and artist:
            out.append((artist, name, genre))
    return out


def lastfm_similar_artists(artist: str, limit: int = 30) -> list[str]:
    """Return artists Last.fm considers similar to `artist` (names only)."""
    if not LASTFM_API_KEY:
        return []
    data = get_json(
        "https://ws.audioscrobbler.com/2.0/",
        params={"method": "artist.getSimilar", "artist": artist, "limit": limit,
                "api_key": LASTFM_API_KEY, "format": "json", "autocorrect": 1},
    )
    similar = (data or {}).get("similarartists", {}).get("artist", [])
    return [a["name"] for a in similar if a.get("name")]


# The Data API's videoEmbeddable filter reflects the uploader's embed setting
# but not the rights-holder blocks that music videos often carry, so a video it
# calls embeddable can still fail in the player with error 150. These ids were
# confirmed unplayable in a real embed; skip them so a rebuild can't bring them
# back. (Verify a suspect id by loading it in the web demo: a blocked one shows
# the "uploader doesn't allow" message instead of playing.)
YOUTUBE_BLOCKLIST = {
    "3mWbRB3Y4R8",  # Swedish House Mafia — Don't You Worry Child (error 150)
}


def youtube_video_id(artist: str, title: str) -> str | None:
    """Find an embeddable YouTube video id for the track (needs an API key)."""
    if not YOUTUBE_API_KEY:
        return None
    data = get_json(
        "https://www.googleapis.com/youtube/v3/search",
        params={"part": "snippet", "type": "video", "videoEmbeddable": "true",
                "maxResults": 1, "q": f"{artist} {title} official audio",
                "key": YOUTUBE_API_KEY},
    )
    if not data or not data.get("items"):
        return None
    vid = data["items"][0].get("id", {}).get("videoId")
    return None if vid in YOUTUBE_BLOCKLIST else vid


def cover_url(release_mbid: str | None) -> str | None:
    """Best-effort album cover from the Cover Art Archive (keyless)."""
    if not release_mbid:
        return None
    # Don't download the image; just point at the CAA front-cover endpoint.
    # (We probe it lightly so we don't store dead links.)
    data_head = get_json(f"https://coverartarchive.org/release/{release_mbid}")
    if not data_head or not data_head.get("images"):
        return None
    return f"https://coverartarchive.org/release/{release_mbid}/front-250"


# --------------------------------------------------------------------------- #
# Build one track
# --------------------------------------------------------------------------- #

def build_track(idx: int, artist: str, title: str, genre: str,
                rank_in_genre: int, verbose: bool = False) -> dict | None:
    """Enrich a single seed track into a full, schema-valid record."""
    mb = mb_lookup(artist, title)
    ab = ab_features_best(mb["candidate_mbids"])

    tempo = ab["tempo"] or GENRE_DEFAULT_TEMPO[genre]
    mood = ab["mood"] or GENRE_DEFAULT_MOOD[genre]
    year = mb["year"] or 2000
    chosen_mbid = ab["mbid"] or (mb["candidate_mbids"][0]
                                 if mb["candidate_mbids"] else None)

    popularity = lastfm_popularity(artist, title)
    if popularity is None:
        # Fallback proxy: earlier in a genre's seed list = more popular.
        popularity = max(45, 88 - rank_in_genre * 4)

    record = {
        "id": f"r{idx:03d}",
        "title": title,
        "artist": artist,
        "genre": genre,
        "tempo": int(tempo),
        "mood": mood,
        "year": int(year),
        "popularity": int(popularity),
        # extra fields for the web app (ignored by the loader/scoring):
        "mbid": chosen_mbid,
        "youtube_id": youtube_video_id(artist, title),
        "cover_url": cover_url(mb["release_mbid"]),
        "source": "enriched",
    }

    # Validate against the same Pydantic model the API uses; skip on failure.
    try:
        Track(**{k: record[k] for k in
                 ("id", "title", "artist", "genre", "tempo", "mood", "year",
                  "popularity")})
    except Exception as exc:
        if verbose:
            print(f"  ! skipped {artist} - {title}: {exc}")
        return None

    if verbose:
        src_t = "AB" if ab["tempo"] else "default"
        src_m = "AB" if ab["mood"] else "default"
        print(f"  + {record['id']} {artist} - {title} "
              f"[{genre}] tempo={tempo}({src_t}) mood={mood}({src_m}) "
              f"year={year} pop={popularity} yt={'y' if record['youtube_id'] else '-'}")
    return record


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def build_seeds(per_genre: int) -> list[tuple[str, str, str]]:
    """The hand-curated seeds plus, optionally, Last.fm chart tracks per genre.

    `per_genre` > 0 pulls that many top tracks for each genre from Last.fm,
    de-duplicated against the hand seeds, to grow the catalogue with real,
    popular (and thus better AcousticBrainz-covered) tracks.
    """
    seeds = list(SEED_TRACKS)
    seen = {(a.lower(), t.lower()) for a, t, _ in seeds}
    if per_genre > 0 and LASTFM_API_KEY:
        for genre in GENRE_LASTFM_TAG:
            for artist, title, g in lastfm_top_tracks(genre, per_genre):
                key = (artist.lower(), title.lower())
                if key not in seen:
                    seen.add(key)
                    seeds.append((artist, title, g))
    return seeds


def build_similarity_map(records: list[dict]) -> None:
    """Fetch Last.fm similar artists for every artist in the dataset and write
    app/data/artist_similarity.json (used for graded artist affinity)."""
    artists = sorted({r["artist"] for r in records})
    dataset_artists = {a.lower() for a in artists}
    sim: dict[str, list[str]] = {}
    useful = 0
    print(f"\nBuilding artist-similarity map for {len(artists)} artists...")
    for a in artists:
        similar = lastfm_similar_artists(a)
        if similar:
            sim[a] = similar
            if any(s.lower() in dataset_artists for s in similar):
                useful += 1
    SIMILARITY_FILE.write_text(json.dumps(sim, indent=2, ensure_ascii=False))
    print(f"Wrote similarity map: {len(sim)}/{len(artists)} artists have similar "
          f"lists, {useful} have at least one match inside the catalogue "
          f"-> {SIMILARITY_FILE.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich the NextTrack dataset.")
    parser.add_argument("--limit", type=int, default=0,
                        help="Only process the first N seed tracks (0 = all).")
    parser.add_argument("--per-genre", type=int, default=0,
                        help="Also pull this many top tracks per genre from "
                             "Last.fm to grow the catalogue (0 = hand seeds only).")
    parser.add_argument("--similar", action="store_true",
                        help="Also build the Last.fm artist-similarity map.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results but write no file.")
    parser.add_argument("--apply", action="store_true",
                        help="Merge real tracks into app/data/tracks.json "
                             "(backs up the original first). Default just "
                             "writes the preview file.")
    parser.add_argument("--no-cache", action="store_true",
                        help="Ignore the on-disk HTTP cache.")
    args = parser.parse_args()

    if args.no_cache:
        global _USE_CACHE
        _USE_CACHE = False

    seeds = build_seeds(args.per_genre)
    if args.limit:
        seeds = seeds[: args.limit]
    print(f"Enriching {len(seeds)} seed tracks "
          f"(Last.fm: {'on' if LASTFM_API_KEY else 'off'}, "
          f"YouTube: {'on' if YOUTUBE_API_KEY else 'off'})\n")

    genre_counts: dict[str, int] = {}
    records: list[dict] = []
    for i, (artist, title, genre) in enumerate(seeds, start=1):
        rank = genre_counts.get(genre, 0)
        genre_counts[genre] = rank + 1
        rec = build_track(i, artist, title, genre, rank, verbose=True)
        if rec:
            records.append(rec)

    print(f"\nBuilt {len(records)}/{len(seeds)} real tracks.")
    _print_coverage(records)

    if args.dry_run:
        print("\n(dry run — no file written)")
        return

    PREVIEW_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"\nWrote {len(records)} real tracks -> {PREVIEW_FILE.name}")

    if args.apply:
        _apply_merge(records)

    if args.similar:
        build_similarity_map(records)


def _print_coverage(records: list[dict]) -> None:
    if not records:
        return
    yt = sum(1 for r in records if r.get("youtube_id"))
    cov = sum(1 for r in records if r.get("cover_url"))
    print(f"Coverage: youtube_id {yt}/{len(records)}, "
          f"cover_url {cov}/{len(records)}")


def _apply_merge(records: list[dict]) -> None:
    """Rebuild tracks.json as (original curated tracks) + (enriched tracks).

    Rebuilding from the original curated base (backed up on first run) makes
    --apply idempotent: re-running with a different/larger catalogue replaces
    the enriched tracks cleanly instead of colliding with previous ids.
    """
    if BACKUP_FILE.exists():
        base = json.loads(BACKUP_FILE.read_text())
    else:
        base = json.loads(CURATED_FILE.read_text())
        BACKUP_FILE.write_text(json.dumps(base, indent=2, ensure_ascii=False))
        print(f"Backed up original curated dataset -> {BACKUP_FILE.name}")

    base_ids = {t["id"] for t in base}
    merged = list(base) + [r for r in records if r["id"] not in base_ids]
    CURATED_FILE.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    print(f"Merged dataset now has {len(merged)} tracks "
          f"({len(base)} curated + {len(merged) - len(base)} enriched) "
          f"-> {CURATED_FILE.name}")


if __name__ == "__main__":
    main()
