"""Connection health monitoring and circuit breaker.

This module implements a circuit breaker pattern to prevent hammering a dead
or unresponsive Docker daemon with repeated connection attempts.
"""

import time
from dataclasses import dataclass


@dataclass
class HealthCheck:
    """Tracks connection health and implements circuit breaker pattern.

    The circuit breaker opens after a configured number of consecutive failures,
    preventing further attempts until a timeout period has elapsed. This gives
    the Docker daemon time to recover and prevents cascading failures.

    Attributes:
        last_success: Timestamp of last successful operation.
        consecutive_failures: Count of failures since last success.
        circuit_open: Whether the circuit breaker is currently open.
        max_failures: Number of failures before opening circuit.
        circuit_timeout: Seconds to wait before allowing retry when circuit is open.
    """

    last_success: float = 0.0
    consecutive_failures: int = 0
    circuit_open: bool = False

    # Configurable via environment variables or runtime parameters
    max_failures: int = 5
    circuit_timeout: float = 30.0  # seconds

    def record_success(self) -> None:
        """Record a successful operation.

        Resets the failure count and closes the circuit breaker.
        """
        self.last_success = time.time()
        self.consecutive_failures = 0
        self.circuit_open = False

    def record_failure(self) -> None:
        """Record a failed operation.

        Increments the failure count and opens the circuit if the threshold
        is reached.
        """
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.max_failures:
            self.circuit_open = True

    def should_attempt(self) -> bool:
        """Check if an operation should be attempted.

        Returns:
            True if the operation should proceed, False if circuit is open
            and timeout has not elapsed.
        """
        if not self.circuit_open:
            return True

        # Check if circuit timeout has elapsed
        time_since_last_success = time.time() - self.last_success
        if time_since_last_success > self.circuit_timeout:
            # Reset circuit and allow attempt
            self.circuit_open = False
            self.consecutive_failures = 0
            return True

        return False
