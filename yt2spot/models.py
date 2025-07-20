"""Data models for YT2Spot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

MatchStatus = Literal["ACCEPT", "SKIP", "UNMATCHED", "AMBIGUOUS"]


@dataclass
class SongInput:
    """Represents a parsed song from the input file."""

    title: str
    artist: str
    album: str = ""
    duration: str = ""
    source_line: int = 0
    normalized_key: str = ""  # Will be set after normalization

    def __post_init__(self) -> None:
        """Generate normalized key if not provided."""
        if not self.normalized_key:
            # Basic normalization - will be enhanced by normalize.py
            self.normalized_key = f"{self.title.lower()}|{self.artist.lower()}"

    @property
    def artist_primary(self) -> str:
        """Get primary artist for backwards compatibility."""
        return self.artist

    @property
    def raw_line(self) -> str:
        """Get source line for backwards compatibility."""
        return f"Line {self.source_line}: {self.title} - {self.artist}"


@dataclass
class MatchCandidate:
    """Represents a potential Spotify match for a song."""

    spotify_id: str
    title: str
    artist: str  # Primary artist
    all_artists: str  # All artists as comma-separated string
    album: str
    duration_ms: int
    popularity: int
    preview_url: str | None = None
    spotify_url: str = ""

    # Scoring fields
    match_score: float = 0.0
    title_score: float = 0.0
    artist_score: float = 0.0
    album_score: float = 0.0
    search_query: str = ""

    @property
    def primary_artist(self) -> str:
        """Get the primary (first) artist."""
        return self.artist

    @property
    def all_artists_str(self) -> str:
        """Get all artists as a comma-separated string."""
        return self.all_artists

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
    chosen_candidate: MatchCandidate | None = None
    decision: str = "no_candidates"  # auto_accept, manual_accept, auto_reject, manual_reject, skipped, no_candidates
    confidence: float = 0.0
    reason: str = ""
    all_candidates: list[MatchCandidate] = field(default_factory=list)

    @property
    def is_matched(self) -> bool:
        """Check if the song was successfully matched."""
        return (
            self.decision in ["auto_accept", "manual_accept"]
            and self.chosen_candidate is not None
        )


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
