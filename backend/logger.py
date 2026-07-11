"""
logger.py — Structured logging configuration for V.V. Automation Contact API

Provides a consistent, production-ready logger that:
  - Writes INFO+ to stdout (captured by Railway/Render)
  - Includes timestamps, log levels, and module names
  - Can be imported by any module: from logger import get_logger
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a named logger with a consistent format."""
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent log messages from propagating to the root logger
    logger.propagate = False

    return logger
