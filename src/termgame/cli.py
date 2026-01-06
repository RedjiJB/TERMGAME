"""CLI interface for TermGame using Typer.

This module provides the command-line interface for TermGame, including
commands for starting missions, viewing progress, and managing scenarios.
"""

import typer
from rich.console import Console

app = typer.Typer(
    name="termgame",
    help="Terminal-based CLI training platform",
    add_completion=True,
)
console = Console()


@app.command()
def start(mission_id: str) -> None:
    """Start a mission by ID.

    Args:
        mission_id: The mission identifier (e.g., 'linux/basics/navigation')
    """
    console.print(f"[bold green]Starting mission:[/bold green] {mission_id}")
    # TODO: Implement mission start logic


@app.command()
def list() -> None:  # noqa: A001
    """List all available missions."""
    console.print("[bold blue]Available missions:[/bold blue]")
    # TODO: Implement mission listing


@app.command()
def progress() -> None:
    """Show your learning progress."""
    console.print("[bold yellow]Your progress:[/bold yellow]")
    # TODO: Implement progress tracking


@app.command()
def tui() -> None:
    """Launch the Terminal User Interface."""
    console.print("[bold magenta]Launching TUI...[/bold magenta]")
    # TODO: Implement TUI launch


if __name__ == "__main__":
    app()
