"""Container runtime abstraction layer.

This package provides an abstraction over Docker and Podman for managing
isolated sandbox environments for mission execution.
"""

from termgame.runtimes.base import ContainerRuntime
from termgame.runtimes.factory import create_runtime

__all__ = ["ContainerRuntime", "create_runtime"]
