"""Factory for creating container runtime instances."""

from termgame.runtimes.base import ContainerRuntime


def create_runtime(runtime_type: str = "docker") -> ContainerRuntime:
    """Create a container runtime instance.

    Args:
        runtime_type: Type of runtime to create ('docker' or 'podman').

    Returns:
        ContainerRuntime instance.

    Raises:
        ValueError: If runtime_type is not supported.
    """
    if runtime_type == "docker":
        # TODO: Import and return DockerRuntime
        msg = "Docker runtime not yet implemented"
        raise NotImplementedError(msg)
    elif runtime_type == "podman":
        # TODO: Import and return PodmanRuntime
        msg = "Podman runtime not yet implemented"
        raise NotImplementedError(msg)
    else:
        msg = f"Unsupported runtime type: {runtime_type}"
        raise ValueError(msg)
