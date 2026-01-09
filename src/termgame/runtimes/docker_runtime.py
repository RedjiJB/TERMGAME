"""Docker-based container runtime implementation.

This module provides a concrete implementation of the ContainerRuntime protocol
using the official Docker SDK for Python. It wraps blocking Docker SDK calls
in asyncio.to_thread() to enable non-blocking async/await usage.

Enhanced with retry logic, circuit breaker pattern, and comprehensive error handling.
"""

import asyncio
import http.client
import logging
import shlex
import time
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from typing import Any

import docker
import docker.errors
from docker.models.containers import Container as DockerSDKContainer

from termgame.runtimes.base import Container
from termgame.runtimes.exceptions import (
    ConnectionError as RuntimeConnectionError,
)
from termgame.runtimes.exceptions import (
    ContainerNotFoundError,
    ImagePullError,
)
from termgame.runtimes.health import HealthCheck

# Type alias for progress callback
ProgressCallback = Callable[[str, int, int], None]


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

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = 300,
        progress_callback: ProgressCallback | None = None,
        config: Any = None,  # Config type (avoid circular import)
    ) -> None:
        """Initialize Docker client with enhanced reliability features.

        Args:
            base_url: Docker daemon URL. If None, uses Docker's default
                (unix:///var/run/docker.sock on Linux/macOS, npipe on Windows).
            timeout: Timeout in seconds for API calls (default: 300 = 5 minutes).
            progress_callback: Optional callback for progress updates during retries.
                Called with (message, attempt, max_attempts).
            config: Optional Config object with retry and circuit breaker settings.
        """
        self._client = docker.DockerClient(base_url=base_url, timeout=timeout)

        # Initialize health check/circuit breaker
        max_failures = getattr(config, "circuit_breaker_max_failures", 5) if config else 5
        circuit_timeout = getattr(config, "circuit_breaker_timeout", 30.0) if config else 30.0
        self._health = HealthCheck(
            max_failures=max_failures,
            circuit_timeout=circuit_timeout,
        )

        # Store configuration
        self._progress_callback = progress_callback
        self._config = config

        # Setup logging
        self._logger = logging.getLogger(__name__)

    def _validate_connection(self) -> bool:
        """Validate Docker daemon connection is alive.

        Returns:
            True if connection is healthy, False otherwise.
        """
        try:
            self._client.ping()
            return True
        except Exception:
            return False

    def _report_progress(self, message: str, attempt: int, max_attempts: int) -> None:
        """Report retry progress to callback if configured.

        Args:
            message: Progress message describing what's happening.
            attempt: Current attempt number (1-indexed).
            max_attempts: Total number of attempts allowed.
        """
        if self._progress_callback:
            self._progress_callback(message, attempt, max_attempts)

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
            self._logger.info(f"Creating container from image: {image}")

            # If a container with the requested name already exists, remove it
            if name:
                try:
                    existing = self._client.containers.get(name)
                    self._logger.debug(f"Removing existing container: {name}")
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
            # Use 'tail -f /dev/null' as command to keep container alive
            try:
                container: DockerSDKContainer = self._client.containers.create(
                    image=image,
                    name=name,
                    command="tail -f /dev/null",
                    working_dir=working_dir,
                    detach=True,
                    tty=True,
                    stdin_open=True,
                    **kwargs,
                )
            except docker.errors.ImageNotFound as e:
                self._logger.error(f"Image not found: {image}")
                raise ImagePullError(f"Failed to pull image: {image}") from e

            # Start the container
            container.start()
            # Docker SDK guarantees id is set for created containers
            assert container.id is not None
            self._logger.info(f"Container created: {container.id[:12]}")
            return container

        sdk_container = await asyncio.to_thread(_create)
        # Docker SDK guarantees id and name are set for created containers
        assert sdk_container.id is not None
        assert sdk_container.name is not None
        return DockerContainer(id=sdk_container.id, name=sdk_container.name)

    async def execute_command(self, container: Container, command: str) -> str:
        """Execute a shell command in the container with enhanced retry logic.

        Commands are wrapped in "sh -c" for portability across different container images.
        Implements exponential backoff retry with circuit breaker protection.

        Args:
            container: Container to execute command in.
            command: Shell command to execute.

        Returns:
            Command stdout and stderr as a string (utf-8 decoded).

        Raises:
            RuntimeConnectionError: If connection to Docker daemon fails after all retries.
            ContainerNotFoundError: If container doesn't exist (permanent failure).
        """
        # Circuit breaker check
        if not self._health.should_attempt():
            raise RuntimeConnectionError(
                "Circuit breaker open: Too many recent failures. "
                "Docker daemon may be down. Please check: docker ps"
            )

        # Get retry configuration
        max_retries = getattr(self._config, "max_retries", 5) if self._config else 5
        base_delay = getattr(self._config, "retry_base_delay", 1.0) if self._config else 1.0
        max_delay = getattr(self._config, "retry_max_delay", 10.0) if self._config else 10.0

        def _exec() -> str:
            for attempt in range(max_retries):
                # Validate connection before retry (skip on first attempt)
                if attempt > 0:
                    self._report_progress(
                        "Reconnecting to Docker daemon",
                        attempt + 1,
                        max_retries,
                    )

                    if not self._validate_connection():
                        # Connection still down, try backoff or fail
                        if attempt < max_retries - 1:
                            # More retries available, backoff and continue
                            delay = min(base_delay * (2**attempt), max_delay)
                            jitter = delay * 0.1 * (2 * time.time() % 1 - 0.5)
                            time.sleep(delay + jitter)
                            continue
                        # Out of retries
                        self._health.record_failure()
                        self._logger.error("Docker daemon unreachable after all retries")
                        raise RuntimeConnectionError(
                            f"Failed to execute command after {max_retries} attempts. "
                            "Docker daemon unreachable. Try: docker ps"
                        )

                try:
                    # Get fresh container reference
                    sdk_container: DockerSDKContainer = self._client.containers.get(container.id)

                    # Execute command (use sh for portability)
                    wrapped_cmd = f"sh -c {shlex.quote(command)}"
                    result = sdk_container.exec_run(wrapped_cmd, tty=False, demux=False)

                    # Decode output
                    output: bytes = result.output if result.output else b""
                    decoded = output.decode("utf-8", errors="replace")

                    # Success!
                    self._health.record_success()
                    self._logger.debug(f"Command executed successfully: {command[:50]}...")

                    # Include exit code info if command failed with no output
                    if result.exit_code != 0 and not decoded:
                        return f"Command exited with code {result.exit_code}"
                    return decoded

                except docker.errors.NotFound:
                    # Container gone - permanent failure, don't retry
                    self._logger.error(f"Container not found: {container.id}")
                    raise ContainerNotFoundError(
                        f"Container {container.name} no longer exists. "
                        "It may have been stopped or removed."
                    )

                except (
                    docker.errors.APIError,
                    http.client.RemoteDisconnected,
                    ConnectionResetError,
                    BrokenPipeError,
                    OSError,  # Catches socket errors and connection failures
                ) as e:
                    # Transient connection errors - retry with backoff
                    self._logger.warning(
                        f"Connection error on attempt {attempt + 1}/{max_retries}: {e}"
                    )

                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = min(base_delay * (2**attempt), max_delay)
                        jitter = delay * 0.1 * (2 * time.time() % 1 - 0.5)
                        time.sleep(delay + jitter)
                        continue

                    # Out of retries
                    self._health.record_failure()
                    self._logger.error(f"Failed after {max_retries} attempts: {e}")
                    raise RuntimeConnectionError(
                        f"Failed to execute command after {max_retries} attempts. "
                        "Docker daemon may be unresponsive. Try: docker ps"
                    ) from e

                except Exception as e:
                    # Unexpected error
                    self._logger.error(f"Unexpected error: {e}", exc_info=True)
                    raise RuntimeError(f"Unexpected error: {e}") from e

            return ""  # Should never reach here

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
