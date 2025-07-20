"""Command-line interface for YT2Spot."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import click
from rich.console import Console

from yt2spot.config import load_config
from yt2spot.models import SessionConfig
from yt2spot.version import __version__

console = Console()


@click.group()
@click.version_option(__version__, prog_name="yt2spot")
def cli() -> None:
    """YT2Spot - Migrate YouTube Music liked songs to Spotify playlists."""
    pass


@cli.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the YouTube Music export text file",
)
@click.option(
    "--playlist",
    "-p",
    default="YT Music Liked Songs",
    help="Name of the Spotify playlist to create/update",
)
@click.option(
    "--public/--private", default=True, help="Make the playlist public or private"
)
@click.option(
    "--dry-run", is_flag=True, help="Simulate the process without making any changes"
)
@click.option("--fuzzy", is_flag=True, help="Enable fuzzy matching for ambiguous songs")
@click.option(
    "--interactive", is_flag=True, help="Prompt for user input on ambiguous matches"
)
@click.option(
    "--force-recreate",
    is_flag=True,
    help="Recreate the playlist from scratch (backup existing)",
)
@click.option(
    "--hard-threshold",
    type=float,
    default=0.87,
    help="Threshold for automatic acceptance (0.0-1.0)",
)
@click.option(
    "--reject-threshold",
    type=float,
    default=0.60,
    help="Threshold for automatic rejection (0.0-1.0)",
)
@click.option(
    "--fuzzy-threshold",
    type=float,
    default=0.80,
    help="Minimum threshold for fuzzy matching (0.0-1.0)",
)
@click.option("--limit", type=int, help="Limit the number of songs to process")
@click.option(
    "--log-dir", type=click.Path(path_type=Path), help="Directory to store log files"
)
@click.option(
    "--cache-file",
    type=click.Path(path_type=Path),
    help="Path to Spotify token cache file",
)
@click.option("--json-logs", is_flag=True, help="Output structured JSON logs")
@click.option("--quiet", "-q", is_flag=True, help="Minimize output (errors only)")
@click.option(
    "--verbose", "-v", is_flag=True, help="Verbose output with detailed information"
)
@click.option("--debug", is_flag=True, help="Debug mode with extensive logging")
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
def migrate(
    input_path: Path,
    playlist: str,
    public: bool,
    dry_run: bool,
    fuzzy: bool,
    interactive: bool,
    force_recreate: bool,
    hard_threshold: float,
    reject_threshold: float,
    fuzzy_threshold: float,
    limit: int | None,
    log_dir: Path | None,
    cache_file: Path | None,
    json_logs: bool,
    quiet: bool,
    verbose: bool,
    debug: bool,
    config: Path | None,
) -> None:
    """
    YT2Spot - Migrate YouTube Music liked songs to Spotify playlists.

    This tool reads a text file export from YouTube Music and creates
    a corresponding Spotify playlist with intelligent track matching.

    Example usage:

        yt2spot --input liked_songs.txt

        yt2spot --input liked_songs.txt --dry-run --verbose

        yt2spot --input liked_songs.txt --interactive --fuzzy
    """
    start_time = time.time()

    # Validate threshold values
    if not (0.0 <= hard_threshold <= 1.0):
        raise click.BadParameter("Hard threshold must be between 0.0 and 1.0")
    if not (0.0 <= reject_threshold <= 1.0):
        raise click.BadParameter("Reject threshold must be between 0.0 and 1.0")
    if not (0.0 <= fuzzy_threshold <= 1.0):
        raise click.BadParameter("Fuzzy threshold must be between 0.0 and 1.0")
    if hard_threshold <= reject_threshold:
        raise click.BadParameter("Hard threshold must be greater than reject threshold")

    # Set verbosity level
    if debug:
        verbose = True
    if quiet and verbose:
        raise click.BadParameter("Cannot use both --quiet and --verbose")

    # Create CLI overrides for configuration
    cli_overrides = {
        "playlists": {
            "default_name": playlist,
            "public": public,
            "force_recreate": force_recreate,
        },
        "matching": {
            "hard_threshold": hard_threshold,
            "reject_threshold": reject_threshold,
            "fuzzy_threshold": fuzzy_threshold,
        },
        "logging": {
            "json": json_logs,
            "quiet": quiet,
            "verbose": verbose,
            "debug": debug,
        },
    }

    # Add optional overrides
    if log_dir:
        cli_overrides["logging"]["log_dir"] = str(log_dir)
    if cache_file:
        cli_overrides["auth"]["cache_file"] = str(cache_file)
    if limit:
        cli_overrides["limit"] = limit
    if dry_run:
        cli_overrides["dry_run"] = dry_run
    if fuzzy:
        cli_overrides["fuzzy"] = fuzzy
    if interactive:
        cli_overrides["interactive"] = interactive

    try:
        # Load configuration
        session_config = load_config(str(input_path), cli_overrides)

        # Show banner
        if not quiet:
            show_banner(session_config)

        # Import and run the main migration pipeline
        from yt2spot.input_parser import parse_input_file
        from yt2spot.matcher.decision import get_decision_summary, make_decision
        from yt2spot.matcher.scoring import score_candidates
        from yt2spot.matcher.search import search_spotify_tracks
        from yt2spot.spotify_client import SpotifyClient

        # Load and validate environment variables
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            # python-dotenv not installed, skip loading .env file
            pass

        # Parse input file
        console.print(f"[cyan]📁 Parsing input file:[/cyan] {input_path}")
        songs = parse_input_file(input_path)

        if not songs:
            console.print("[red]❌ No songs found in input file[/red]")
            return

        # Apply limit if specified
        if limit and limit > 0:
            songs = songs[:limit]
            console.print(f"[yellow]⚠️  Limited to first {limit} songs[/yellow]")

        # Initialize Spotify client
        console.print("[cyan]🔐 Authenticating with Spotify...[/cyan]")
        spotify_client = SpotifyClient(session_config)

        if not spotify_client.authenticate():
            console.print("[red]❌ Failed to authenticate with Spotify[/red]")
            return

        # Process songs
        console.print(f"[cyan]🎵 Processing {len(songs)} songs...[/cyan]")
        decisions = []
        liked_count = 0

        from rich.progress import (
            BarColumn,
            Progress,
            SpinnerColumn,
            TaskProgressColumn,
            TextColumn,
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Processing songs...", total=len(songs))

            for _i, song in enumerate(songs, 1):
                progress.update(task, description=f"Processing: {song.title[:30]}...")

                try:
                    # Search for candidates
                    candidates = search_spotify_tracks(
                        song, spotify_client, session_config
                    )

                    # Score candidates
                    if candidates:
                        candidates = score_candidates(song, candidates, session_config)

                    # Make decision
                    decision = make_decision(
                        song, candidates, session_config, interactive
                    )
                    decisions.append(decision)

                    # Like the track if decision was positive and not dry run
                    if decision.chosen_candidate and not dry_run:
                        if spotify_client.like_track(
                            decision.chosen_candidate.spotify_id
                        ):
                            liked_count += 1
                            if verbose:
                                console.print(
                                    f"[green]✓[/green] Liked: {decision.chosen_candidate.title} by {decision.chosen_candidate.artist}"
                                )
                        else:
                            if verbose:
                                console.print(
                                    f"[red]✗[/red] Failed to like: {decision.chosen_candidate.title}"
                                )
                    elif decision.chosen_candidate and dry_run:
                        liked_count += 1  # Count what would be liked
                        if verbose:
                            console.print(
                                f"[blue]🔍[/blue] Would like: {decision.chosen_candidate.title} by {decision.chosen_candidate.artist}"
                            )

                    progress.advance(task)

                except KeyboardInterrupt:
                    console.print("\n[yellow]⚠️  Migration cancelled by user[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]❌ Error processing '{song.title}': {e}[/red]")
                    continue

        # Show summary
        if not quiet:
            summary = get_decision_summary(decisions)
            console.print("\n[bold]📊 Migration Summary:[/bold]")
            console.print(f"  Total songs processed: {summary['total']}")
            console.print(
                f"  Successfully matched: [green]{summary['auto_accept'] + summary['manual_accept']}[/green]"
            )
            console.print(
                f"  Automatically accepted: [green]{summary['auto_accept']}[/green]"
            )
            console.print(
                f"  Manually accepted: [green]{summary['manual_accept']}[/green]"
            )
            console.print(f"  Songs liked on Spotify: [cyan]{liked_count}[/cyan]")
            console.print(f"  Skipped: [yellow]{summary['skipped']}[/yellow]")
            console.print(
                f"  Rejected: [red]{summary['auto_reject'] + summary['manual_reject']}[/red]"
            )
            console.print(f"  Success rate: [cyan]{summary['success_rate']:.1%}[/cyan]")

            if dry_run:
                console.print(
                    "\n[blue]🔍 This was a dry run - no tracks were actually liked[/blue]"
                )

        if not quiet:
            runtime = time.time() - start_time
            console.print(f"\n[green]✅ Setup completed in {runtime:.2f}s[/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        if debug:
            import traceback

            console.print("[red]" + traceback.format_exc() + "[/red]")
        sys.exit(1)


def show_banner(config: SessionConfig) -> None:
    """Display the application banner."""
    console.print(
        f"""
[bold blue]🎵 YT2Spot v{__version__}[/bold blue]
[dim]YouTube Music → Spotify Migration Tool[/dim]

[bold]Configuration:[/bold]
  Input: {config.input_path}
  Playlist: {config.playlist_name} ({'public' if config.public_playlist else 'private'})
  Matching: hard={config.hard_threshold:.2f}, reject={config.reject_threshold:.2f}
  Mode: {'🔍 Interactive' if config.interactive else '🤖 Automatic'} {'+ 🌊 Fuzzy' if config.fuzzy else ''}
  {'🧪 DRY RUN - No changes will be made' if config.dry_run else ''}
"""
    )


@cli.command()
@click.option(
    "--path",
    type=click.Path(path_type=Path),
    default=Path(".yt2spot.toml"),
    help="Path where to create the config file",
)
def init_config(path: Path) -> None:
    """Create a sample configuration file."""
    from yt2spot.config import ConfigManager

    if path.exists():
        if not click.confirm(f"Config file {path} already exists. Overwrite?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

    manager = ConfigManager()
    manager.create_sample_config(path)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
