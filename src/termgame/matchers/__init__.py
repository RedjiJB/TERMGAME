"""Command validation matchers.

This package provides various matchers for validating user commands and
outputs during mission execution.
"""

from termgame.matchers.base import Matcher
from termgame.matchers.implementations import ContainsMatcher, ExactMatcher, ExistsMatcher
from termgame.matchers.registry import MatcherRegistry

__all__ = [
    "ContainsMatcher",
    "ExactMatcher",
    "ExistsMatcher",
    "Matcher",
    "MatcherRegistry",
]
