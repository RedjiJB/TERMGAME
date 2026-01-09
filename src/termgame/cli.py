"""CLI interface for TermGame using Typer.

This module provides the command-line interface for TermGame, including
commands for starting missions, viewing progress, and managing scenarios.
"""

import asyncio
from collections.abc import Coroutine
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from termgame.cli_utils import create_cli_engine
from termgame.config import get_config
from termgame.engine.exceptions import (
    MissionAlreadyActiveError,
    MissionNotFoundError,
    NoActiveMissionError,
    ValidationFailedError,
)
from termgame.loaders.scenario_loader import ScenarioLoader

app = typer.Typer(
    name="termgame",
    help="Terminal-based CLI training platform for learning command-line skills",
    add_completion=True,
)
console = Console()

# Constants
DESCRIPTION_MAX_LEN = 60


def run_async(coro: Coroutine[Any, Any, None]) -> None:
    """Helper to run async functions in Typer commands.

    Args:
        coro: Coroutine to execute
    """
    asyncio.run(coro)


@app.command(name="list")
def list_missions(
    difficulty: str = typer.Option(
        None,
        "--difficulty",
        "-d",
        help="Filter by difficulty (beginner, intermediate, advanced)",
    ),
) -> None:
    """List all available missions.

    Shows available missions from the scenarios directory, with optional
    filtering by difficulty level.
    """
    try:
        config = get_config()
        loader = ScenarioLoader(config.scenarios_dir)

        # Discover all scenarios
        scenarios: list[dict[str, Any]] = []
        for scenario_file in config.scenarios_dir.rglob("*.yml"):
            if scenario_file.name.startswith("_"):
                continue

            # Get relative path as mission ID
            rel_path = scenario_file.relative_to(config.scenarios_dir)
            mission_id = str(rel_path.with_suffix("")).replace("\\", "/")

            try:
                scenario = loader.load(mission_id)

                # Filter by difficulty if specified
                if difficulty and scenario.mission.difficulty != difficulty:
                    continue

                scenarios.append(
                    {
                        "id": mission_id,
                        "title": scenario.mission.title,
                        "difficulty": scenario.mission.difficulty,
                        "time": scenario.mission.estimated_time,
                        "description": scenario.mission.description,
                    }
                )
            except Exception:  # noqa: S112
                # Skip invalid scenarios
                continue

        if not scenarios:
            if difficulty:
                console.print(f"[yellow]No {difficulty} missions found.[/yellow]")
            else:
                console.print("[yellow]No missions found.[/yellow]")
            return

        # Create table
        table = Table(title="Available Missions", show_header=True, header_style="bold")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Difficulty", justify="center")
        table.add_column("Time", justify="right")
        table.add_column("Description", style="dim")

        # Color coding for difficulty
        diff_colors = {
            "beginner": "green",
            "intermediate": "yellow",
            "advanced": "red",
        }

        for s in sorted(scenarios, key=lambda x: str(x["id"])):
            table.add_row(
                s["id"],
                s["title"],
                f"[{diff_colors.get(s['difficulty'], 'white')}]{s['difficulty']}[/]",
                f"{s['time']} min",
                (
                    s["description"][:DESCRIPTION_MAX_LEN] + "..."
                    if len(s["description"]) > DESCRIPTION_MAX_LEN
                    else s["description"]
                ),
            )

        console.print(table)
        console.print(f"\n[dim]Found {len(scenarios)} mission(s)[/dim]")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def start(mission_id: str) -> None:
    """Start a mission by ID.

    Initializes a mission container and sets up the environment. You can
    then use 'validate' to check each step and 'hint' if you need help.

    Args:
        mission_id: The mission identifier (e.g., 'linux/basics/navigation')
    """

    async def _start() -> None:
        config = get_config()
        engine = await create_cli_engine(config)

        try:
            await engine.start_mission(mission_id)
            console.print(f"[bold green]✓ Mission started:[/bold green] {mission_id}")

            # Show first step
            step_info = await engine.get_current_step(mission_id)
            if step_info:
                step_num = int(step_info["index"]) + 1
                console.print(f"\n[bold blue]Step {step_num}:[/bold blue] {step_info['title']}")
                console.print(f"[dim]{step_info['description']}[/dim]")
                console.print(f"\n[yellow]Hint:[/yellow] {step_info['hint']}")

        except MissionNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            console.print("[dim]Use 'termgame list' to see available missions[/dim]")
            raise typer.Exit(code=1) from e
        except MissionAlreadyActiveError as e:
            console.print(f"[yellow]Warning:[/yellow] {e}")
            console.print("[dim]Use 'termgame abandon' to quit the current mission first[/dim]")
            raise typer.Exit(code=1) from e
        except Exception as e:
            console.print(f"[red]Unexpected error:[/red] {e}")
            raise typer.Exit(code=1) from e

    run_async(_start())


@app.command()
def validate(mission_id: str) -> None:
    """Validate the current step of an active mission.

    Checks if you've completed the current step correctly and advances
    to the next step if successful.

    Args:
        mission_id: The mission identifier
    """

    async def _validate() -> None:
        config = get_config()
        engine = await create_cli_engine(config)

        try:
            # Get current step before validation
            step_info = await engine.get_current_step(mission_id)
            if not step_info:
                console.print("[yellow]No active mission step found[/yellow]")
                return

            current_step = int(step_info["index"]) + 1

            # Validate
            success = await engine.validate_step(mission_id)

            if success:
                console.print(f"[bold green]✓ Step {current_step} complete![/bold green]")

                # Check if there's a next step
                next_step = await engine.get_current_step(mission_id)
                if next_step:
                    next_step_num = int(next_step["index"]) + 1
                    console.print(
                        f"\n[bold blue]Step {next_step_num}:[/bold blue] {next_step['title']}"
                    )
                    console.print(f"[dim]{next_step['description']}[/dim]")
                    console.print(f"\n[yellow]Hint:[/yellow] {next_step['hint']}")
                else:
                    # Mission complete
                    progress = await engine.get_mission_status(mission_id)
                    if progress and progress["status"] == "completed":
                        console.print("\n[bold green]🎉 Mission Complete![/bold green]")
                        xp_earned = progress.get("xp_earned", 0)
                        console.print(f"[green]You earned {xp_earned} XP![/green]")
            else:
                console.print(f"[red]✗ Step {current_step} validation failed[/red]")
                console.print("[dim]Use 'termgame hint {mission_id}' for help[/dim]")

        except ValidationFailedError as e:
            console.print(f"[red]Validation failed:[/red] {e}")
            raise typer.Exit(code=1) from e
        except NoActiveMissionError as e:
            console.print(f"[yellow]{e}[/yellow]")
            console.print("[dim]Use 'termgame start <mission-id>' to begin[/dim]")
            raise typer.Exit(code=1) from e
        except Exception as e:
            console.print(f"[red]Unexpected error:[/red] {e}")
            raise typer.Exit(code=1) from e

    run_async(_validate())


@app.command()
def hint(mission_id: str) -> None:
    """Get a hint for the current step.

    Args:
        mission_id: The mission identifier
    """

    async def _hint() -> None:
        config = get_config()
        engine = await create_cli_engine(config)

        try:
            hint_text = await engine.get_hint(mission_id)
            if hint_text:
                console.print(f"[yellow]💡 Hint:[/yellow] {hint_text}")
            else:
                console.print("[dim]No hint available[/dim]")

        except NoActiveMissionError as e:
            console.print(f"[yellow]{e}[/yellow]")
            raise typer.Exit(code=1) from e
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1) from e

    run_async(_hint())


@app.command()
def progress(
    mission_id: str = typer.Option(
        None,
        "--mission",
        "-m",
        help="Show progress for specific mission",
    ),
) -> None:
    """Show your learning progress.

    Displays current mission status, XP earned, and step completion.
    """

    async def _progress() -> None:
        config = get_config()
        engine = await create_cli_engine(config)

        try:
            if mission_id:
                # Show specific mission progress
                status = await engine.get_mission_status(mission_id)
                if not status:
                    console.print(f"[yellow]No progress found for {mission_id}[/yellow]")
                    return

                console.print(f"[bold]Mission:[/bold] {mission_id}")
                console.print(f"[bold]Status:[/bold] {status['status']}")
                console.print(f"[bold]Current Step:[/bold] {status['current_step']}")
                console.print(f"[bold]XP Earned:[/bold] {status.get('xp_earned', 0)}")

                if status["status"] == "active":
                    step_info = await engine.get_current_step(mission_id)
                    if step_info:
                        console.print(f"\n[bold blue]Next Step:[/bold blue] {step_info['title']}")
                        console.print(f"[dim]{step_info['description']}[/dim]")
            else:
                # Show overall progress (would need to query all missions)
                console.print("[bold blue]Your Progress:[/bold blue]")
                console.print("[dim]Use --mission/-m to view specific mission progress[/dim]")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1) from e

    run_async(_progress())


@app.command()
def abandon(mission_id: str) -> None:
    """Abandon the current mission.

    Stops and removes the mission container. Progress is saved but
    the mission is marked as abandoned.

    Args:
        mission_id: The mission identifier
    """

    async def _abandon() -> None:
        config = get_config()
        engine = await create_cli_engine(config)

        try:
            await engine.abandon_mission(mission_id)
            console.print(f"[yellow]Mission abandoned:[/yellow] {mission_id}")
            console.print("[dim]Progress has been saved[/dim]")

        except NoActiveMissionError as e:
            console.print(f"[yellow]{e}[/yellow]")
            raise typer.Exit(code=1) from e
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1) from e

    run_async(_abandon())


@app.command()
def tui() -> None:
    """Launch interactive CLI mode.

    Opens a continuous prompt interface for running missions,
    similar to Codex/Gemini CLI experience.
    """
    from termgame.interactive import run_interactive

    try:
        run_interactive()
    except Exception as e:
        console.print(f"[red]Error launching interactive CLI:[/red] {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
