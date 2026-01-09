"""Factory for creating container runtime instances."""

from collections.abc import Callable
from typing import Any

from termgame.runtimes.base import ContainerRuntime

# Type alias for progress callback
ProgressCallback = Callable[[str, int, int], None]


def create_runtime(
    runtime_type: str = "docker",
    config: Any = None,  # Config type (avoid circular import)
    progress_callback: ProgressCallback | None = None,
) -> ContainerRuntime:
    """Create a container runtime instance.

    Args:
        runtime_type: Type of runtime to create ('docker' or 'podman').
        config: Optional Config object with runtime settings.
        progress_callback: Optional callback for progress updates during retries.

    Returns:
        ContainerRuntime instance.

    Raises:
        ValueError: If runtime_type is not supported.
    """
    if runtime_type == "docker":
        from termgame.runtimes.docker_runtime import DockerRuntime

        return DockerRuntime(
            config=config,
            progress_callback=progress_callback,
        )
    if runtime_type == "podman":
        # TODO: Import and return PodmanRuntime
        msg = "Podman runtime not yet implemented"
        raise NotImplementedError(msg)
    msg = f"Unsupported runtime type: {runtime_type}"
    raise ValueError(msg)
