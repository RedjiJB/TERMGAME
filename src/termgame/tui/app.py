"""Main Textual application for TermGame.

This module defines the main Textual app and screen management.
"""

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class TermGameApp(App[None]):
    """Main TermGame TUI application.

    This app provides an interactive terminal interface for navigating
    missions, viewing progress, and accessing all TermGame features.
    """

    TITLE = "TermGame"
    CSS_PATH = "app.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the application layout.

        Yields:
            Widget components for the app layout.
        """
        yield Header()
        # TODO: Add main content area
        yield Footer()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = TermGameApp()
    app.run()
