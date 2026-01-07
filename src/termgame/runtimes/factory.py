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
        from termgame.runtimes.docker_runtime import DockerRuntime

        return DockerRuntime()
    if runtime_type == "podman":
        # TODO: Import and return PodmanRuntime
        msg = "Podman runtime not yet implemented"
        raise NotImplementedError(msg)
    msg = f"Unsupported runtime type: {runtime_type}"
    raise ValueError(msg)
