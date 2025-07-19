Below is an **ultra‑detailed, end‑to‑end specification** for your _YT2Spot_ project (import YouTube Music liked songs from a `.txt` export into Spotify). It goes beyond the earlier outline and drills into architecture, data flows, matching heuristics, error handling, quality metrics, extensibility, and delivery. Treat this as a combined **Product Requirements Doc (PRD) + Technical Design + Engineering Playbook + Future Roadmap**.

---

# 1. Vision & Value

**Goal:** Seamless, accurate, transparent migration of personal “Liked Songs” (and eventually playlists) from YouTube Music (offline-exported text) into a Spotify playlist—locally, privately, scriptable.

**Core Principles:**

1. **Accuracy First:** Maximize correct track matches; expose uncertainty.
2. **Transparency:** Clear logs for matched, skipped, ambiguous, fuzzy‑matched.
3. **Speed with Safety:** Reasonable throughput while respecting Spotify rate limits.
4. **Extensibility:** Modular so adding Apple Music / Deezer / Tidal later is trivial.
5. **Zero Cloud Dependence:** User runs locally; no external storage.
6. **Determinism (when desired):** Option for stable matching (idempotent reruns).

---

# 2. High-Level Use Cases

| Use Case                        | Actor              | Scenario                                               | Success Criteria                                             |
| ------------------------------- | ------------------ | ------------------------------------------------------ | ------------------------------------------------------------ |
| Import liked songs quickly      | User (default run) | `python yt2spot.py --input liked.txt`                  | Playlist created, majority of songs matched, summary printed |
| Re-run incremental update       | Power user         | Run again with same input after new likes appended     | Only new (unimported) songs added                            |
| Diagnostic / QA                 | User               | Run with `--dry-run`                                   | No playlist changes; full report of potential matches        |
| Manual approval                 | Picky user         | Run with `--interactive`                               | For ambiguous matches, user chooses final track              |
| Fuzzy improvement pass          | Analyst user       | Run with `--fuzzy --threshold 82`                      | Only matches above threshold accepted; rest logged           |
| Multi-playlist support (future) | Advanced           | Import separate `.txt` exports into separate playlists | Each file → distinct configured playlist                     |

---

# 3. Functional Requirements

### 3.1 Input Handling

- **Accepted Formats (Phase 1)**:

  - Plain lines: `Title - Artist`
  - Lines optionally annotated with YouTube Music extra: `Title - Artist (Official Video)` → must strip suffixes.

- **Normalization**:

  - Trim whitespace.
  - Remove trailing qualifiers: `(Official Video)`, `[Official Audio]`, `(Lyrics)`, `(feat. X)`, `(ft. X)` → store features separately for boosting search (optional advanced).

- **Validation**:

  - Reject lines missing delimiter `-` (log as `MALFORMED_LINE`).
  - Deduplicate identical `title|artist` pairs (configurable: keep first, or keep order duplicates to preserve counts).

### 3.2 Spotify Integration

- **Scopes**: `playlist-modify-public` or `playlist-modify-private` based on `--public/--private`.
- **Token Caching**: Local `.cache-yt2spot` via Spotipy; override path with `--cache-file`.
- **Playlist Strategy**:

  - Default name: `YT Music Liked Songs`
  - If exists:

    - Default: append only new tracks not already in playlist (idempotent).
    - With `--force-recreate`: archive (rename with timestamp) and create fresh.

- **Batching**: Add tracks in chunks of 100.
- **Retry**: Exponential backoff for transient `429` or network errors (max attempts configurable).

### 3.3 Matching Engine

1. **Primary Exact Search**: Query string pattern:

   ```
   track:"<clean_title>" artist:"<primary_artist>"
   ```

   Fallback to:

   ```
   "<clean_title>" "<primary_artist>"
   ```

2. **Candidate Selection**:

   - Pull top N (configurable, default 5) from Spotify search.

3. **Scoring Pipeline** (composable):

   - **Base Title Similarity** (Normalized Levenshtein / token ratio via `rapidfuzz`).
   - **Artist Similarity** (handle & unify featured artist lists).
   - **Penalty Adjustments**:

     - Year difference (if available & > 5 years).
     - Explicit vs clean duplicates (± small bias).
     - Live / remaster / acoustic mismatch penalty unless input line tagged similarly.

   - **Boosts**:

     - High track popularity (within reason, only if similarity ≥ threshold).
     - Matched featured artists.

4. **Final Score** formula (example, configurable):

   ```
   score = 0.55*title_sim + 0.30*artist_sim + 0.05*feature_match + 0.05*popularity_norm - penalties
   ```

5. **Decision Thresholds**:

   - `>= hard_accept_threshold` (e.g. 0.87): auto-accept.
   - `< reject_threshold` (e.g. 0.60): auto-reject → log unmatched.
   - Between thresholds:

     - If `--interactive`: ask user (show top candidates with preview name/duration).
     - Else: treat as unmatched or (if `--fuzzy`) accept best if above fuzzy minimal threshold.

6. **Edge Cases**:

   - Non-Latin scripts: rely on Spotify Unicode; no transliteration first pass.
   - All-caps lines → casefold.
   - Featuring notation: parse `(feat. X)`, `feat. X`, `ft. X`, `Feat.`—split into base_title + features array.

### 3.4 Logging & Reporting

- **Real-time Console**:

  - Progress bar: `Matched: X | Unmatched: Y | Pending: Z`
  - Warnings for ambiguous matches.

- **Artifacts**:

  - `unmatched.txt`
  - `ambiguous.csv` (fields: original_title, original_artist, candidate_title, candidate_artist, score, popularity, decision)
  - `session_summary.json` (timestamp, counts, threshold settings, version)
  - Optional `matched.csv` for auditing.

- **Verbosity Levels**:

  - `--quiet`, default (info), `--debug` (raw JSON of top candidates).

### 3.5 Configuration Precedence

1. CLI flags
2. Environment variables (`YT2SPOT_*`)
3. `.yt2spot.toml` (project root or user home)
4. Built-in defaults

### 3.6 Dry Run

- Executes full matching pipeline without playlist creation or modification.
- Outputs simulated actions + logs.

### 3.7 Incremental Mode

- Determine existing Spotify playlist track IDs.
- Skip songs whose selected track already exists.
- Hash input line (`sha1(normalized_title|artist)`) to maintain optional local state file for faster re-runs.

### 3.8 Interactive Mode

- For ambiguous lines: display:

  ```
  [Original]  Lose Yourself - Eminem
  (1) Lose Yourself - Eminem (4:26) score=0.93
  (2) Lose Yourself - Eminem - Live (4:30) score=0.81
  (s) Skip  (a) Accept #1  (2) Accept #2  (q) Quit
  >
  ```

---

# 4. Non-Functional Requirements

| Aspect              | Target                                                    |
| ------------------- | --------------------------------------------------------- |
| **Performance**     | 500 tracks in < 5 min (network dependent)                 |
| **Accuracy**        | >90% correct matches on clean English dataset             |
| **Resilience**      | Recover from mid-run 429 by retry/backoff                 |
| **Portability**     | Runs on Windows/macOS/Linux with Python 3.10+             |
| **Maintainability** | Clear module boundaries; type hints (mypy clean)          |
| **Observability**   | Structured logs (JSON mode optional)                      |
| **Security**        | Credentials never written to logs; `.env` in `.gitignore` |

---

# 5. Architecture & Module Layout

```
yt2spot/
  __init__.py
  cli.py                # argparse entrypoint
  config.py             # load & merge config sources
  input_parser.py       # read & normalize lines
  models.py             # dataclasses: SongInput, MatchCandidate, MatchDecision
  spotify_client.py     # wrapper around spotipy; caching, retries
  matcher/
      __init__.py
      normalize.py      # title/artist normalization
      search.py         # queries & gather candidates
      scoring.py        # scoring algorithm
      decision.py       # threshold logic
  playlist.py           # create/find/update playlist
  incremental.py        # track caching & dedupe logic
  logging_utils.py      # structured + file log handlers
  interactive.py        # user prompt flows
  report.py             # summary & artifact writers
  version.py            # semantic version string
tests/
  ...
scripts/
  export_requirements.sh
README.md
pyproject.toml
```

---

# 6. Data Models (Python `dataclasses`)

```python
@dataclass
class SongInput:
    raw_line: str
    title: str
    artist_primary: str
    features: list[str]
    normalized_key: str  # title|artist normalized

@dataclass
class MatchCandidate:
    spotify_id: str
    title: str
    artists: list[str]
    popularity: int
    duration_ms: int
    score_components: dict[str, float]
    final_score: float

@dataclass
class MatchDecision:
    input_song: SongInput
    chosen: Optional[MatchCandidate]
    status: Literal["ACCEPT","SKIP","UNMATCHED","AMBIGUOUS"]
    reason: str
```

---

# 7. Matching Heuristics Deep Dive

**Normalization Steps**:

1. Casefold
2. Remove punctuation except alphanumerics and spaces
3. Replace multiple spaces with single
4. Strip content inside `()` or `[]` if matches label patterns (configurable lists)

**Similarity Functions**:

- Token set ratio (RapidFuzz) for robustness to word order.
- Partial ratio for possible truncated forms.
- Weighted combination:

  ```
  title_sim = max(token_set_ratio, partial_ratio)
  artist_sim = token_ratio(artist_primary, candidate_main_artist)
  ```

**Penalties**:

- If candidate title includes “live” and input doesn’t: -0.04
- If includes “remaster” and input absent that token: -0.02
- Duration delta > 15%: -0.03
  **Boosts**:
- Popularity percentile: up to +0.03
- Feature alignment: +0.02 if all listed features appear among candidate artists.

Threshold tuning can be in a YAML file.

---

# 8. Error Handling Policy

| Failure Point             | Strategy                                           |
| ------------------------- | -------------------------------------------------- |
| Network timeout           | Retry up to N (default 3) with exponential backoff |
| 401 Unauthorized          | Refresh token (Spotipy handles) else abort         |
| 429 Rate Limited          | Respect `Retry-After` header + jitter              |
| Malformed line            | Log & continue; increment `malformed_count`        |
| No candidates             | Log UNMATCHED                                      |
| Playlist creation failure | Abort gracefully with partial summary              |
| Write permissions (logs)  | Fallback to temp directory                         |

---

# 9. CLI Specification (Argparse)

| Flag                       | Description                   | Default                |
| -------------------------- | ----------------------------- | ---------------------- |
| `--input PATH`             | Input text file               | Required               |
| `--playlist NAME`          | Playlist name                 | "YT Music Liked Songs" |
| `--public / --private`     | Visibility toggle             | public                 |
| `--dry-run`                | Simulate                      | False                  |
| `--fuzzy`                  | Enable fuzzy fallback         | False                  |
| `--hard-threshold FLOAT`   | Accept threshold              | 0.87                   |
| `--reject-threshold FLOAT` | Reject threshold              | 0.60                   |
| `--fuzzy-threshold FLOAT`  | Fuzzy minimal acceptance      | 0.80                   |
| `--limit N`                | Cap number of input songs     | None                   |
| `--interactive`            | Prompt user for ambiguous     | False                  |
| `--force-recreate`         | Rebuild playlist from scratch | False                  |
| `--log-dir PATH`           | Output logs directory         | `./logs/<timestamp>`   |
| `--cache-file PATH`        | Spotify token cache path      | `.cache-yt2spot`       |
| `--json-logs`              | Structured JSON logs          | False                  |
| `--quiet`                  | Minimal output                | False                  |
| `--debug`                  | Verbose internal state        | False                  |
| `--version`                | Print version                 | -                      |

---

# 10. Configuration File Example (`.yt2spot.toml`)

```toml
[matching]
hard_threshold = 0.87
reject_threshold = 0.60
fuzzy_threshold = 0.80
max_candidates = 5

[playlists]
default_name = "YT Music Liked Songs"
force_recreate = false

[logging]
json = false
log_dir = "logs"

[auth]
client_id = ""
client_secret = ""
redirect_uri = "http://localhost:8888/callback"
```

---

# 11. Summary Metrics (Printed at End)

Example:

```
=== YT2Spot Summary ===
Total input lines: 742
Valid songs parsed: 735
Matched (auto): 648
Matched (interactive): 22
Fuzzy accepted: 34
Unmatched: 31
Skipped/Rejected: 0
Malformed lines: 7
Existing tracks skipped: 112
Playlist name: YT Music Liked Songs
Playlist URL: https://open.spotify.com/playlist/XXXX
Duration: 00:04:37
Accuracy (accepted / valid): 704 / 735 = 95.8%
Artifacts:
  logs/session_summary.json
  logs/unmatched.txt
  logs/ambiguous.csv
```

---

# 12. Testing Strategy

### 12.1 Unit Tests

- `input_parser_test.py`
- `normalize_test.py`
- `scoring_test.py`
- `threshold_logic_test.py`

### 12.2 Integration Tests

- Mock Spotify responses (using `responses` library).
- End-to-end dry run.

### 12.3 Data-driven Tests

- Fixture sets: normal titles, live versions, remasters, non-English.

### 12.4 Regression Tests

- Lock expected decisions for a curated 50‑song test file.

### 12.5 Performance Test

- Synthetic 1500-line input file; record throughput.

---

# 13. Tooling & Quality Gates

| Tool         | Purpose                        |
| ------------ | ------------------------------ |
| `ruff`       | Lint + style                   |
| `black`      | Formatting                     |
| `mypy`       | Type checking                  |
| `pytest`     | Test runner                    |
| `coverage`   | Ensure ≥85% core modules       |
| `pre-commit` | Enforce quality before commits |

---

# 14. Distribution & Packaging

1. **`pyproject.toml`** with Poetry or PEP 621 metadata.
2. Entry point:

   ```toml
   [project.scripts]
   yt2spot = "yt2spot.cli:main"
   ```

3. Publish to PyPI (`pip install yt2spot`).
4. Optional: Build standalone executables via `pyinstaller`.
5. Dockerfile:

   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   COPY . .
   RUN pip install .
   ENTRYPOINT ["yt2spot"]
   ```

---

# 15. Documentation Outline (README.md)

1. **Intro / Badge Row**
2. Features
3. Install
4. Quick Start
5. Obtaining Spotify Credentials (screenshots)
6. Input File Format + Generation Tips
7. Matching Algorithm & Tuning
8. CLI Reference
9. Examples
10. Troubleshooting (auth, 429, unmatched)
11. Roadmap
12. Contributing
13. License (MIT)
14. Disclaimer

---

# 16. Roadmap (Versioned)

| Version | Milestones                                  |
| ------- | ------------------------------------------- |
| v0.1.0  | MVP: input → playlist, basic logging        |
| v0.2.0  | Fuzzy scoring, unmatched artifacts          |
| v0.3.0  | Interactive mode, incremental dedupe        |
| v0.4.0  | Config file + environment overrides         |
| v0.5.0  | Multi-threaded search batching              |
| v0.6.0  | Additional providers abstraction layer      |
| v0.7.0  | GUI wrapper (Tk / minimal web UI)           |
| v1.0.0  | Hardening, full test coverage, PyPI release |

---

# 17. Extension Layer (Future Multi-Service Design)

Introduce abstraction:

```python
class MusicProvider(Protocol):
    def search(self, title: str, artist: str) -> list[TrackMeta]: ...
    def create_playlist(self, name: str, public: bool) -> PlaylistMeta: ...
    def add_tracks(self, playlist_id: str, track_ids: list[str]) -> None: ...
```

Implementations: `SpotifyProvider`, future `AppleMusicProvider`, `DeezerProvider`.

---

# 18. Privacy & Security Considerations

- Never log raw client secret.
- Offer `--redact` mode: redacts tokens from debug traces.
- Encourage user to store secrets in environment variables (not committed).
- Provide `.env.example` and `.gitignore` entry for `.env`.

---

# 19. Internationalization (Optional Later)

- Extract all CLI prompts to a small `messages.json`.
- Support `--lang` for prompt localization.

---

# 20. Operational Edge Cases & Mitigations

| Edge Case                                       | Mitigation                                                     |
| ----------------------------------------------- | -------------------------------------------------------------- |
| Playlist hits size limits (≈10k tracks)         | Detect size & create rollover playlist `... (Part 2)`          |
| Duplicate lines representing different versions | Maintain a variant suffix if user enables `--allow-duplicates` |
| Long titles with pipes or unusual delimiters    | Fallback natural language search query                         |
| Network offline mid-run                         | Save checkpoint `checkpoint.json`; resume with `--resume`      |

---

# 21. Sample Skeleton (Minimal)

```python
# cli.py
def main():
    args = parse_args()
    config = load_config(args)
    songs = parse_input(config.input_path, limit=config.limit)
    spotify = SpotifyClient(config.auth)
    playlist = ensure_playlist(spotify, config)
    decisions = match_and_decide(songs, spotify, config)
    if not config.dry_run:
        commit_playlist(spotify, playlist, decisions)
    write_reports(decisions, config)
    print_summary(decisions, playlist, config)
```

---

# 22. Quality / Success Metrics (Post Release)

- **Adoption:** Stars on GitHub, issues opened.
- **Accuracy telemetry (opt-in)**: Ratio matched vs unmatched (anonymized).
- **User Feedback**: “Ambiguous pool size” trending downward after scoring tweaks.

---

# 23. Example Threshold Tuning Session

1. Run with `--dry-run --debug --limit 300` generating `ambiguous.csv`.
2. Manually label 50 ambiguous lines (correct candidate index).
3. Adjust scoring weights; re-run; target reduction of ambiguous bucket by ≥30% without increasing false acceptances.

---

# 24. Developer Onboarding Steps

1. Clone repo; run `poetry install` (or `pip install -e .[dev]`).
2. Copy `.env.example` → `.env` & fill Spotify creds.
3. Run `make test` (or `tox`).
4. Try sample file: `python -m yt2spot.cli --input sample_likes.txt --dry-run`.

---

# 25. Potential “Wow” Enhancements (Later)

- **Similarity Explanation Mode** (`--explain`): prints component scores per track.
- **Heuristic Learning**: store historical accepted decisions to bias future scoring toward certain canonical versions.
- **Audio Fingerprint Support**: If user supplies local audio (ambitious).
- **Web Dashboard**: Localhost UI showing progress in real-time (FastAPI + SSE).

---

# 26. Risks & Mitigations

| Risk                             | Impact            | Mitigation                                              |
| -------------------------------- | ----------------- | ------------------------------------------------------- |
| Spotify API schema changes       | Breakage          | Pin `spotipy` version; integration tests                |
| Over-aggressive fuzzy accept     | Incorrect matches | Conservative default thresholds; dry-run recommendation |
| User confusion about credentials | Setup friction    | README with screenshots & troubleshooting section       |
| Rate limits for large libraries  | Slow or abort     | Backoff + progress persistence                          |

---

# 27. Licensing & Compliance

- **License**: MIT (allows forks & contributions).
- **Dependency Licenses**: Ensure `spotipy`, `rapidfuzz`, `tqdm` all permissive (they are).
- Provide `LICENSE` + `NOTICE`.

---

# 28. Example `session_summary.json`

```json
{
  "timestamp": "2025-07-19T19:42:11Z",
  "input_file": "liked_songs.txt",
  "total_lines": 742,
  "parsed_valid": 735,
  "matched_auto": 648,
  "matched_interactive": 0,
  "fuzzy_accepted": 34,
  "unmatched": 31,
  "malformed": 7,
  "skipped_existing": 112,
  "thresholds": {
    "hard": 0.87,
    "reject": 0.6,
    "fuzzy": 0.8
  },
  "runtime_seconds": 277,
  "playlist": {
    "id": "xyz123",
    "name": "YT Music Liked Songs",
    "public": true,
    "final_track_count": 704
  },
  "version": "0.3.0"
}
```

---

# 29. Minimal Contribution Guidelines

- Branch naming: `feature/<slug>`, `fix/<slug>`
- PR Template:

  - **Summary**
  - **Changes**
  - **Testing**
  - **Screenshots (if CLI UI changes)**
  - **Checklist** (lint, tests, docs updated)

---

# 30. Immediate Implementation Order (Sprint 0 → 2)

**Sprint 0 (Setup)**
Repo scaffold, pyproject, lint config, basic CLI, Spotify auth test.

**Sprint 1 (Core)**
Input parsing, basic search + accept (no fuzzy), playlist creation, batching, summary.

**Sprint 2 (Quality)**
Fuzzy scoring, logging artifacts, interactive mode, config system, tests.

(Then iterate.)

---

**That’s the exhaustive blueprint.**
If you want, next I can:

1. Generate the initial code skeleton, or
2. Write a polished README draft, or
3. Craft the matching algorithm implementation first.

Just tell me which step you want to execute now, and I’ll produce it. 🚀
