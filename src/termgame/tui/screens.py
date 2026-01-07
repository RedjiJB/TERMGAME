"""TUI screens for TermGame application.

This module defines all screens/views used in the Textual TUI, including
mission lists, active mission displays, and progress tracking.
"""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static


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
        # TODO: Load actual mission details from scenario
        details = self.query_one("#mission-details", Static)
        details.update(
            f"Mission ID: {self.mission_id}\n\n"
            "This will create a container environment.\n"
            "Press Start to begin."
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.app.pop_screen()
        elif event.button.id == "confirm-btn":
            # TODO: Actually start the mission
            self.app.push_screen(ActiveMissionScreen(self.mission_id))


class ActiveMissionScreen(Screen[None]):
    """Screen for active mission with step-by-step guidance.

    Displays current step information, hints, and validation controls.
    """

    BINDINGS = [
        ("h", "show_hint", "Hint"),
        ("v", "validate", "Validate"),
        ("a", "abandon", "Abandon"),
    ]

    def __init__(self, mission_id: str, *args: Any, **kwargs: Any) -> None:
        """Initialize active mission screen.

        Args:
            mission_id: Mission identifier
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.mission_id = mission_id
        self.current_step = 0

    def compose(self) -> ComposeResult:
        """Compose the active mission layout."""
        yield Header()
        yield Container(
            Static(f"Mission: {self.mission_id}", classes="screen-title"),
            Vertical(
                Static("Step 1", id="step-title", classes="step-title"),
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
        # TODO: Load actual step from engine
        self._update_step_display()

    def _update_step_display(self) -> None:
        """Update the displayed step information."""
        step_title = self.query_one("#step-title", Static)
        step_desc = self.query_one("#step-description", Static)

        step_title.update(f"Step {self.current_step + 1}")
        step_desc.update(
            "This is a placeholder step.\n\n"
            "In a real mission, this would show:\n"
            "- Step instructions\n"
            "- What you need to do\n"
            "- Expected outcome"
        )

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
        hint_box = self.query_one("#hint-text", Static)
        hint_box.update("💡 Hint: This is a placeholder hint for the current step.")

    def action_validate(self) -> None:
        """Validate current step."""
        status = self.query_one("#status-message", Static)
        # TODO: Actual validation
        status.update("✓ Step validation successful! (placeholder)")
        self.current_step += 1
        self._update_step_display()

    def action_abandon(self) -> None:
        """Abandon the mission."""
        self.app.pop_screen()


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
        progress_info = self.query_one("#progress-info", Static)
        # TODO: Load actual progress from database
        progress_info.update(
            "Total XP: 0\n"
            "Missions Completed: 0\n"
            "Active Missions: 0\n\n"
            "Start a mission to begin earning XP!"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.app.pop_screen()
