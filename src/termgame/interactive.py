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

    # Constants
    MAX_ERROR_LENGTH = 200  # Max length for inline error display

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
        self.console.print(
            "Type [cyan]help[/cyan] for commands, or [cyan]list[/cyan] to see all missions\n"
        )

    def print_help(self) -> None:
        """Display help message with available commands."""
        if self.current_mission:
            help_text = """
[bold cyan]Mission Mode - You're in an active mission![/bold cyan]

[bold white]How it works:[/bold white]
  • Read the step instructions carefully
  • Type Linux commands (e.g., [cyan]ls[/cyan], [cyan]pwd[/cyan], [cyan]cat file.txt[/cyan])
  • Commands are executed inside a real Ubuntu container
  • When you complete the step, type [cyan]validate[/cyan] to check your work

[bold white]Special Commands:[/bold white]
  [cyan]validate[/cyan]          Check if you completed the current step correctly
  [cyan]hint[/cyan]              Get a helpful hint if you're stuck
  [cyan]abandon[/cyan]           Give up and exit this mission
  [cyan]help[/cyan]              Show this help message again
  [cyan]quit[/cyan]              Exit TermGame (mission will be saved)

[bold yellow]Tips:[/bold yellow]
  • If validation fails, read the error and try again
  • Use [cyan]hint[/cyan] if you're unsure what to do
  • Commands run in the container, not your local machine
"""
        else:
            help_text = """
[bold cyan]Welcome to TermGame![/bold cyan]

[bold white]Getting Started:[/bold white]
  1. Type [cyan]list[/cyan] to see all available missions
  2. Choose a mission and type [cyan]start <mission-id>[/cyan]
  3. Complete the mission steps and earn XP!

[bold white]Available Commands:[/bold white]
  [cyan]list[/cyan]              Show all missions with difficulty and time
  [cyan]start <mission-id>[/cyan] Begin a training mission
  [cyan]progress[/cyan]          View your XP and completed missions
  [cyan]help[/cyan]              Show this help message
  [cyan]quit[/cyan]              Exit TermGame

[bold yellow]Examples:[/bold yellow]
  [cyan]list[/cyan]                          → See all missions
  [cyan]start linux/basics/navigation[/cyan]  → Start navigation tutorial
  [cyan]start linux/files/file-viewing[/cyan] → Learn file viewing commands

[dim]Tip: Start with beginner missions in linux/basics/[/dim]
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
            self.console.print("[red]Error:[/red] Mission ID required\n")
            self.console.print("[bold white]Usage:[/bold white] [cyan]start <mission-id>[/cyan]")
            self.console.print("\n[bold white]Examples:[/bold white]")
            self.console.print("  [cyan]start linux/basics/navigation[/cyan]")
            self.console.print("  [cyan]start linux/files/file-viewing[/cyan]")
            self.console.print("\n[dim]Tip: Type 'list' to see all available missions[/dim]\n")
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
            self.console.print(
                "[dim]Creating container environment (this may take a moment)...[/dim]\n"
            )

            await self.engine.start_mission(mission_id)
            step_info = await self.engine.get_current_step(mission_id)

            if not step_info:
                self.console.print("[red]Error:[/red] Failed to load mission steps")
                return

            self.current_mission = mission_id
            self._display_step(step_info)

            # Show helpful tip for first-time users
            self.console.print("[bold yellow]💡 Quick Start:[/bold yellow]")
            self.console.print("  • Run Linux commands to complete the step")
            self.console.print("  • Type [cyan]validate[/cyan] when done to check your work")
            self.console.print("  • Type [cyan]hint[/cyan] if you need help\n")

        except Exception as e:
            error_msg = str(e)
            self.console.print(f"[red]Error starting mission:[/red] {error_msg}\n")

            if "not found" in error_msg.lower():
                self.console.print("[bold white]Suggestions:[/bold white]")
                self.console.print("  • Check the mission ID spelling")
                self.console.print("  • Type [cyan]list[/cyan] to see all available missions")
                self.console.print("  • Mission IDs are case-sensitive\n")

    async def cmd_validate(self, _args: list[str]) -> None:
        """Validate current step."""
        if not self.current_mission:
            self.console.print("[yellow]No active mission[/yellow]")
            self.console.print("[dim]Use 'start <mission-id>' to begin[/dim]\n")
            return

        await self.initialize()

        try:
            self.console.print("[dim]Validating step...[/dim]\n")

            success = await self.engine.validate_step(self.current_mission)

            if success:
                next_step = await self.engine.get_current_step(self.current_mission)

                if next_step:
                    # Move to next step
                    self.console.print("[bold green]✓ Step Complete![/bold green] Great job!\n")
                    self._display_step(next_step)
                else:
                    # Mission complete
                    status = await self.engine.get_mission_status(self.current_mission)
                    xp = status.get("xp_earned", 0) if status else 0
                    self.console.print("\n[bold green]" + "=" * 50 + "[/bold green]")
                    self.console.print(
                        f"[bold green]🎉 MISSION COMPLETE![/bold green] "
                        f"You earned [bold cyan]{xp} XP[/bold cyan]"
                    )
                    self.console.print("[bold green]" + "=" * 50 + "[/bold green]\n")
                    self.console.print("[dim]Type 'list' to start another mission[/dim]\n")
                    self.current_mission = None
            else:
                self.console.print("[bold red]✗ Validation Failed[/bold red]\n")
                self.console.print("[bold white]What to do:[/bold white]")
                self.console.print("  • Read the step instructions carefully above")
                self.console.print("  • Make sure you ran the correct command")
                self.console.print("  • Type [cyan]hint[/cyan] if you're stuck")
                self.console.print("  • Try running the command again\n")

        except Exception as e:
            self.console.print(f"[red]Validation error:[/red] {e}\n")
            self.console.print("[dim]There was a problem checking your work.[/dim]")
            self.console.print(
                "[dim]Try running your command again, or type 'hint' for help.[/dim]\n"
            )

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

    async def handle_command(self, user_input: str) -> None:  # noqa: PLR0912
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
                    # Check if output indicates an error
                    if "command not found" in output.lower() or "no such file" in output.lower():
                        self.console.print(f"[yellow]{output}[/yellow]")
                        self.console.print("[dim]Tip: Check spelling and try again[/dim]\n")
                    elif "error" in output.lower() and len(output) < self.MAX_ERROR_LENGTH:
                        self.console.print(f"[yellow]{output}[/yellow]")
                    else:
                        self.console.print(output)
            except Exception as e:
                self.console.print(f"[red]Error executing command:[/red] {e}\n")
                self.console.print(
                    "[dim]The container may have stopped. "
                    "Try typing 'abandon' and restarting.[/dim]\n"
                )

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
            self.console.print(f"[red]Unknown command:[/red] '{command}'\n")
            self.console.print("[bold white]Did you mean?[/bold white]")
            self.console.print("  [cyan]list[/cyan]     - See all available missions")
            self.console.print("  [cyan]start[/cyan]    - Begin a mission")
            self.console.print("  [cyan]help[/cyan]     - Show help information")
            self.console.print("\n[dim]Type 'help' to see all commands[/dim]\n")

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
