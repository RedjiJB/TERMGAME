"""Matcher registry for looking up matchers by type.

This module provides a registry pattern for managing different
matcher implementations used in mission step validation.
"""

from termgame.matchers.base import Matcher


class MatcherRegistry:
    """Registry for matcher implementations.

    The registry allows dynamic registration and retrieval of matcher
    classes by name, enabling extensible validation strategies.
    """

    def __init__(self) -> None:
        """Initialize empty matcher registry."""
        self._matchers: dict[str, type[Matcher]] = {}

    def register(self, name: str, matcher_class: type[Matcher]) -> None:
        """Register a matcher implementation.

        Args:
            name: Matcher name (e.g., 'exact', 'contains', 'regex').
            matcher_class: Matcher class implementing the Matcher protocol.
        """
        self._matchers[name] = matcher_class

    def get(self, name: str) -> type[Matcher]:
        """Get matcher class by name.

        Args:
            name: Matcher name.

        Returns:
            Matcher class.

        Raises:
            KeyError: If matcher not registered.
        """
        if name not in self._matchers:
            msg = f"Matcher not registered: {name}"
            raise KeyError(msg)
        return self._matchers[name]

    def create(self, name: str) -> Matcher:
        """Create matcher instance by name.

        Args:
            name: Matcher name.

        Returns:
            Matcher instance.

        Raises:
            KeyError: If matcher not registered.
        """
        matcher_class = self.get(name)
        return matcher_class()
