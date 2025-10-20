"""
Logging utility for the project.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str = "compliance_ml",
    log_file: str = None,
    level: int = logging.INFO,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.

    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level (default: INFO)
        console: Whether to log to console (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "compliance_ml") -> logging.Logger:
    """
    Get an existing logger or create a new one.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up with default config
    if not logger.handlers:
        return setup_logger(name)

    return logger


if __name__ == "__main__":
    # Test the logger
    logger = setup_logger(
        name="test_logger",
        log_file="logs/test.log",
        level=logging.DEBUG
    )

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
