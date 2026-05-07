# ============================================================
# Monitoring System — DDoS Detector
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
ddos.py — Basic DDoS Detection

Monitors packet rates per source IP using a sliding window.
Fires alerts when traffic from a single source exceeds the
configured threshold.
"""

import time
import threading
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from config import settings
from monitor.logger import get_logger

logger = get_logger(__name__)


class DDoSDetector:
    """
    Sliding-window DDoS detection by source IP.

    Tracks packets per source IP over a 60-second window
    and fires an alert when any source exceeds the threshold.

    Usage::

        detector = DDoSDetector(on_alert=my_callback)
        detector.record_packet("192.168.1.100")
    """

    def __init__(
        self,
        threshold: Optional[int] = None,
        window_seconds: int = 60,
        on_alert: Optional[Callable] = None,
    ) -> None:
        self.threshold = threshold or settings.DDOS_PACKET_THRESHOLD
        self.window = window_seconds
        self.on_alert = on_alert
        self.enabled = settings.ENABLE_DDOS_DETECTION

        # ip -> [timestamp, timestamp, ...]
        self._packets: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._alerted: Dict[str, float] = {}  # cooldown tracker

        if self.enabled:
            logger.info(
                "DDoS detector initialized — threshold=%d pkts/%ds",
                self.threshold, self.window,
            )

    def record_packet(self, source_ip: str) -> None:
        """
        Record a packet from a source IP and check threshold.

        Args:
            source_ip: Source IP address of the packet.
        """
        if not self.enabled:
            return

        now = time.time()
        with self._lock:
            # Add timestamp
            self._packets[source_ip].append(now)

            # Purge old entries
            cutoff = now - self.window
            self._packets[source_ip] = [
                ts for ts in self._packets[source_ip]
                if ts > cutoff
            ]

            # Check threshold
            count = len(self._packets[source_ip])
            if count >= self.threshold:
                self._trigger_alert(source_ip, count)

    def _trigger_alert(self, source_ip: str, count: int) -> None:
        """Fire a DDoS alert with cooldown (5 minutes per IP)."""
        now = time.time()
        last = self._alerted.get(source_ip, 0)
        if now - last < 300:
            return  # Cooldown active

        self._alerted[source_ip] = now
        message = (
            f"⚠️ Possible DDoS detected!\n"
            f"Source IP: {source_ip}\n"
            f"Packets in window: {count}\n"
            f"Threshold: {self.threshold}/{self.window}s"
        )
        logger.warning(message)

        if self.on_alert:
            try:
                self.on_alert(message, "CRITICAL")
            except Exception:
                logger.exception("DDoS alert callback error")

    def get_stats(self) -> Dict[str, Any]:
        """Return current detection statistics."""
        now = time.time()
        cutoff = now - self.window
        with self._lock:
            active = {
                ip: len([ts for ts in times if ts > cutoff])
                for ip, times in self._packets.items()
                if any(ts > cutoff for ts in times)
            }
        return {
            "enabled": self.enabled,
            "threshold": self.threshold,
            "window_seconds": self.window,
            "active_sources": len(active),
            "top_sources": dict(
                sorted(active.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
        }

    def reset(self) -> None:
        """Clear all tracked data."""
        with self._lock:
            self._packets.clear()
            self._alerted.clear()
