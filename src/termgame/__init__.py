"""TermGame - Terminal-based CLI training platform.

A gamified learning environment for teaching Linux, Cisco IOS, and PowerShell
skills through interactive missions and challenges.
"""

__version__ = "0.1.0"
__author__ = "Redji Jean Baptiste"
__email__ = "jean0319@algonquinlive.com"

from termgame.models.mission import Mission
from termgame.models.scenario import Scenario

__all__ = ["Mission", "Scenario", "__version__"]
