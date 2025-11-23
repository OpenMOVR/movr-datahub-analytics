"""Logging configuration utilities."""

import sys
from loguru import logger


def setup_logging(level="INFO", log_file=None):
    """
    Configure logging for MOVR package.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
    """
    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=level,
        colorize=True
    )

    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=level,
            rotation="10 MB"
        )
