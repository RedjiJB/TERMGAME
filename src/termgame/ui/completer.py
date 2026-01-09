"""Command completion for interactive CLI with slash command support."""

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document


class SlashCommandCompleter(Completer):
    """Completer for slash commands in interactive CLI.

    Provides autocomplete suggestions when user types '/' followed by command names.
    Similar to Claude's CLI experience.
    """

    def __init__(self, in_mission: bool = False) -> None:
        """Initialize the completer.

        Args:
            in_mission: Whether user is currently in a mission (affects available commands).
        """
        self.in_mission = in_mission

        # Commands available in lobby (outside missions)
        self.lobby_commands = {
            "list": "Show all available missions",
            "start": "Start a mission (usage: /start <mission-id>)",
            "progress": "View your XP and completed missions",
            "reset": "Reset all progress and start fresh",
            "status": "Check Docker connection health",
            "help": "Show available commands",
            "quit": "Exit TermGame",
        }

        # Commands available during missions
        self.mission_commands = {
            "validate": "Check if current step is complete",
            "hint": "Get a hint for the current step",
            "abandon": "Give up and cleanup mission container",
            "help": "Show available commands",
            "quit": "Exit TermGame",
        }

    def set_mission_mode(self, in_mission: bool) -> None:
        """Update whether user is in a mission.

        Args:
            in_mission: True if in mission, False if in lobby.
        """
        self.in_mission = in_mission

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> list[Completion]:
        """Get command completions based on current input.

        Args:
            document: Current document/input state.
            complete_event: Completion event with metadata.

        Returns:
            List of completion suggestions.
        """
        text = document.text_before_cursor

        # Don't complete if there's text that's not a command
        # (e.g., if they're typing a Linux command in mission mode)
        if text and not text.startswith("/") and " " in text:
            return []

        # Get available commands based on mode
        commands = self.mission_commands if self.in_mission else self.lobby_commands

        # Determine if using slash syntax and get search text
        using_slash = text.startswith("/")
        if using_slash:
            search_text = text[1:].lower()
        else:
            search_text = text.lower()

        completions = []
        for cmd, description in commands.items():
            # Match command prefix
            if cmd.lower().startswith(search_text):
                # Calculate how much to replace
                start_position = -len(search_text) if search_text else 0

                # Show with or without slash based on how user typed
                if using_slash:
                    display = f"/{cmd}"
                else:
                    display = cmd

                completions.append(
                    Completion(
                        text=cmd,
                        start_position=start_position,
                        display=display,
                        display_meta=description,
                    )
                )

        return completions
