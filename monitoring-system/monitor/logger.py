# ============================================================
# Monitoring System — Logger Module
# Copyright (c) 2026 Soft Game Studio
# License: MIT
#
# Professional logging with rotating file handlers,
# colorized console output via Rich, and structured
# formatting for production diagnostics.
# ============================================================

"""
logger.py — Centralized Logging System

Provides a ``get_logger(name)`` factory that returns a
pre-configured logger with:
  - RotatingFileHandler (10 MB, 5 backups)
  - Rich-formatted console handler
  - Structured format with timestamps and module names
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from rich.logging import RichHandler

# Default log directory (created on first use)
_DEFAULT_LOG_DIR = "logs"
_DEFAULT_LOG_FILE = "logs/system.log"
_MAX_BYTES = 10 * 1024 * 1024   # 10 MB per file
_BACKUP_COUNT = 5
_LOG_FORMAT = "%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Track whether we've already set up the root logger
_root_configured = False


def _ensure_log_directory(log_dir: str) -> None:
    """Create log directory if it does not exist."""
    os.makedirs(log_dir, exist_ok=True)


def setup_root_logger(
    log_dir: str = _DEFAULT_LOG_DIR,
    log_file: str = _DEFAULT_LOG_FILE,
    level: int = logging.DEBUG,
    enable_file: bool = True,
    enable_console: bool = True,
) -> None:
    """
    Configure the root logger with file and console handlers.

    This is called once at application startup. Subsequent calls
    are no-ops to prevent duplicate handlers.

    Args:
        log_dir:        Directory for log files.
        log_file:       Path to the main log file.
        level:          Minimum log level.
        enable_file:    Attach a rotating file handler.
        enable_console: Attach a Rich console handler.
    """
    global _root_configured
    if _root_configured:
        return

    _ensure_log_directory(log_dir)

    root = logging.getLogger()
    root.setLevel(level)

    # ---- File Handler (rotating) ----
    if enable_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
        )
        root.addHandler(file_handler)

    # ---- Console Handler (Rich) ----
    if enable_console:
        console_handler = RichHandler(
            level=logging.INFO,
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_path=False,
        )
        root.addHandler(console_handler)

    _root_configured = True


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a named logger.

    Ensures the root logger is configured before returning.

    Args:
        name:  Logger name (typically ``__name__``).
        level: Optional override for this logger's level.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    # Ensure root logger is set up (no-op after first call)
    setup_root_logger()

    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger