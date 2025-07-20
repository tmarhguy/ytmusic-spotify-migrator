"""Data models for YT2Spot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

MatchStatus = Literal["ACCEPT", "SKIP", "UNMATCHED", "AMBIGUOUS"]


@dataclass
class SongInput:
    """Represents a parsed song from the input file."""

    raw_line: str
    title: str
    artist_primary: str
    features: list[str] = field(default_factory=list)
    normalized_key: str = ""  # Will be set after normalization

    def __post_init__(self) -> None:
        """Generate normalized key if not provided."""
        if not self.normalized_key:
            # Basic normalization - will be enhanced by normalize.py
            self.normalized_key = f"{self.title.lower()}|{self.artist_primary.lower()}"


@dataclass
class MatchCandidate:
    """Represents a potential Spotify match for a song."""

    spotify_id: str
    title: str
    artists: list[str]
    popularity: int
    duration_ms: int
    explicit: bool = False
    album_name: str = ""
    release_date: str = ""
    preview_url: str | None = None
    score_components: dict[str, float] = field(default_factory=dict)
    final_score: float = 0.0

    @property
    def primary_artist(self) -> str:
        """Get the primary (first) artist."""
        return self.artists[0] if self.artists else ""

    @property
    def all_artists_str(self) -> str:
        """Get all artists as a comma-separated string."""
        return ", ".join(self.artists)

    @property
    def duration_str(self) -> str:
        """Get duration as a formatted string (MM:SS)."""
        minutes = self.duration_ms // 60000
        seconds = (self.duration_ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"


@dataclass
class MatchDecision:
    """Represents the final decision for a song match."""

    input_song: SongInput
    chosen: MatchCandidate | None = None
    status: MatchStatus = "UNMATCHED"
    reason: str = ""
    all_candidates: list[MatchCandidate] = field(default_factory=list)
    user_decision: bool = False  # True if user made manual choice

    @property
    def is_matched(self) -> bool:
        """Check if the song was successfully matched."""
        return self.status == "ACCEPT" and self.chosen is not None


@dataclass
class PlaylistMeta:
    """Metadata about a Spotify playlist."""

    id: str
    name: str
    public: bool
    description: str = ""
    track_count: int = 0
    url: str = ""
    existing_track_ids: set[str] = field(default_factory=set)


@dataclass
class SessionConfig:
    """Configuration for a YT2Spot session."""

    # Input/Output
    input_path: str
    playlist_name: str = "YT Music Liked Songs"
    log_dir: str = "logs"
    cache_file: str = ".cache-yt2spot"

    # Matching thresholds
    hard_threshold: float = 0.87
    reject_threshold: float = 0.60
    fuzzy_threshold: float = 0.80
    max_candidates: int = 5

    # Behavior flags
    dry_run: bool = False
    interactive: bool = False
    fuzzy: bool = False
    public_playlist: bool = True
    force_recreate: bool = False

    # Limits and controls
    limit: int | None = None
    verbose: bool = False
    quiet: bool = False
    debug: bool = False
    json_logs: bool = False

    # Spotify auth
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8888/callback"


@dataclass
class SessionSummary:
    """Summary statistics for a completed session."""

    total_lines: int = 0
    parsed_valid: int = 0
    matched_auto: int = 0
    matched_interactive: int = 0
    fuzzy_accepted: int = 0
    unmatched: int = 0
    malformed: int = 0
    skipped_existing: int = 0

    runtime_seconds: float = 0.0
    playlist_id: str = ""
    playlist_name: str = ""
    playlist_url: str = ""

    @property
    def total_matched(self) -> int:
        """Total successfully matched songs."""
        return self.matched_auto + self.matched_interactive + self.fuzzy_accepted

    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy as percentage of valid songs matched."""
        if self.parsed_valid == 0:
            return 0.0
        return (self.total_matched / self.parsed_valid) * 100
