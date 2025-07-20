"""Tests for text normalization functions."""

from yt2spot.matcher.normalize import (
    create_search_key,
    is_live_version,
    is_remaster,
    is_remix_version,
    normalize_artist,
    normalize_title,
)


class TestNormalizeTitle:
    """Test title normalization."""

    def test_basic_normalization(self):
        """Test basic title normalization."""
        title, features = normalize_title("Hotel California - Eagles")
        assert title == "Hotel California - Eagles"
        assert features == []

    def test_official_video_removal(self):
        """Test removal of (Official Video) tags."""
        title, features = normalize_title("Bohemian Rhapsody (Official Video)")
        assert title == "Bohemian Rhapsody"
        assert features == []

    def test_feature_extraction(self):
        """Test extraction of featured artists."""
        title, features = normalize_title("Song Title (feat. Artist Name)")
        assert title == "Song Title"
        assert "Artist Name" in features

        title, features = normalize_title("Another Song ft. Someone Else")
        assert "Someone Else" in features

    def test_multiple_features(self):
        """Test extraction of multiple featured artists."""
        title, features = normalize_title("Song (feat. Artist1 & Artist2)")
        assert len(features) == 2
        assert "Artist1" in features
        assert "Artist2" in features


class TestNormalizeArtist:
    """Test artist normalization."""

    def test_basic_normalization(self):
        """Test basic artist normalization."""
        result = normalize_artist("The Beatles")
        assert result == "Beatles, The"

    def test_no_the_prefix(self):
        """Test artist without 'The' prefix."""
        result = normalize_artist("Queen")
        assert result == "Queen"

    def test_whitespace_handling(self):
        """Test whitespace normalization."""
        result = normalize_artist("  Led   Zeppelin  ")
        assert result == "Led Zeppelin"


class TestSearchKey:
    """Test search key creation."""

    def test_basic_key_creation(self):
        """Test basic search key creation."""
        key = create_search_key("Song Title", "Artist Name")
        assert "|" in key
        assert key.islower()

    def test_punctuation_removal(self):
        """Test that punctuation is removed from keys."""
        key = create_search_key("Song, Title!", "Artist's Name")
        assert "," not in key
        assert "!" not in key
        assert "'" not in key


class TestVersionDetection:
    """Test version detection functions."""

    def test_live_version_detection(self):
        """Test live version detection."""
        assert is_live_version("Song Title (Live)")
        assert is_live_version("Song Title - Live at Madison Square Garden")
        assert not is_live_version("Song Title")

    def test_remix_detection(self):
        """Test remix detection."""
        assert is_remix_version("Song Title (Remix)")
        assert is_remix_version("Song Title - Radio Edit")
        assert not is_remix_version("Song Title")

    def test_remaster_detection(self):
        """Test remaster detection."""
        assert is_remaster("Song Title (Remastered)")
        assert is_remaster("Song Title - 2009 Remaster")
        assert not is_remaster("Song Title")
