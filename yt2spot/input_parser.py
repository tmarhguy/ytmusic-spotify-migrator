"""
Input file parsing for YT2Spot.
Supports CSV, JSON, and TXT formats from YouTube Music exports.
"""

import csv
import json
from pathlib import Path

from rich.console import Console

from yt2spot.models import SongInput

console = Console()


def parse_input_file(file_path: str | Path) -> list[SongInput]:
    """
    Parse input file and return list of SongInput objects.

    Supports:
    - CSV files (with headers: Title, Artist, Album, Duration)
    - JSON files (with track objects)
    - TXT files (simple format: "Title - Artist")

    Args:
        file_path: Path to the input file

    Returns:
        List of SongInput objects

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is unsupported or malformed
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return _parse_csv(file_path)
    elif suffix == ".json":
        return _parse_json(file_path)
    elif suffix == ".txt":
        return _parse_txt(file_path)
    else:
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported: .csv, .json, .txt"
        )


def _parse_csv(file_path: Path) -> list[SongInput]:
    """Parse CSV file with song data."""
    songs = []

    try:
        with open(file_path, encoding="utf-8") as file:
            # Try to detect if file has headers
            sample = file.read(1024)
            file.seek(0)

            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(sample)

            reader = csv.reader(file)

            if has_header:
                headers = next(reader)
                # Try to map headers to expected fields
                header_map = _map_csv_headers(headers)
            else:
                # Assume order: Title, Artist, Album, Duration
                header_map = {"title": 0, "artist": 1, "album": 2, "duration": 3}

            for row_num, row in enumerate(reader, start=2 if has_header else 1):
                if not row or all(not cell.strip() for cell in row):
                    continue  # Skip empty rows

                try:
                    song = SongInput(
                        title=row[header_map["title"]].strip()
                        if len(row) > header_map["title"]
                        else "",
                        artist=row[header_map["artist"]].strip()
                        if len(row) > header_map["artist"]
                        else "",
                        album=row[header_map.get("album", -1)].strip()
                        if len(row) > header_map.get("album", -1)
                        else "",
                        duration=row[header_map.get("duration", -1)].strip()
                        if len(row) > header_map.get("duration", -1)
                        else "",
                        source_line=row_num,
                    )

                    if song.title and song.artist:  # Require at least title and artist
                        songs.append(song)
                    else:
                        console.print(
                            f"[yellow]Warning:[/yellow] Skipping row {row_num} - missing title or artist"
                        )

                except (IndexError, ValueError) as e:
                    console.print(
                        f"[yellow]Warning:[/yellow] Skipping malformed row {row_num}: {e}"
                    )

    except Exception as e:
        raise ValueError(f"Failed to parse CSV file: {e}") from e

    console.print(f"[green]✓[/green] Parsed {len(songs)} songs from CSV file")
    return songs


def _parse_json(file_path: Path) -> list[SongInput]:
    """Parse JSON file with song data."""
    songs = []

    try:
        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)

        # Handle different JSON structures
        if isinstance(data, list):
            # Array of track objects
            tracks = data
        elif isinstance(data, dict):
            # Object with tracks array
            tracks = data.get("tracks", data.get("songs", data.get("items", [])))
        else:
            raise ValueError("Unexpected JSON structure")

        for i, track in enumerate(tracks):
            try:
                # Handle different field names
                title = (
                    track.get("title")
                    or track.get("name")
                    or track.get("track_name", "")
                )
                artist = track.get("artist") or track.get("artist_name") or ""
                album = track.get("album") or track.get("album_name", "")
                duration = (
                    track.get("duration")
                    or track.get("duration_ms")
                    or track.get("length", "")
                )

                # Handle artist arrays
                if isinstance(artist, list):
                    artist = ", ".join(artist)

                song = SongInput(
                    title=str(title).strip(),
                    artist=str(artist).strip(),
                    album=str(album).strip(),
                    duration=str(duration).strip(),
                    source_line=i + 1,
                )

                if song.title and song.artist:
                    songs.append(song)
                else:
                    console.print(
                        f"[yellow]Warning:[/yellow] Skipping track {i+1} - missing title or artist"
                    )

            except (KeyError, ValueError) as e:
                console.print(
                    f"[yellow]Warning:[/yellow] Skipping malformed track {i+1}: {e}"
                )

    except Exception as e:
        raise ValueError(f"Failed to parse JSON file: {e}") from e

    console.print(f"[green]✓[/green] Parsed {len(songs)} songs from JSON file")
    return songs


def _parse_txt(file_path: Path) -> list[SongInput]:
    """Parse simple text file with song data."""
    songs = []

    try:
        with open(file_path, encoding="utf-8") as file:
            lines = file.readlines()

        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue

            # Try different separators
            if " - " in line:
                parts = line.split(" - ", 1)
            elif " | " in line:
                parts = line.split(" | ", 1)
            elif "\t" in line:
                parts = line.split("\t", 1)
            else:
                # Single field, assume it's title
                parts = [line, ""]

            if len(parts) >= 2:
                title, artist = parts[0].strip(), parts[1].strip()
            else:
                title, artist = parts[0].strip(), ""

            # Clean up common patterns
            title = _clean_track_title(title)
            artist = _clean_artist_name(artist)

            if title:  # Require at least a title
                song = SongInput(
                    title=title,
                    artist=artist,
                    album="",
                    duration="",
                    source_line=line_num,
                )
                songs.append(song)
            else:
                console.print(
                    f"[yellow]Warning:[/yellow] Skipping empty line {line_num}"
                )

    except Exception as e:
        raise ValueError(f"Failed to parse TXT file: {e}") from e

    console.print(f"[green]✓[/green] Parsed {len(songs)} songs from TXT file")
    return songs


def _map_csv_headers(headers: list[str]) -> dict:
    """Map CSV headers to standard field names."""
    header_map = {}
    headers_lower = [h.lower().strip() for h in headers]

    # Map title field
    for i, header in enumerate(headers_lower):
        if header in ["title", "name", "song", "track", "song_name", "track_name"]:
            header_map["title"] = i
            break
    else:
        header_map["title"] = 0  # Default to first column

    # Map artist field
    for i, header in enumerate(headers_lower):
        if header in ["artist", "artist_name", "artists", "performer"]:
            header_map["artist"] = i
            break
    else:
        header_map["artist"] = 1  # Default to second column

    # Map album field
    for i, header in enumerate(headers_lower):
        if header in ["album", "album_name", "release"]:
            header_map["album"] = i
            break
    else:
        header_map["album"] = 2 if len(headers) > 2 else -1

    # Map duration field
    for i, header in enumerate(headers_lower):
        if header in ["duration", "length", "time", "duration_ms"]:
            header_map["duration"] = i
            break
    else:
        header_map["duration"] = 3 if len(headers) > 3 else -1

    return header_map


def _clean_track_title(title: str) -> str:
    """Clean track title by removing common unwanted patterns."""
    title = title.strip()

    # Remove common YouTube-specific patterns
    patterns_to_remove = [
        "(Official Video)",
        "(Official Audio)",
        "(Official Music Video)",
        "(Official Lyric Video)",
        "[Official Video]",
        "[Official Audio]",
        "(HD)",
        "[HD]",
        "(HQ)",
        "[HQ]",
    ]

    for pattern in patterns_to_remove:
        title = title.replace(pattern, "").strip()

    return title


def _clean_artist_name(artist: str) -> str:
    """Clean artist name by removing unwanted characters."""
    artist = artist.strip()

    # Remove common prefixes/suffixes
    if artist.startswith("by "):
        artist = artist[3:].strip()

    return artist
