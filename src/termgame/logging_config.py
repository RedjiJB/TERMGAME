"""Logging configuration for TermGame.

This module sets up structured logging with both file and console output.
Configuration is controlled via environment variables.
"""

import logging
import os
import sys
from pathlib import Path


def setup_logging() -> None:
    """Configure application-wide logging.

    Sets up dual logging handlers:
    - Console handler: ERROR and above to stderr (transient warnings hidden)
    - File handler: All messages to log file based on configured level

    Environment variables:
        TERMGAME_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
            Default: INFO
        TERMGAME_LOG_FILE: Path to log file
            Default: ~/.termgame/termgame.log

    The log directory is created automatically if it doesn't exist.
    """
    # Get configuration from environment
    level = os.getenv("TERMGAME_LOG_LEVEL", "INFO")
    log_file_path = os.getenv("TERMGAME_LOG_FILE")

    # Default log file location if not specified
    if not log_file_path:
        log_dir = Path.home() / ".termgame"
        log_dir.mkdir(exist_ok=True)
        log_file_path = str(log_dir / "termgame.log")

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler - only errors to avoid cluttering user output
    # Transient warnings (retries) should not be shown to users
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)

    # File handler - all messages at configured level
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    file_handler.setFormatter(formatter)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=[console_handler, file_handler],
        force=True,  # Override any existing configuration
    )

    # Reduce noise from third-party libraries
    logging.getLogger("docker").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Log successful setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={level}, file={log_file_path}")
