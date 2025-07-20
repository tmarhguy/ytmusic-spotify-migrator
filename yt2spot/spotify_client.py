"""
Spotify API client for playlist management and track operations.
"""

import os
import time
from urllib.parse import quote

import spotipy
from rich.console import Console
from spotipy.oauth2 import SpotifyOAuth

from yt2spot.models import MatchCandidate, SessionConfig

console = Console()


class SpotifyClient:
    """Client for interacting with the Spotify Web API."""

    def __init__(self, config: SessionConfig):
        self.config = config
        self._client: spotipy.Spotify | None = None
        self._user_id: str | None = None

    def authenticate(self) -> bool:
        """Authenticate with Spotify using OAuth2."""
        try:
            # Get credentials from environment or config
            client_id = os.getenv("SPOTIFY_CLIENT_ID") or self.config.client_id
            client_secret = (
                os.getenv("SPOTIFY_CLIENT_SECRET") or self.config.client_secret
            )
            redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI") or self.config.redirect_uri

            if not all([client_id, client_secret, redirect_uri]):
                console.print(
                    "[red]Missing Spotify credentials. Please set environment variables or config.[/red]"
                )
                return False

            # Set up OAuth with required scopes
            scope = (
                "user-library-read "
                "user-library-modify "
                "playlist-read-private "
                "playlist-modify-private "
                "playlist-modify-public"
            )

            auth_manager = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope,
                cache_path=".spotify_cache",
                show_dialog=True,
            )

            self._client = spotipy.Spotify(auth_manager=auth_manager)

            # Test authentication by getting user profile
            user_profile = self._client.current_user()
            self._user_id = user_profile["id"]

            console.print(
                f"[green]✓[/green] Authenticated as [cyan]{user_profile['display_name']}[/cyan]"
            )
            return True

        except Exception as e:
            console.print(f"[red]Authentication failed: {e}[/red]")
            return False

    def search_tracks(self, query: str, limit: int = 10) -> list[MatchCandidate]:
        """Search for tracks on Spotify."""
        if not self._client:
            raise RuntimeError("Spotify client not authenticated")

        try:
            # Clean and format search query
            search_query = quote(query.strip())
            results = self._client.search(q=search_query, type="track", limit=limit)

            candidates = []
            for track in results["tracks"]["items"]:
                # Get primary artist and additional artists
                artists = [artist["name"] for artist in track["artists"]]
                primary_artist = artists[0] if artists else "Unknown"
                all_artists = ", ".join(artists)

                candidate = MatchCandidate(
                    spotify_id=track["id"],
                    title=track["name"],
                    artist=primary_artist,
                    all_artists=all_artists,
                    album=track["album"]["name"],
                    duration_ms=track["duration_ms"],
                    popularity=track["popularity"],
                    preview_url=track.get("preview_url"),
                    spotify_url=track["external_urls"]["spotify"],
                )
                candidates.append(candidate)

            return candidates

        except Exception as e:
            console.print(f"[red]Search failed for '{query}': {e}[/red]")
            return []

    def like_track(self, spotify_id: str) -> bool:
        """Add a track to the user's liked songs."""
        if not self._client:
            raise RuntimeError("Spotify client not authenticated")

        try:
            self._client.current_user_saved_tracks_add([spotify_id])
            return True
        except Exception as e:
            console.print(f"[red]Failed to like track {spotify_id}: {e}[/red]")
            return False

    def unlike_track(self, spotify_id: str) -> bool:
        """Remove a track from the user's liked songs."""
        if not self._client:
            raise RuntimeError("Spotify client not authenticated")

        try:
            self._client.current_user_saved_tracks_delete([spotify_id])
            return True
        except Exception as e:
            console.print(f"[red]Failed to unlike track {spotify_id}: {e}[/red]")
            return False

    def is_track_liked(self, spotify_id: str) -> bool:
        """Check if a track is in the user's liked songs."""
        if not self._client:
            raise RuntimeError("Spotify client not authenticated")

        try:
            result = self._client.current_user_saved_tracks_contains([spotify_id])
            return result[0] if result else False
        except Exception as e:
            console.print(
                f"[red]Failed to check if track {spotify_id} is liked: {e}[/red]"
            )
            return False

    def create_playlist(
        self, name: str, description: str = "", public: bool = True
    ) -> str | None:
        """Create a new playlist."""
        if not self._client or not self._user_id:
            raise RuntimeError("Spotify client not authenticated")

        try:
            playlist = self._client.user_playlist_create(
                user=self._user_id, name=name, public=public, description=description
            )
            return playlist["id"]
        except Exception as e:
            console.print(f"[red]Failed to create playlist '{name}': {e}[/red]")
            return None

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> bool:
        """Add tracks to a playlist."""
        if not self._client:
            raise RuntimeError("Spotify client not authenticated")

        try:
            # Spotify API allows max 100 tracks per request
            batch_size = 100
            for i in range(0, len(track_ids), batch_size):
                batch = track_ids[i : i + batch_size]
                self._client.playlist_add_items(playlist_id, batch)

                # Rate limiting
                if len(track_ids) > batch_size:
                    time.sleep(0.1)

            return True
        except Exception as e:
            console.print(f"[red]Failed to add tracks to playlist: {e}[/red]")
            return False

    def get_playlist_by_name(self, name: str) -> dict | None:
        """Find a playlist by name."""
        if not self._client:
            raise RuntimeError("Spotify client not authenticated")

        try:
            playlists = self._client.current_user_playlists(limit=50)
            for playlist in playlists["items"]:
                if playlist["name"] == name:
                    return playlist
            return None
        except Exception as e:
            console.print(f"[red]Failed to search for playlist '{name}': {e}[/red]")
            return None

    def get_user_profile(self) -> dict | None:
        """Get the current user's profile."""
        if not self._client:
            return None

        try:
            return self._client.current_user()
        except Exception as e:
            console.print(f"[red]Failed to get user profile: {e}[/red]")
            return None

    def get_track_info(self, spotify_id: str) -> dict | None:
        """Get detailed information about a track."""
        if not self._client:
            raise RuntimeError("Spotify client not authenticated")

        try:
            return self._client.track(spotify_id)
        except Exception as e:
            console.print(f"[red]Failed to get track info for {spotify_id}: {e}[/red]")
            return None
