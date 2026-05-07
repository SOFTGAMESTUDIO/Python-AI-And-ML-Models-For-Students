# ============================================================
# Monitoring System — Security Module
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
security.py — Security utilities: sanitization, rate limiting,
IP validation, and sensitive data masking.
"""

import re
import time
import threading
import ipaddress
from typing import Dict, Optional

from monitor.logger import get_logger

logger = get_logger(__name__)


def sanitize_url(url: str) -> str:
    """Sanitize and validate a URL string."""
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty")
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL scheme: {url!r}")
    return url


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Strip control characters and truncate."""
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
    return value[:max_length]


class RateLimiter:
    """Thread-safe token-bucket rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self._max = max_requests
        self._window = window_seconds
        self._buckets: Dict[str, list] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        """Return True if request from key is within limits."""
        now = time.time()
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = []
            self._buckets[key] = [
                ts for ts in self._buckets[key]
                if now - ts < self._window
            ]
            if len(self._buckets[key]) >= self._max:
                return False
            self._buckets[key].append(now)
            return True

    def reset(self, key: Optional[str] = None) -> None:
        """Reset limits for a key or all keys."""
        with self._lock:
            if key:
                self._buckets.pop(key, None)
            else:
                self._buckets.clear()


def is_valid_ip(address: str) -> bool:
    """Validate an IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def is_private_ip(address: str) -> bool:
    """Check if an IP address is private/reserved."""
    try:
        return ipaddress.ip_address(address).is_private
    except ValueError:
        return False


_SECRET_PATTERNS = re.compile(
    r"(token|password|secret|api[_-]?key|authorization)"
    r"\s*[:=]\s*\S+",
    re.IGNORECASE,
)


def mask_sensitive(text: str) -> str:
    """Mask sensitive values (tokens, passwords, etc.) in text."""
    def _replacer(match: re.Match) -> str:
        key_part = match.group().split("=")[0].split(":")[0]
        return f"{key_part.strip()}=****"
    return _SECRET_PATTERNS.sub(_replacer, text)
