"""Interactive CLI interface for TermGame - Codex-style prompt loop.

This module provides a REPL-style interactive interface for executing missions,
similar to Codex CLI's approach of continuous prompting rather than full-screen TUI.
"""

import asyncio
import sys
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from termgame.cli_utils import create_cli_engine
from termgame.config import get_config
from termgame.loaders.scenario_loader import ScenarioLoader


class InteractiveCLI:
    """Interactive command-line interface with continuous prompts."""

    def __init__(self) -> None:
        """Initialize the interactive CLI."""
        self.console = Console()
        self.config = get_config()
        self.engine: Any = None
        self.current_mission: str | None = None
        self.loader = ScenarioLoader(self.config.scenarios_dir)
        self.running = True

    async def initialize(self) -> None:
        """Initialize the mission engine."""
        if self.engine is None:
            self.engine = await create_cli_engine(self.config)

    def print_banner(self) -> None:
        """Display welcome banner."""
        self.console.print("\n[bold cyan]TERMGAME[/bold cyan]")
        self.console.print(
            "[dim]Terminal training platform for Linux, Cisco IOS, and PowerShell[/dim]\n"
        )
        self.console.print("Type [cyan]help[/cyan] for available commands\n")

    def print_help(self) -> None:
        """Display help message with available commands."""
        if self.current_mission:
            help_text = """
[bold cyan]Mission Mode Commands:[/bold cyan]

  When in a mission, you can run any shell command (e.g., [cyan]ls --help[/cyan]).
  The command will be executed in the mission container.

  [cyan]validate[/cyan]          Validate current step and advance
  [cyan]hint[/cyan]              Get a hint for current step
  [cyan]abandon[/cyan]           Abandon current mission
  [cyan]help[/cyan]              Show this help message
  [cyan]quit[/cyan]              Exit the interactive CLI

[dim]Try running commands to complete the mission steps,[/dim]
[dim]then use 'validate' to check your work.[/dim]
"""
        else:
            help_text = """
[bold cyan]Available Commands:[/bold cyan]

  [cyan]list[/cyan]              List all available missions
  [cyan]start <mission-id>[/cyan] Start a mission
  [cyan]progress[/cyan]          Show your progress
  [cyan]help[/cyan]              Show this help message
  [cyan]quit[/cyan]              Exit the interactive CLI

[dim]Example: start linux/basics/navigation[/dim]
"""
        self.console.print(help_text)

    async def cmd_list(self, _args: list[str]) -> None:
        """List all available missions."""
        missions: list[dict[str, Any]] = []

        for scenario_file in self.config.scenarios_dir.rglob("*.yml"):
            if scenario_file.name.startswith("_"):
                continue

            rel_path = scenario_file.relative_to(self.config.scenarios_dir)
            mission_id = str(rel_path.with_suffix("")).replace("\\", "/")

            try:
                scenario = self.loader.load(mission_id)
                missions.append(
                    {
                        "id": mission_id,
                        "title": scenario.mission.title,
                        "difficulty": scenario.mission.difficulty,
                        "time": scenario.mission.estimated_time,
                    }
                )
            except Exception as e:
                # Skip invalid scenario files
                self.console.print(f"[dim]Warning: Skipped {mission_id}: {e}[/dim]", style="dim")
                continue

        if not missions:
            self.console.print("[yellow]No missions found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold dim")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Difficulty", style="dim")
        table.add_column("Time", style="dim", justify="right")

        for mission in sorted(missions, key=lambda m: m["id"]):
            table.add_row(
                mission["id"],
                mission["title"],
                mission["difficulty"],
                f"{mission['time']} min",
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Found {len(missions)} mission(s)[/dim]\n")

    async def cmd_start(self, args: list[str]) -> None:
        """Start a mission."""
        if not args:
            self.console.print("[red]Error:[/red] Mission ID required")
            self.console.print("[dim]Usage: start <mission-id>[/dim]")
            return

        mission_id = args[0]

        await self.initialize()

        try:
            # Check if already in a mission
            if self.current_mission:
                self.console.print(
                    f"[yellow]Warning:[/yellow] Already in mission '{self.current_mission}'"
                )
                self.console.print("[dim]Use 'abandon' to quit current mission first[/dim]\n")
                return

            # Start the mission
            self.console.print(f"[cyan]Starting mission:[/cyan] {mission_id}")
            self.console.print("[dim]Creating container environment...[/dim]")

            await self.engine.start_mission(mission_id)
            step_info = await self.engine.get_current_step(mission_id)

            if not step_info:
                self.console.print("[red]Error:[/red] Failed to load mission steps")
                return

            self.current_mission = mission_id
            self._display_step(step_info)

        except Exception as e:
            self.console.print(f"[red]Error starting mission:[/red] {e}")

    async def cmd_validate(self, _args: list[str]) -> None:
        """Validate current step."""
        if not self.current_mission:
            self.console.print("[yellow]No active mission[/yellow]")
            self.console.print("[dim]Use 'start <mission-id>' to begin[/dim]\n")
            return

        await self.initialize()

        try:
            self.console.print("[dim]Validating step...[/dim]")

            success = await self.engine.validate_step(self.current_mission)

            if success:
                next_step = await self.engine.get_current_step(self.current_mission)

                if next_step:
                    # Move to next step
                    self.console.print("[green]✓ Step complete![/green]\n")
                    self._display_step(next_step)
                else:
                    # Mission complete
                    status = await self.engine.get_mission_status(self.current_mission)
                    xp = status.get("xp_earned", 0) if status else 0
                    self.console.print(
                        f"\n[bold green]🎉 Mission Complete![/bold green] "
                        f"You earned [cyan]{xp} XP[/cyan]\n"
                    )
                    self.current_mission = None
            else:
                self.console.print(
                    "[red]✗ Validation failed[/red] - Check your work and try again\n"
                )

        except Exception as e:
            self.console.print(f"[red]Validation error:[/red] {e}\n")

    async def cmd_hint(self, _args: list[str]) -> None:
        """Get a hint for current step."""
        if not self.current_mission:
            self.console.print("[yellow]No active mission[/yellow]")
            self.console.print("[dim]Use 'start <mission-id>' to begin[/dim]\n")
            return

        await self.initialize()

        try:
            hint = await self.engine.get_hint(self.current_mission)

            if hint:
                self.console.print(Panel(hint, title="💡 Hint", border_style="magenta"))
            else:
                self.console.print("[dim]No hint available for this step[/dim]\n")

        except Exception as e:
            self.console.print(f"[red]Error getting hint:[/red] {e}\n")

    async def cmd_abandon(self, _args: list[str]) -> None:
        """Abandon current mission."""
        if not self.current_mission:
            self.console.print("[yellow]No active mission to abandon[/yellow]\n")
            return

        await self.initialize()

        try:
            mission_id = self.current_mission
            await self.engine.abandon_mission(mission_id)
            self.current_mission = None
            self.console.print(
                f"[yellow]Mission '{mission_id}' abandoned[/yellow] - Progress saved\n"
            )

        except Exception as e:
            self.console.print(f"[red]Error abandoning mission:[/red] {e}\n")

    async def cmd_progress(self, _args: list[str]) -> None:
        """Show user progress."""
        await self.initialize()

        try:
            # TODO: Implement overall progress retrieval
            self.console.print("[cyan]Your Progress:[/cyan]\n")
            self.console.print("[dim]Total XP: 0[/dim]")
            self.console.print("[dim]Missions Completed: 0[/dim]")
            self.console.print("[dim]Active Missions: 0[/dim]\n")
            self.console.print("[dim]Start a mission to begin earning XP![/dim]\n")

        except Exception as e:
            self.console.print(f"[red]Error loading progress:[/red] {e}\n")

    def _display_step(self, step_info: dict[str, Any]) -> None:
        """Display step information."""
        step_num = int(step_info.get("index", 0)) + 1
        total = step_info.get("total", "?")
        title = step_info.get("title", "Unknown Step")
        description = step_info.get("description", "No description")

        self.console.print(f"\n[bold cyan]Step {step_num}/{total}:[/bold cyan] {title}\n")
        self.console.print(Markdown(description))
        self.console.print()

    async def handle_command(self, user_input: str) -> None:
        """Parse and execute user command."""
        user_input = user_input.strip()

        if not user_input:
            return

        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:]

        # Handle quit command
        if command in ("quit", "exit", "q"):
            self.running = False
            if self.current_mission:
                self.console.print(
                    "\n[yellow]Exiting with active mission - use 'abandon' to clean up[/yellow]"
                )
            self.console.print("[dim]Goodbye![/dim]\n")
        # Handle commands that work in any mode
        elif command == "help":
            self.print_help()
        elif command == "validate":
            await self.cmd_validate(args)
        elif command == "hint":
            await self.cmd_hint(args)
        elif command == "abandon":
            await self.cmd_abandon(args)
        # Handle commands outside missions
        elif not self.current_mission:
            await self._handle_lobby_command(command, args)
        # When in a mission, execute commands in the container
        else:
            await self.initialize()
            try:
                output = await self.engine.execute_command(self.current_mission, user_input)
                if output:
                    self.console.print(output)
            except Exception as e:
                self.console.print(f"[red]Error executing command:[/red] {e}")

    async def _handle_lobby_command(self, command: str, args: list[str]) -> None:
        """Handle commands available in lobby (outside missions)."""
        lobby_commands = {
            "list": self.cmd_list,
            "start": self.cmd_start,
            "progress": self.cmd_progress,
        }

        if command in lobby_commands:
            await lobby_commands[command](args)
        else:
            self.console.print(f"[red]Unknown command:[/red] {command}")
            self.console.print("[dim]Type 'help' for available commands[/dim]\n")

    async def run(self) -> None:
        """Run the interactive CLI loop."""
        self.print_banner()

        while self.running:
            try:
                # Show prompt with mission indicator
                if self.current_mission:
                    prompt_text = f"[cyan]{self.current_mission}[/cyan] > "
                else:
                    prompt_text = "[cyan]termgame[/cyan] > "

                user_input = Prompt.ask(prompt_text, console=self.console)
                await self.handle_command(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[dim]Use 'quit' to exit[/dim]")
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[red]Error:[/red] {e}\n")


def run_interactive() -> None:
    """Entry point for interactive CLI."""
    cli = InteractiveCLI()

    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        sys.exit(0)
