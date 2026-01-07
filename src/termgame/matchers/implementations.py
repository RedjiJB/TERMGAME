"""Stub matcher implementations for testing.

This module provides basic matcher implementations for exact string matching,
substring matching, and file existence checking. These are simple implementations
suitable for initial testing and development.
"""

from typing import Any


class ExactMatcher:
    """Exact string match validator.

    Compares actual output against expected value for exact equality.
    """

    def matches(self, actual: str, expected: Any) -> bool:
        """Check if actual matches expected exactly.

        Args:
            actual: Actual output from command or file.
            expected: Expected value.

        Returns:
            True if actual equals expected, False otherwise.
        """
        return bool(actual == expected)


class ContainsMatcher:
    """Substring match validator.

    Checks if expected value is contained within actual output.
    """

    def matches(self, actual: str, expected: Any) -> bool:
        """Check if actual contains expected substring.

        Args:
            actual: Actual output from command or file.
            expected: Expected substring.

        Returns:
            True if expected is in actual, False otherwise.
        """
        return expected in actual


class ExistsMatcher:
    """File/directory existence validator.

    Checks if a file or directory exists based on command output.
    Expects actual to be "true" or "false" string from test command.
    """

    def matches(self, actual: str, expected: Any) -> bool:  # noqa: ARG002
        """Check if file exists.

        Args:
            actual: Output from test command ("true" or "false").
            expected: Not used for existence checks.

        Returns:
            True if actual is "true", False otherwise.
        """
        return actual == "true"
