"""Container runtime abstraction layer.

This package provides an abstraction over Docker and Podman for managing
isolated sandbox environments for mission execution.
"""

from termgame.runtimes.base import Container, ContainerRuntime
from termgame.runtimes.docker_runtime import DockerContainer, DockerRuntime
from termgame.runtimes.factory import create_runtime

__all__ = [
    "Container",
    "ContainerRuntime",
    "DockerContainer",
    "DockerRuntime",
    "create_runtime",
]
