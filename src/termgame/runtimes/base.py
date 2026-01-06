"""Base container runtime protocol.

Defines the interface that all container runtime implementations must follow.
"""

from typing import Protocol


class Container(Protocol):
    """Protocol for container objects."""

    id: str
    name: str


class ContainerRuntime(Protocol):
    """Protocol for container runtime implementations.

    This protocol defines the interface for Docker and Podman runtimes,
    ensuring consistent behavior across different container technologies.
    """

    async def create_container(
        self,
        image: str,
        name: str | None = None,
        **kwargs: str,
    ) -> Container:
        """Create a new container.

        Args:
            image: Container image to use.
            name: Optional container name.
            **kwargs: Additional runtime-specific arguments.

        Returns:
            Created container object.
        """
        ...

    async def execute_command(self, container: Container, command: str) -> str:
        """Execute a command in a container.

        Args:
            container: Container to execute command in.
            command: Command to execute.

        Returns:
            Command output as string.
        """
        ...

    async def stop_container(self, container: Container) -> None:
        """Stop a running container.

        Args:
            container: Container to stop.
        """
        ...

    async def remove_container(self, container: Container) -> None:
        """Remove a container.

        Args:
            container: Container to remove.
        """
        ...
