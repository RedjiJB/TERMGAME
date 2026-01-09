"""Runtime-specific exceptions for container operations.

This module provides a hierarchy of exceptions for container runtime operations,
with a distinction between transient (retry-able) and permanent errors.
"""


class RuntimeError(Exception):
    """Base exception for runtime errors.

    Attributes:
        transient: Whether this error is transient and retry might succeed.
            True for connection issues, temporary resource constraints.
            False for permanent failures like missing containers.
    """

    def __init__(self, message: str, transient: bool = False) -> None:
        super().__init__(message)
        self.transient = transient


class ConnectionError(RuntimeError):
    """Docker daemon connection failed.

    Raised when unable to communicate with the Docker daemon. This is typically
    a transient error caused by network issues, daemon restarts, or resource
    exhaustion.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message, transient=True)


class ContainerNotFoundError(RuntimeError):
    """Container no longer exists.

    Raised when attempting to interact with a container that has been stopped
    or removed. This is a permanent error that cannot be resolved by retrying.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message, transient=False)


class CommandTimeoutError(RuntimeError):
    """Command execution timed out.

    Raised when a command takes longer than the allowed timeout. This may be
    transient if the container is temporarily overloaded.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message, transient=True)


class ImagePullError(RuntimeError):
    """Failed to pull container image.

    Raised when the Docker daemon cannot pull or find the specified image.
    This may be transient if caused by network issues.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message, transient=True)
