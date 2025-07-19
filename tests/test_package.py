"""Tests for the YT2Spot package."""

def test_version():
    """Test that version is properly defined."""
    from yt2spot.version import __version__
    
    assert __version__ == "0.1.0"
    assert isinstance(__version__, str)


def test_package_import():
    """Test that the package imports correctly."""
    import yt2spot
    
    assert hasattr(yt2spot, '__version__')
    assert yt2spot.__version__ == "0.1.0"
