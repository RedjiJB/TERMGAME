"""Docker-based container runtime implementation.

This module provides a concrete implementation of the ContainerRuntime protocol
using the official Docker SDK for Python. It wraps blocking Docker SDK calls
in asyncio.to_thread() to enable non-blocking async/await usage.
"""

import asyncio
import shlex
from contextlib import suppress
from dataclasses import dataclass
from typing import Any

import docker
import docker.errors
from docker.models.containers import Container as DockerSDKContainer

from termgame.runtimes.base import Container


@dataclass
class DockerContainer:
    """Docker container wrapper implementing Container protocol.

    Attributes:
        id: Unique container identifier.
        name: Container name.
    """

    id: str
    name: str


class DockerRuntime:
    """Docker-based container runtime implementation.

    Uses the official Docker SDK to create, manage, and execute commands
    in Docker containers. All blocking Docker SDK calls are wrapped in
    asyncio.to_thread() for async compatibility.

    Example:
        >>> runtime = DockerRuntime()
        >>> container = await runtime.create_container("alpine:latest")
        >>> output = await runtime.execute_command(container, "echo 'Hello'")
        >>> await runtime.remove_container(container)
    """

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize Docker client.

        Args:
            base_url: Docker daemon URL. If None, uses Docker's default
                (unix:///var/run/docker.sock on Linux/macOS, npipe on Windows).
        """
        self._client = docker.DockerClient(base_url=base_url)

    async def create_container(
        self,
        image: str,
        name: str | None = None,
        working_dir: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Container:
        """Create and start a Docker container.

        The container is created with tty=True and stdin_open=True to support
        interactive commands. Docker will automatically pull the image if not
        present locally.

        Args:
            image: Docker image name (e.g., "alpine:latest", "ubuntu:22.04").
            name: Optional container name. If None, Docker assigns a random name.
            working_dir: Working directory inside container (e.g., "/home/learner").
                If None, uses image default (typically /root or /).
            **kwargs: Additional arguments passed to docker.containers.create().

        Returns:
            DockerContainer instance with id and name.

        Raises:
            docker.errors.APIError: If container creation or start fails.
            docker.errors.ImageNotFound: If image cannot be pulled.
        """

        def _create() -> DockerSDKContainer:
            # If a container with the requested name already exists, remove it
            if name:
                try:
                    existing = self._client.containers.get(name)
                    try:
                        existing.remove(force=True)
                    except Exception:
                        # Best-effort: if removal fails, try stop then remove
                        with suppress(Exception):
                            existing.stop(timeout=5)
                        with suppress(Exception):
                            existing.remove(force=True)
                except docker.errors.NotFound:
                    # No existing container with this name
                    pass

            # Create container with interactive TTY support
            container: DockerSDKContainer = self._client.containers.create(
                image=image,
                name=name,
                working_dir=working_dir,
                detach=True,
                tty=True,
                stdin_open=True,
                **kwargs,
            )
            # Start the container
            container.start()
            return container

        sdk_container = await asyncio.to_thread(_create)
        # Docker SDK guarantees id and name are set for created containers
        assert sdk_container.id is not None
        assert sdk_container.name is not None
        return DockerContainer(id=sdk_container.id, name=sdk_container.name)

    async def execute_command(self, container: Container, command: str) -> str:
        """Execute a shell command in the container.

        Commands are wrapped in "bash -c" to support shell features like
        pipes, redirects, and environment variable expansion.

        Args:
            container: Container to execute command in.
            command: Shell command to execute.

        Returns:
            Command stdout as a string (utf-8 decoded).

        Raises:
            docker.errors.NotFound: If container doesn't exist.
            docker.errors.APIError: If command execution fails.
        """

        def _exec() -> str:
            sdk_container: DockerSDKContainer = self._client.containers.get(container.id)
            # Use sh -c for portability (Alpine and minimal images)
            wrapped_cmd = f"sh -c {shlex.quote(command)}"
            result = sdk_container.exec_run(wrapped_cmd, tty=False, demux=False)
            # Decode bytes to string - result.output is bytes
            output: bytes = result.output
            return output.decode("utf-8")

        return await asyncio.to_thread(_exec)

    async def stop_container(self, container: Container) -> None:
        """Stop a running container.

        This is a best-effort operation that silently ignores errors.
        If the container is already stopped or doesn't exist, no exception
        is raised.

        Args:
            container: Container to stop.
        """

        def _stop() -> None:
            try:
                sdk_container = self._client.containers.get(container.id)
                sdk_container.stop(timeout=10)
            except docker.errors.NotFound:
                # Already removed
                pass
            except Exception:
                # Best-effort cleanup - swallow all errors
                pass

        await asyncio.to_thread(_stop)

    async def remove_container(self, container: Container) -> None:
        """Remove a container.

        This is a best-effort operation that silently ignores errors.
        If the container doesn't exist, no exception is raised. The force=True
        flag ensures the container is stopped before removal.

        Args:
            container: Container to remove.
        """

        def _remove() -> None:
            try:
                sdk_container = self._client.containers.get(container.id)
                sdk_container.remove(force=True)
            except docker.errors.NotFound:
                # Already removed
                pass
            except Exception:
                # Best-effort cleanup - swallow all errors
                pass

        await asyncio.to_thread(_remove)
