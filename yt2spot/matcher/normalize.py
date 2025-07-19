"""Text normalization functions for song matching."""

import re
import string
from typing import List, Tuple


# Common patterns to remove from song titles
TITLE_CLEANUP_PATTERNS = [
    r'\(Official\s+Video\)',
    r'\(Official\s+Audio\)',
    r'\[Official\s+Video\]',
    r'\[Official\s+Audio\]',
    r'\(Lyrics?\)',
    r'\[Lyrics?\]',
    r'\(HD\)',
    r'\[HD\]',
    r'\(4K\)',
    r'\[4K\]',
    r'\(Visualizer\)',
    r'\[Visualizer\]',
    r'\(Music\s+Video\)',
    r'\[Music\s+Video\]',
]

# Feature patterns to extract and normalize
FEATURE_PATTERNS = [
    r'\(feat\.?\s+([^)]+)\)',
    r'\(ft\.?\s+([^)]+)\)',
    r'\(featuring\s+([^)]+)\)',
    r'feat\.?\s+([^(\[]+)',
    r'ft\.?\s+([^(\[]+)',
    r'featuring\s+([^(\[]+)',
]


def normalize_title(title: str) -> Tuple[str, List[str]]:
    """
    Normalize a song title and extract featured artists.
    
    Returns:
        Tuple of (normalized_title, featured_artists)
    """
    # Store original for reference
    original = title.strip()
    normalized = original
    features = []
    
    # Extract featured artists first
    for pattern in FEATURE_PATTERNS:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            feature_text = match.group(1).strip()
            # Split multiple features (e.g., "Artist1 & Artist2")
            feature_artists = re.split(r'[&,]|and', feature_text, flags=re.IGNORECASE)
            features.extend([f.strip() for f in feature_artists if f.strip()])
            # Remove the feature text from title
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
    
    # Remove common YouTube/streaming qualifiers
    for pattern in TITLE_CLEANUP_PATTERNS:
        normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
    
    # Basic text normalization
    normalized = normalized.strip()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove trailing/leading punctuation except essential ones
    normalized = normalized.strip(' -()[]')
    
    return normalized, features


def normalize_artist(artist: str) -> str:
    """
    Normalize an artist name for matching.
    """
    normalized = artist.strip()
    
    # Handle "The" prefix - move to end for better matching
    if normalized.lower().startswith('the '):
        base = normalized[4:]
        if base:  # Only if there's something after "The"
            normalized = f"{base}, The"
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized.strip()


def create_search_key(title: str, artist: str) -> str:
    """
    Create a normalized key for deduplication and caching.
    """
    # Basic normalization for key creation
    title_clean = title.lower().strip()
    artist_clean = artist.lower().strip()
    
    # Remove punctuation for key
    title_clean = title_clean.translate(str.maketrans('', '', string.punctuation))
    artist_clean = artist_clean.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra spaces
    title_clean = re.sub(r'\s+', ' ', title_clean).strip()
    artist_clean = re.sub(r'\s+', ' ', artist_clean).strip()
    
    return f"{title_clean}|{artist_clean}"


def similarity_normalize(text: str) -> str:
    """
    Aggressive normalization for similarity comparison.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove all punctuation and special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_year(text: str) -> int | None:
    """
    Extract a 4-digit year from text if present.
    """
    match = re.search(r'\b(19|20)\d{2}\b', text)
    if match:
        return int(match.group())
    return None


def is_live_version(title: str) -> bool:
    """Check if a title indicates a live version."""
    live_indicators = [
        'live', 'concert', 'tour', 'acoustic', 'unplugged',
        'session', 'performance', 'mtv', 'radio'
    ]
    title_lower = title.lower()
    return any(indicator in title_lower for indicator in live_indicators)


def is_remix_version(title: str) -> bool:
    """Check if a title indicates a remix."""
    remix_indicators = ['remix', 'mix', 'edit', 'version', 'rework']
    title_lower = title.lower()
    return any(indicator in title_lower for indicator in remix_indicators)


def is_remaster(title: str) -> bool:
    """Check if a title indicates a remaster."""
    remaster_indicators = ['remaster', 'remastered', 'anniversary', 'deluxe']
    title_lower = title.lower()
    return any(indicator in title_lower for indicator in remaster_indicators)
