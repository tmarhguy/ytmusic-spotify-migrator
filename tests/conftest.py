"""Test configuration for YT2Spot."""

import pytest


@pytest.fixture
def sample_input_file(tmp_path):
    """Create a sample input file for testing."""
    content = """Bohemian Rhapsody - Queen
Hotel California - Eagles (Official Video)
Stairway to Heaven - Led Zeppelin
Sweet Child O' Mine - Guns N' Roses (Official Audio)
Don't Stop Believin' - Journey
Imagine - John Lennon
Like a Rolling Stone - Bob Dylan
Hey Jude - The Beatles
Purple Haze - Jimi Hendrix
Good Vibrations - The Beach Boys"""

    file_path = tmp_path / "test_input.txt"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    from yt2spot.models import SessionConfig

    return SessionConfig(
        input_path="test_input.txt",
        playlist_name="Test Playlist",
        dry_run=True,  # Always dry run in tests
        client_id="test_client_id",
        client_secret="test_client_secret",
    )
