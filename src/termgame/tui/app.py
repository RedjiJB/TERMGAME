"""Main Textual application for TermGame.

This module defines the main Textual app and screen management.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from termgame.config import get_config
from termgame.loaders.scenario_loader import ScenarioLoader
from termgame.tui.screens import MissionListScreen, ProgressScreen


class HomeScreen(Screen[None]):
    """Home screen with main menu options.

    Displays welcome message and navigation buttons for main features.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "missions", "Missions"),
        ("2", "progress", "Progress"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the home screen layout."""
        yield Header()
        yield Container(
            Static(
                """
╔═══════════════════════════════════════╗
║                                       ║
║           T E R M G A M E             ║
║                                       ║
║    Terminal Training Platform         ║
║                                       ║
╚═══════════════════════════════════════╝
                """,
                classes="app-title",
            ),
            Static(
                "Learn command-line skills through\n" "interactive, hands-on missions",
                classes="welcome-text",
            ),
            Vertical(
                Button("Browse Missions (1)", id="missions-btn", classes="menu-button"),
                Button("View Progress (2)", id="progress-btn", classes="menu-button"),
                Button("Quit (q)", id="quit-btn", variant="error", classes="menu-button"),
                classes="menu-container",
            ),
            classes="home-container",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "quit-btn":
            self.app.exit()
        elif event.button.id == "missions-btn":
            self.action_missions()
        elif event.button.id == "progress-btn":
            self.action_progress()

    def action_missions(self) -> None:
        """Navigate to missions screen."""
        try:
            config = get_config()
            loader = ScenarioLoader(config.scenarios_dir)

            # Load all missions
            missions: list[dict[str, str]] = []
            for scenario_file in config.scenarios_dir.rglob("*.yml"):
                if scenario_file.name.startswith("_"):
                    continue

                rel_path = scenario_file.relative_to(config.scenarios_dir)
                mission_id = str(rel_path.with_suffix("")).replace("\\", "/")

                try:
                    scenario = loader.load(mission_id)
                    missions.append(
                        {
                            "id": mission_id,
                            "title": scenario.mission.title,
                            "difficulty": scenario.mission.difficulty,
                            "time": str(scenario.mission.estimated_time),
                            "description": scenario.mission.description,
                        }
                    )
                except Exception:  # noqa: S112
                    continue

            self.app.push_screen(MissionListScreen(missions))
        except Exception as e:
            # TODO: Show error dialog
            self.notify(f"Error loading missions: {e}", severity="error")

    def action_progress(self) -> None:
        """Navigate to progress screen."""
        self.app.push_screen(ProgressScreen())


class TermGameApp(App[None]):
    """Main TermGame TUI application.

    This app provides an interactive terminal interface for navigating
    missions, viewing progress, and accessing all TermGame features.
    """

    TITLE = "TermGame"
    CSS_PATH = "app.css"

    def on_mount(self) -> None:
        """Initialize the app and show home screen."""
        self.push_screen(HomeScreen())


def run_tui() -> None:
    """Run the TermGame TUI application.

    This function is called from the CLI tui command.
    """
    app = TermGameApp()
    app.run()


if __name__ == "__main__":
    run_tui()
