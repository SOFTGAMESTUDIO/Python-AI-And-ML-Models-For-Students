# ============================================================
# Monitoring System — Utility Functions
# Copyright (c) 2026 Soft Game Studio
# License: MIT
#
# Cross-platform helpers for Npcap detection, admin checks,
# retry logic, and formatting utilities.
# ============================================================

"""
utils.py — Shared Utility Functions

Provides:
  - Npcap / libpcap installation detection
  - Administrator / root privilege checks
  - Platform information gathering
  - Retry decorator with exponential backoff
  - Byte and duration formatting helpers
"""

import os
import sys
import time
import platform
import functools
import asyncio
from typing import Any, Callable, Dict, Optional, Tuple

from monitor.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# PLATFORM DETECTION
# ============================================================

def get_platform_info() -> Dict[str, str]:
    """
    Gather information about the current platform.

    Returns:
        Dictionary with keys: os, os_version, architecture,
        python_version, hostname.
    """
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
    }


def is_windows() -> bool:
    """Check if the current OS is Windows."""
    return platform.system().lower() == "windows"


def is_linux() -> bool:
    """Check if the current OS is Linux."""
    return platform.system().lower() == "linux"


# ============================================================
# ADMIN / ROOT DETECTION
# ============================================================

def is_admin() -> bool:
    """
    Check if the current process has administrator (Windows)
    or root (Linux/macOS) privileges.

    Packet sniffing requires elevated privileges on most systems.

    Returns:
        True if running as admin/root, False otherwise.
    """
    try:
        if is_windows():
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            return os.geteuid() == 0
    except (AttributeError, OSError):
        return False


# ============================================================
# NPCAP / WINPCAP / LIBPCAP DETECTION
# ============================================================

def check_npcap_installed() -> Tuple[bool, str]:
    """
    Detect whether Npcap (Windows) or libpcap (Linux) is
    installed and available for packet capture.

    Returns:
        Tuple of (is_installed, message).
    """
    if is_windows():
        return _check_npcap_windows()
    elif is_linux():
        return _check_libpcap_linux()
    else:
        return False, f"Unsupported platform: {platform.system()}"


def _check_npcap_windows() -> Tuple[bool, str]:
    """Check for Npcap or WinPcap on Windows via registry and filesystem."""
    # Method 1: Check Npcap installation directory
    npcap_dir = os.path.join(
        os.environ.get("SystemRoot", r"C:\Windows"),
        "System32", "Npcap"
    )
    if os.path.isdir(npcap_dir):
        return True, "Npcap found in System32"

    # Method 2: Check registry for Npcap
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Npcap"
        )
        winreg.CloseKey(key)
        return True, "Npcap found in registry"
    except (FileNotFoundError, OSError):
        pass

    # Method 3: Check for WinPcap (legacy)
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WinPcap"
        )
        winreg.CloseKey(key)
        return True, "WinPcap (legacy) found in registry"
    except (FileNotFoundError, OSError):
        pass

    # Method 4: Check for wpcap.dll
    sys32 = os.path.join(
        os.environ.get("SystemRoot", r"C:\Windows"),
        "System32"
    )
    if os.path.isfile(os.path.join(sys32, "wpcap.dll")):
        return True, "wpcap.dll found in System32"

    return False, (
        "Npcap/WinPcap is NOT installed.\n"
        "  → Download Npcap: https://npcap.com/#download\n"
        "  → Install with 'WinPcap API-compatible mode' enabled.\n"
        "  → Restart your terminal after installation."
    )


def _check_libpcap_linux() -> Tuple[bool, str]:
    """Check for libpcap on Linux."""
    import shutil

    # Check for tcpdump (requires libpcap)
    if shutil.which("tcpdump"):
        return True, "libpcap available (tcpdump found)"

    # Check for library files
    lib_paths = [
        "/usr/lib/libpcap.so",
        "/usr/lib64/libpcap.so",
        "/usr/lib/x86_64-linux-gnu/libpcap.so",
    ]
    for path in lib_paths:
        if os.path.exists(path):
            return True, f"libpcap found at {path}"

    return False, (
        "libpcap is NOT installed.\n"
        "  → Ubuntu/Debian:  sudo apt install libpcap-dev\n"
        "  → Fedora/RHEL:    sudo dnf install libpcap-devel\n"
        "  → Arch:           sudo pacman -S libpcap"
    )


# ============================================================
# RETRY DECORATOR
# ============================================================

def retry(
    max_retries: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0,
    exceptions: Tuple = (Exception,),
) -> Callable:
    """
    Retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        delay:       Initial delay between retries (seconds).
        backoff:     Multiplier applied to delay after each retry.
        exceptions:  Tuple of exception types to catch.

    Returns:
        Decorated function.

    Example::

        @retry(max_retries=3, delay=1.0)
        def fetch_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt < max_retries:
                        logger.warning(
                            "%s failed (attempt %d/%d): %s — "
                            "retrying in %.1fs",
                            func.__name__, attempt, max_retries,
                            exc, current_delay,
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "%s failed after %d attempts: %s",
                            func.__name__, max_retries, exc,
                        )
            raise last_exception  # type: ignore[misc]

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt < max_retries:
                        logger.warning(
                            "%s failed (attempt %d/%d): %s — "
                            "retrying in %.1fs",
                            func.__name__, attempt, max_retries,
                            exc, current_delay,
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "%s failed after %d attempts: %s",
                            func.__name__, max_retries, exc,
                        )
            raise last_exception  # type: ignore[misc]

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# ============================================================
# FORMATTING HELPERS
# ============================================================

def format_bytes(num_bytes: int) -> str:
    """
    Format a byte count into a human-readable string.

    Args:
        num_bytes: Number of bytes.

    Returns:
        Formatted string, e.g. "1.23 MB".
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0  # type: ignore[assignment]
    return f"{num_bytes:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted string, e.g. "2h 15m 30s".
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"

    parts = []
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")

    return " ".join(parts)
