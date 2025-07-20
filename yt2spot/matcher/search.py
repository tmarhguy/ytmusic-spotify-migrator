"""
Spotify search functionality with intelligent query construction.
"""


from rich.console import Console

from yt2spot.matcher.normalize import normalize_artist, normalize_title
from yt2spot.models import MatchCandidate, SessionConfig, SongInput
from yt2spot.spotify_client import SpotifyClient

console = Console()


def search_spotify_tracks(
    song: SongInput, spotify_client: SpotifyClient, config: SessionConfig
) -> list[MatchCandidate]:
    """
    Search Spotify for track candidates using multiple query strategies.

    Args:
        song: Input song to search for
        spotify_client: Authenticated Spotify client
        config: Session configuration

    Returns:
        List of match candidates sorted by relevance
    """
    all_candidates = []
    used_queries = set()

    # Strategy 1: Exact search with normalized fields
    normalized_title = normalize_title(song.title)
    normalized_artist = normalize_artist(song.artist)

    queries = [
        # Most specific to least specific
        f'track:"{normalized_title}" artist:"{normalized_artist}"',
        f'"{normalized_title}" "{normalized_artist}"',
        f"{normalized_title} {normalized_artist}",
        f'track:"{normalized_title}"',
        f"{normalized_title}",
    ]

    # Add album-specific queries if album is available
    if song.album and song.album.strip():
        normalized_album = normalize_title(song.album)  # Reuse title normalization
        album_queries = [
            f'track:"{normalized_title}" artist:"{normalized_artist}" album:"{normalized_album}"',
            f'"{normalized_title}" "{normalized_artist}" "{normalized_album}"',
        ]
        queries = album_queries + queries

    for query in queries:
        if query in used_queries:
            continue
        used_queries.add(query)

        try:
            candidates = spotify_client.search_tracks(
                query, limit=config.max_candidates
            )
            if candidates:
                # Tag candidates with the search strategy used
                for candidate in candidates:
                    candidate.search_query = query
                all_candidates.extend(candidates)

                # If we get good results from specific queries, don't need broader ones
                if len(candidates) >= config.max_candidates and "track:" in query:
                    break

        except Exception as e:
            console.print(
                f"[yellow]Warning:[/yellow] Search failed for query '{query}': {e}"
            )
            continue

    # Remove duplicates while preserving order
    seen_ids = set()
    unique_candidates = []
    for candidate in all_candidates:
        if candidate.spotify_id not in seen_ids:
            seen_ids.add(candidate.spotify_id)
            unique_candidates.append(candidate)

    # Limit to max candidates
    return unique_candidates[: config.max_candidates]


def build_search_query(song: SongInput, strategy: str = "balanced") -> str:
    """
    Build a Spotify search query for a song using different strategies.

    Args:
        song: Input song to search for
        strategy: Search strategy ("exact", "balanced", "broad")

    Returns:
        Formatted search query string
    """
    normalized_title = normalize_title(song.title)
    normalized_artist = normalize_artist(song.artist)

    if strategy == "exact":
        # Most restrictive search
        query = f'track:"{normalized_title}" artist:"{normalized_artist}"'
    elif strategy == "balanced":
        # Balanced approach with quotes for phrases
        query = f'"{normalized_title}" "{normalized_artist}"'
    elif strategy == "broad":
        # Broadest search without quotes
        query = f"{normalized_title} {normalized_artist}"
    else:
        raise ValueError(f"Unknown search strategy: {strategy}")

    # Add album if available and strategy allows
    if song.album and song.album.strip() and strategy in ["exact", "balanced"]:
        normalized_album = normalize_title(song.album)
        if strategy == "exact":
            query += f' album:"{normalized_album}"'
        else:
            query += f' "{normalized_album}"'

    return query
