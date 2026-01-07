"""TUI screens for TermGame application.

This module defines all screens/views used in the Textual TUI, including
mission lists, active mission displays, and progress tracking.
"""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

from termgame.tui.engine_wrapper import get_engine_wrapper


class MissionListScreen(Screen[None]):
    """Screen displaying available missions.

    Shows a table of all available missions with their metadata,
    allowing users to select and start missions.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(
        self,
        missions: list[dict[str, str]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize mission list screen.

        Args:
            missions: List of mission dictionaries with id, title, difficulty, etc.
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.missions = missions

    def compose(self) -> ComposeResult:
        """Compose the mission list layout."""
        yield Header()
        yield Container(
            Static("Available Missions", classes="screen-title"),
            DataTable(id="missions-table"),
            Horizontal(
                Button("Start Mission", id="start-btn", variant="primary"),
                Button("Back", id="back-btn"),
                classes="button-row",
            ),
            classes="mission-list-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the missions table when screen mounts."""
        table = self.query_one("#missions-table", DataTable)
        table.add_columns("ID", "Title", "Difficulty", "Time", "Description")
        table.cursor_type = "row"

        for mission in self.missions:
            table.add_row(
                mission.get("id", ""),
                mission.get("title", ""),
                mission.get("difficulty", ""),
                f"{mission.get('time', 0)} min",
                mission.get("description", "")[:50] + "...",
                key=mission.get("id", ""),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.app.pop_screen()
        elif event.button.id == "start-btn":
            table = self.query_one("#missions-table", DataTable)
            if table.cursor_row >= 0:
                mission_id = str(table.get_row_at(table.cursor_row)[0])
                self.app.push_screen(MissionStartScreen(mission_id))


class MissionStartScreen(Screen[None]):
    """Screen for starting a mission.

    Shows mission details and confirmation before initializing
    the container environment.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, mission_id: str, *args: Any, **kwargs: Any) -> None:
        """Initialize mission start screen.

        Args:
            mission_id: Mission identifier
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.mission_id = mission_id
        self._starting = False

    def compose(self) -> ComposeResult:
        """Compose the mission start layout."""
        yield Header()
        yield Container(
            Static(f"Mission: {self.mission_id}", classes="screen-title"),
            Static("Loading mission details...", id="mission-details"),
            Horizontal(
                Button("Start", id="confirm-btn", variant="primary"),
                Button("Cancel", id="cancel-btn"),
                classes="button-row",
            ),
            classes="mission-start-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load mission details when screen mounts."""
        # Load mission details from scenario
        details = self.query_one("#mission-details", Static)
        details.update(
            f"Mission ID: {self.mission_id}\n\n"
            "This will create a Docker/Podman container environment.\n"
            "The container will be automatically cleaned up when done.\n\n"
            "Press Start to begin, or Cancel to go back."
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.app.pop_screen()
        elif event.button.id == "confirm-btn" and not self._starting:
            self._starting_mission()

    def _starting_mission(self) -> None:
        """Start the mission asynchronously."""
        self._starting = True
        # Update UI
        self.query_one("#mission-details", Static).update("Starting mission...")
        self.query_one("#confirm-btn", Button).disabled = True

        # Start mission in background
        self.run_worker(self._start_mission_async())

    async def _start_mission_async(self) -> None:
        """Async worker to start mission."""
        try:
            wrapper = get_engine_wrapper()
            await wrapper.initialize()

            result = await wrapper.start_mission(self.mission_id)

            if result["success"]:
                # Navigate to active mission screen
                self.app.call_from_thread(self.app.pop_screen)  # Remove this screen
                self.app.call_from_thread(
                    self.app.push_screen,
                    ActiveMissionScreen(self.mission_id, result["step"]),
                )
            else:
                self.app.call_from_thread(
                    self.notify,
                    f"Failed to start mission: {result.get('error', 'Unknown error')}",
                    severity="error",
                )
                self._starting = False
                self.query_one("#confirm-btn", Button).disabled = False

        except Exception as e:
            self.app.call_from_thread(
                self.notify,
                f"Error starting mission: {e}",
                severity="error",
            )
            self._starting = False
            self.query_one("#confirm-btn", Button).disabled = False


class ActiveMissionScreen(Screen[None]):
    """Screen for active mission with step-by-step guidance.

    Displays current step information, hints, and validation controls.
    """

    BINDINGS = [
        ("h", "show_hint", "Hint"),
        ("v", "validate", "Validate"),
        ("a", "abandon", "Abandon"),
    ]

    def __init__(
        self,
        mission_id: str,
        step_info: dict[str, Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize active mission screen.

        Args:
            mission_id: Mission identifier
            step_info: Current step information
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.mission_id = mission_id
        self.step_info = step_info
        self._validating = False

    def compose(self) -> ComposeResult:
        """Compose the active mission layout."""
        yield Header()
        yield Container(
            Static(f"Mission: {self.mission_id}", classes="screen-title"),
            Vertical(
                Static("Loading...", id="step-title", classes="step-title"),
                Static("Loading...", id="step-description"),
                Static("", id="hint-text", classes="hint-box"),
                classes="step-info",
            ),
            Horizontal(
                Button("Show Hint (h)", id="hint-btn", variant="default"),
                Button("Validate (v)", id="validate-btn", variant="primary"),
                Button("Abandon (a)", id="abandon-btn", variant="error"),
                classes="button-row",
            ),
            Static("", id="status-message", classes="status"),
            classes="active-mission-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load current step when screen mounts."""
        self._update_step_display()

    def _update_step_display(self) -> None:
        """Update the displayed step information."""
        step_title = self.query_one("#step-title", Static)
        step_desc = self.query_one("#step-description", Static)
        hint_box = self.query_one("#hint-text", Static)

        step_num = int(self.step_info.get("index", 0)) + 1
        step_title.update(f"Step {step_num}: {self.step_info.get('title', 'Unknown')}")
        step_desc.update(self.step_info.get("description", "No description available"))
        hint_box.update("")  # Clear hint

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "abandon-btn":
            self.action_abandon()
        elif event.button.id == "hint-btn":
            self.action_show_hint()
        elif event.button.id == "validate-btn":
            self.action_validate()

    def action_show_hint(self) -> None:
        """Show hint for current step."""
        self.run_worker(self._get_hint_async())

    async def _get_hint_async(self) -> None:
        """Async worker to get hint."""
        try:
            wrapper = get_engine_wrapper()
            hint = await wrapper.get_hint(self.mission_id)

            if hint:
                self.app.call_from_thread(
                    self.query_one("#hint-text", Static).update,
                    f"💡 Hint: {hint}",
                )
            else:
                self.app.call_from_thread(
                    self.query_one("#hint-text", Static).update,
                    "No hint available for this step.",
                )
        except Exception as e:
            self.app.call_from_thread(
                self.notify,
                f"Error getting hint: {e}",
                severity="error",
            )

    def action_validate(self) -> None:
        """Validate current step."""
        if not self._validating:
            self._validating = True
            self.query_one("#validate-btn", Button).disabled = True
            self.query_one("#status-message", Static).update("Validating...")
            self.run_worker(self._validate_async())

    async def _validate_async(self) -> None:
        """Async worker to validate step."""
        try:
            wrapper = get_engine_wrapper()
            result = await wrapper.validate_step(self.mission_id)

            if result["success"]:
                if result.get("completed"):
                    # Mission complete!
                    xp = result.get("xp_earned", 0)
                    self.app.call_from_thread(
                        self.notify,
                        f"🎉 Mission Complete! You earned {xp} XP!",
                        severity="information",
                    )
                    self.app.call_from_thread(self.app.pop_screen)
                else:
                    # Move to next step
                    next_step = result.get("next_step")
                    if next_step:
                        self.step_info = next_step
                        self.app.call_from_thread(self._update_step_display)
                        self.app.call_from_thread(
                            self.query_one("#status-message", Static).update,
                            f"✓ {result.get('message', 'Step complete!')}",
                        )
            else:
                self.app.call_from_thread(
                    self.query_one("#status-message", Static).update,
                    f"✗ {result.get('message', 'Validation failed')}",
                )

        except Exception as e:
            self.app.call_from_thread(
                self.notify,
                f"Validation error: {e}",
                severity="error",
            )
        finally:
            self._validating = False
            self.app.call_from_thread(
                lambda: self.query_one("#validate-btn", Button)
            ).disabled = False

    def action_abandon(self) -> None:
        """Abandon the mission."""
        self.run_worker(self._abandon_async())

    async def _abandon_async(self) -> None:
        """Async worker to abandon mission."""
        try:
            wrapper = get_engine_wrapper()
            success = await wrapper.abandon_mission(self.mission_id)

            if success:
                self.app.call_from_thread(
                    self.notify,
                    "Mission abandoned. Progress saved.",
                    severity="warning",
                )
                self.app.call_from_thread(self.app.pop_screen)
            else:
                self.app.call_from_thread(
                    self.notify,
                    "Failed to abandon mission",
                    severity="error",
                )

        except Exception as e:
            self.app.call_from_thread(
                self.notify,
                f"Error abandoning mission: {e}",
                severity="error",
            )


class ProgressScreen(Screen[None]):
    """Screen showing user progress and statistics.

    Displays completed missions, XP earned, and achievements.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the progress screen layout."""
        yield Header()
        yield Container(
            Static("Your Progress", classes="screen-title"),
            Static("Loading progress...", id="progress-info"),
            Button("Back", id="back-btn"),
            classes="progress-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load progress when screen mounts."""
        self.run_worker(self._load_progress_async())

    async def _load_progress_async(self) -> None:
        """Async worker to load progress."""
        try:
            wrapper = get_engine_wrapper()
            await wrapper.initialize()
            progress = await wrapper.get_progress()

            progress_text = (
                f"Total XP: {progress.get('total_xp', 0)}\n"
                f"Missions Completed: {progress.get('missions_completed', 0)}\n"
                f"Active Missions: {progress.get('active_missions', 0)}\n\n"
            )

            if progress.get("missions_completed", 0) == 0:
                progress_text += "Start a mission to begin earning XP!"

            self.app.call_from_thread(
                self.query_one("#progress-info", Static).update,
                progress_text,
            )

        except Exception as e:
            self.app.call_from_thread(
                self.query_one("#progress-info", Static).update,
                f"Error loading progress: {e}",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.app.pop_screen()
