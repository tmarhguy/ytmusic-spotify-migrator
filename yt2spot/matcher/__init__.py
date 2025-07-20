"""Matching engine for YT2Spot."""

from yt2spot.matcher.decision import make_decision
from yt2spot.matcher.normalize import normalize_artist, normalize_title
from yt2spot.matcher.scoring import score_candidates
from yt2spot.matcher.search import search_spotify_tracks

__all__ = [
    "normalize_title",
    "normalize_artist",
    "search_spotify_tracks",
    "score_candidates",
    "make_decision",
]
