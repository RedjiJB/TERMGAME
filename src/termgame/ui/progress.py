"""Progress indication for long-running operations.

This module provides user feedback during retries and other operations that
may take time, improving the user experience by showing what's happening
instead of leaving users wondering if the system is frozen.
"""

from rich.console import Console


class OperationProgress:
    """Manages progress display for runtime operations.

    Uses Rich library for formatted terminal output with colors and styling.

    Attributes:
        console: Rich console for formatted output.
    """

    def __init__(self, console: Console) -> None:
        """Initialize with a Rich console.

        Args:
            console: Rich Console instance for output.
        """
        self.console = console

    def start_operation(self, description: str) -> None:
        """Start showing progress for an operation.

        Args:
            description: Brief description of what's happening.
        """
        self.console.print(f"[dim]{description}...[/dim]")

    def update_retry(self, message: str, attempt: int, max_attempts: int) -> None:
        """Update retry progress.

        Only shows messages for retries >= 3 to avoid clutter.
        Quick recoveries (1-2 retries) happen silently.

        Args:
            message: Description of what's being retried.
            attempt: Current attempt number (1-indexed).
            max_attempts: Total number of attempts allowed.
        """
        # Only show retry messages if it's taking a while (3+ attempts)
        if attempt >= 3:
            self.console.print(f"[dim]⟳ Retry {attempt}/{max_attempts}...[/dim]")

    def end_operation(self, success: bool, message: str = "") -> None:
        """End operation display with success or failure indicator.

        Args:
            success: Whether the operation succeeded.
            message: Optional message to display.
        """
        if success:
            self.console.print(f"[green]✓[/green] {message or 'Complete'}")
        else:
            self.console.print(f"[red]✗[/red] {message or 'Failed'}")
