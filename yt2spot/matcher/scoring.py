"""
Scoring algorithm for track matching using fuzzy string matching.
"""


from rapidfuzz import fuzz
from rich.console import Console

from yt2spot.matcher.normalize import normalize_artist, normalize_title
from yt2spot.models import MatchCandidate, SessionConfig, SongInput

console = Console()


def score_candidates(
    song: SongInput, candidates: list[MatchCandidate], config: SessionConfig
) -> list[MatchCandidate]:
    """
    Score and sort match candidates based on similarity to input song.

    Args:
        song: Input song to match against
        candidates: List of Spotify track candidates
        config: Session configuration with scoring thresholds

    Returns:
        List of candidates sorted by match score (descending)
    """
    if not candidates:
        return []

    # Normalize input song fields once
    input_title_norm = normalize_title(song.title)
    input_artist_norm = normalize_artist(song.artist)
    input_album_norm = normalize_title(song.album) if song.album else ""

    scored_candidates = []

    for candidate in candidates:
        # Normalize candidate fields
        candidate_title_norm = normalize_title(candidate.title)
        candidate_artist_norm = normalize_artist(candidate.artist)
        candidate_album_norm = normalize_title(candidate.album)

        # Calculate individual scores
        title_score = calculate_title_score(input_title_norm, candidate_title_norm)
        artist_score = calculate_artist_score(
            input_artist_norm, candidate_artist_norm, candidate.all_artists
        )
        album_score = calculate_album_score(input_album_norm, candidate_album_norm)

        # Calculate weighted overall score
        overall_score = calculate_weighted_score(
            title_score, artist_score, album_score, candidate.popularity
        )

        # Set the score on the candidate
        candidate.match_score = overall_score
        candidate.title_score = title_score
        candidate.artist_score = artist_score
        candidate.album_score = album_score

        scored_candidates.append(candidate)

    # Sort by match score (descending)
    scored_candidates.sort(key=lambda c: c.match_score, reverse=True)

    return scored_candidates


def calculate_title_score(input_title: str, candidate_title: str) -> float:
    """Calculate title similarity score."""
    if not input_title or not candidate_title:
        return 0.0

    # Use multiple fuzzy matching algorithms and take the best
    ratio = fuzz.ratio(input_title, candidate_title) / 100.0
    partial_ratio = fuzz.partial_ratio(input_title, candidate_title) / 100.0
    token_sort_ratio = fuzz.token_sort_ratio(input_title, candidate_title) / 100.0
    token_set_ratio = fuzz.token_set_ratio(input_title, candidate_title) / 100.0

    # Take the maximum of all methods
    return max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)


def calculate_artist_score(
    input_artist: str, primary_artist: str, all_artists: str
) -> float:
    """Calculate artist similarity score."""
    if not input_artist:
        return 0.0

    scores = []

    # Score against primary artist
    if primary_artist:
        primary_score = fuzz.token_set_ratio(input_artist, primary_artist) / 100.0
        scores.append(primary_score)

    # Score against all artists (for collaborations)
    if all_artists and all_artists != primary_artist:
        all_artists_score = fuzz.token_set_ratio(input_artist, all_artists) / 100.0
        scores.append(all_artists_score)

    # Check if input artist appears as a substring in all_artists
    if all_artists and input_artist.lower() in all_artists.lower():
        scores.append(0.9)  # High score for substring match

    return max(scores) if scores else 0.0


def calculate_album_score(input_album: str, candidate_album: str) -> float:
    """Calculate album similarity score."""
    if not input_album or not candidate_album:
        return 0.5  # Neutral score if no album info

    # Handle common single/EP patterns
    if input_album.lower() in ["single", "ep", ""] or candidate_album.lower() in [
        "single",
        "ep",
        "",
    ]:
        return 0.7  # Moderate score for singles

    # Use token-based matching for albums (handles reissues, deluxe editions)
    return fuzz.token_set_ratio(input_album, candidate_album) / 100.0


def calculate_weighted_score(
    title_score: float, artist_score: float, album_score: float, popularity: int
) -> float:
    """
    Calculate weighted overall match score.

    Weights:
    - Title: 50% (most important)
    - Artist: 35% (very important)
    - Album: 10% (less important, often missing/different)
    - Popularity: 5% (tiebreaker)
    """
    # Normalize popularity (0-100) to 0-1
    popularity_norm = popularity / 100.0 if popularity else 0.0

    weighted_score = (
        title_score * 0.50
        + artist_score * 0.35
        + album_score * 0.10
        + popularity_norm * 0.05
    )

    return weighted_score


def is_good_match(candidate: MatchCandidate, config: SessionConfig) -> bool:
    """Check if a candidate is a good match based on thresholds."""
    return candidate.match_score >= config.hard_threshold


def is_acceptable_match(candidate: MatchCandidate, config: SessionConfig) -> bool:
    """Check if a candidate is an acceptable match (not rejected)."""
    return candidate.match_score >= config.reject_threshold


def get_match_quality(score: float) -> tuple[str, str]:
    """
    Get match quality description and color for display.

    Returns:
        Tuple of (quality_text, color_code)
    """
    if score >= 0.90:
        return ("Excellent", "bright_green")
    elif score >= 0.80:
        return ("Good", "green")
    elif score >= 0.70:
        return ("Fair", "yellow")
    elif score >= 0.60:
        return ("Poor", "orange1")
    else:
        return ("Very Poor", "red")
