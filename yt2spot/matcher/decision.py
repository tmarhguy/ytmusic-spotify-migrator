"""
Decision logic for track matching with automatic and interactive modes.
"""

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from yt2spot.matcher.scoring import (
    get_match_quality,
    is_acceptable_match,
    is_good_match,
)
from yt2spot.models import MatchCandidate, MatchDecision, SessionConfig, SongInput

console = Console()


def make_decision(
    song: SongInput,
    candidates: list[MatchCandidate],
    config: SessionConfig,
    interactive: bool = False,
) -> MatchDecision:
    """
    Make a decision on which track to match, if any.

    Args:
        song: Input song to match
        candidates: Scored and sorted list of candidates
        config: Session configuration
        interactive: Whether to prompt user for manual decisions

    Returns:
        MatchDecision with the chosen candidate or rejection reason
    """
    if not candidates:
        return MatchDecision(
            input_song=song,
            decision="no_candidates",
            confidence=0.0,
            reason="No candidates found in Spotify search",
        )

    best_candidate = candidates[0]  # Already sorted by score

    # Automatic decision based on thresholds
    if is_good_match(best_candidate, config):
        return MatchDecision(
            input_song=song,
            chosen_candidate=best_candidate,
            decision="auto_accept",
            confidence=best_candidate.match_score,
            reason=f"High confidence match (score: {best_candidate.match_score:.2f})",
        )

    if not is_acceptable_match(best_candidate, config):
        return MatchDecision(
            input_song=song,
            decision="auto_reject",
            confidence=best_candidate.match_score,
            reason=f"Below rejection threshold (score: {best_candidate.match_score:.2f})",
        )

    # Middle ground - requires decision
    if interactive:
        return _interactive_decision(song, candidates, config)
    else:
        # In non-interactive mode, skip uncertain matches
        return MatchDecision(
            input_song=song,
            decision="skipped",
            confidence=best_candidate.match_score,
            reason=f"Uncertain match - requires manual review (score: {best_candidate.match_score:.2f})",
        )


def _interactive_decision(
    song: SongInput, candidates: list[MatchCandidate], config: SessionConfig
) -> MatchDecision:
    """Handle interactive decision making with user input."""

    console.print(
        f"\n[bold]🎵 Matching: [cyan]{song.title}[/cyan] by [cyan]{song.artist}[/cyan][/bold]"
    )

    if song.album:
        console.print(f"   Album: [dim]{song.album}[/dim]")

    # Show candidates table
    _display_candidates_table(candidates[:5])  # Show top 5

    while True:
        console.print("\n[bold]Options:[/bold]")
        console.print("  [green]1-5[/green]: Select a candidate")
        console.print("  [yellow]s[/yellow]: Skip this song")
        console.print("  [red]r[/red]: Reject (no good match)")
        console.print("  [blue]p[/blue]: Preview candidate (if available)")
        console.print("  [cyan]q[/cyan]: Quit migration")

        choice = Prompt.ask("Your choice", default="s").lower().strip()

        if choice == "q":
            raise KeyboardInterrupt("Migration cancelled by user")

        if choice == "s":
            return MatchDecision(
                input_song=song,
                decision="skipped",
                confidence=candidates[0].match_score if candidates else 0.0,
                reason="Manually skipped",
            )

        if choice == "r":
            return MatchDecision(
                input_song=song,
                decision="manual_reject",
                confidence=0.0,
                reason="Manually rejected - no good match",
            )

        if choice == "p":
            _preview_candidate(candidates)
            continue

        # Try to parse as candidate number
        try:
            candidate_idx = int(choice) - 1
            if 0 <= candidate_idx < len(candidates) and candidate_idx < 5:
                chosen = candidates[candidate_idx]

                # Confirm selection
                quality, _ = get_match_quality(chosen.match_score)
                if Confirm.ask(
                    f"Confirm selection: [cyan]{chosen.title}[/cyan] by [cyan]{chosen.artist}[/cyan] ({quality} match)?"
                ):
                    return MatchDecision(
                        input_song=song,
                        chosen_candidate=chosen,
                        decision="manual_accept",
                        confidence=chosen.match_score,
                        reason=f"Manually selected (option {choice})",
                    )
            else:
                console.print("[red]Invalid selection. Please choose 1-5.[/red]")
        except ValueError:
            console.print(
                "[red]Invalid input. Please choose a number 1-5 or use s/r/p/q.[/red]"
            )


def _display_candidates_table(candidates: list[MatchCandidate]) -> None:
    """Display candidates in a formatted table."""
    table = Table(
        title="🎯 Match Candidates", show_header=True, header_style="bold magenta"
    )

    table.add_column("#", style="dim", width=3)
    table.add_column("Title", style="cyan", min_width=20)
    table.add_column("Artist", style="green", min_width=15)
    table.add_column("Album", style="yellow", min_width=15)
    table.add_column("Score", justify="right", style="bright_white")
    table.add_column("Quality", justify="center")

    for i, candidate in enumerate(candidates, 1):
        quality, color = get_match_quality(candidate.match_score)

        # Truncate long text for table display
        title = (
            candidate.title[:25] + "..."
            if len(candidate.title) > 25
            else candidate.title
        )
        artist = (
            candidate.artist[:20] + "..."
            if len(candidate.artist) > 20
            else candidate.artist
        )
        album = (
            candidate.album[:20] + "..."
            if len(candidate.album) > 20
            else candidate.album
        )

        table.add_row(
            str(i),
            title,
            artist,
            album,
            f"{candidate.match_score:.2f}",
            f"[{color}]{quality}[/{color}]",
        )

    console.print(table)


def _preview_candidate(candidates: list[MatchCandidate]) -> None:
    """Allow user to preview a candidate (open Spotify URL)."""
    while True:
        choice = Prompt.ask(
            "Which candidate to preview? (1-5 or 'b' to go back)", default="b"
        )

        if choice.lower() == "b":
            break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(candidates) and idx < 5:
                candidate = candidates[idx]
                console.print(
                    f"\n[cyan]🎵 Preview:[/cyan] {candidate.title} by {candidate.artist}"
                )
                console.print(f"[blue]Spotify URL:[/blue] {candidate.spotify_url}")

                if candidate.preview_url:
                    console.print(
                        f"[green]Preview URL:[/green] {candidate.preview_url}"
                    )
                else:
                    console.print("[dim]No preview available[/dim]")

                console.print("[dim]Copy the URL to your browser to listen[/dim]\n")
                Prompt.ask("Press Enter to continue", default="")
                break
            else:
                console.print("[red]Invalid selection.[/red]")
        except ValueError:
            console.print("[red]Please enter a number 1-5 or 'b'.[/red]")


def get_decision_summary(decisions: list[MatchDecision]) -> dict:
    """Generate summary statistics for a list of decisions."""
    if not decisions:
        return {
            "total": 0,
            "auto_accept": 0,
            "manual_accept": 0,
            "auto_reject": 0,
            "manual_reject": 0,
            "skipped": 0,
            "no_candidates": 0,
            "success_rate": 0.0,
            "avg_confidence": 0.0,
        }

    counts = {
        "total": len(decisions),
        "auto_accept": sum(1 for d in decisions if d.decision == "auto_accept"),
        "manual_accept": sum(1 for d in decisions if d.decision == "manual_accept"),
        "auto_reject": sum(1 for d in decisions if d.decision == "auto_reject"),
        "manual_reject": sum(1 for d in decisions if d.decision == "manual_reject"),
        "skipped": sum(1 for d in decisions if d.decision == "skipped"),
        "no_candidates": sum(1 for d in decisions if d.decision == "no_candidates"),
    }

    successful = counts["auto_accept"] + counts["manual_accept"]
    counts["success_rate"] = (
        successful / counts["total"] if counts["total"] > 0 else 0.0
    )

    confidences = [d.confidence for d in decisions if d.confidence > 0]
    counts["avg_confidence"] = (
        sum(confidences) / len(confidences) if confidences else 0.0
    )

    return counts
