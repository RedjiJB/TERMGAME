"""Base matcher protocol and common matcher implementations."""

from typing import Any, Protocol


class Matcher(Protocol):
    """Protocol for validation matchers.

    Matchers validate whether user commands or outputs meet specific criteria
    defined in mission scenarios.
    """

    def matches(self, actual: str, expected: Any) -> bool:
        """Check if actual value matches expected criteria.

        Args:
            actual: Actual value to validate.
            expected: Expected value or pattern.

        Returns:
            True if actual matches expected.
        """
        ...
