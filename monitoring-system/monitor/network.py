# ============================================================
# Monitoring System — Network Monitor
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
network.py — Network Traffic Monitor with Scapy

This module solves the core issue:
  RuntimeError: Sniffing and sending packets is not available
  at layer 2: winpcap is not installed

Strategy:
  1. NEVER import Scapy at module level
  2. Check Npcap/libpcap BEFORE attempting to use Scapy
  3. Check admin privileges
  4. Graceful fallback — if unavailable, monitor continues
     without packet sniffing
  5. Socket-based fallback for basic connectivity checks
"""

import os
import sys
import time
import socket
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from config import settings
from monitor.logger import get_logger
from monitor.utils import check_npcap_installed, is_admin, is_windows

logger = get_logger(__name__)


@dataclass
class NetworkStats:
    """Accumulated network traffic statistics."""
    packets_total: int = 0
    packets_tcp: int = 0
    packets_udp: int = 0
    packets_icmp: int = 0
    packets_dns: int = 0
    packets_other: int = 0
    bytes_total: int = 0
    start_time: float = field(default_factory=time.time)
    source_ips: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    @property
    def elapsed_seconds(self) -> float:
        return max(time.time() - self.start_time, 1.0)

    @property
    def packets_per_second(self) -> float:
        return self.packets_total / self.elapsed_seconds

    @property
    def top_source(self) -> Optional[str]:
        if not self.source_ips:
            return None
        return max(self.source_ips, key=self.source_ips.get)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packets_total": self.packets_total,
            "packets_tcp": self.packets_tcp,
            "packets_udp": self.packets_udp,
            "packets_icmp": self.packets_icmp,
            "packets_dns": self.packets_dns,
            "packets_other": self.packets_other,
            "bytes_total": self.bytes_total,
            "packets_per_second": round(self.packets_per_second, 2),
            "top_source": self.top_source,
            "elapsed_seconds": round(self.elapsed_seconds, 1),
        }


class NetworkMonitor:
    """
    Network traffic monitor with Scapy + safe fallback.

    Automatically detects Npcap availability and admin
    privileges. If either is missing, packet sniffing is
    disabled gracefully and the rest of the system continues.

    Usage::

        monitor = NetworkMonitor()
        if monitor.available:
            monitor.start()
        else:
            print(monitor.unavailable_reason)
    """

    def __init__(
        self,
        interface: Optional[str] = None,
        on_packet: Optional[Callable] = None,
        on_alert: Optional[Callable] = None,
    ) -> None:
        self.interface = interface or settings.NETWORK_INTERFACE
        self.on_packet = on_packet
        self.on_alert = on_alert

        self.stats = NetworkStats()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Check availability
        self.available = False
        self.unavailable_reason = ""
        self._scapy_sniff = None
        self._scapy_IP = None
        self._scapy_TCP = None
        self._scapy_UDP = None
        self._scapy_ICMP = None
        self._scapy_DNS = None

        self._check_availability()

    def _check_availability(self) -> None:
        """
        Determine if packet sniffing is possible on this system.

        Checks:
          1. Npcap / libpcap installed
          2. Admin / root privileges
          3. Scapy importable
        """
        # Step 1: Check pcap library
        pcap_ok, pcap_msg = check_npcap_installed()
        if not pcap_ok:
            self.unavailable_reason = (
                f"Packet capture library not found.\n{pcap_msg}"
            )
            logger.warning("Network sniffing disabled: %s", pcap_msg)
            return

        logger.info("Pcap library check: %s", pcap_msg)

        # Step 2: Check privileges
        if not is_admin():
            self.unavailable_reason = (
                "Packet sniffing requires administrator/root privileges.\n"
                "  → Windows: Run terminal as Administrator\n"
                "  → Linux:   Run with sudo"
            )
            logger.warning("Network sniffing disabled: not running as admin")
            return

        # Step 3: Try importing Scapy
        try:
            # Suppress Scapy warnings during import
            import logging as _logging
            _logging.getLogger("scapy.runtime").setLevel(_logging.ERROR)

            from scapy.all import sniff as scapy_sniff
            from scapy.layers.inet import IP, TCP, UDP, ICMP
            from scapy.layers.dns import DNS

            self._scapy_sniff = scapy_sniff
            self._scapy_IP = IP
            self._scapy_TCP = TCP
            self._scapy_UDP = UDP
            self._scapy_ICMP = ICMP
            self._scapy_DNS = DNS

            self.available = True
            logger.info("Scapy loaded — packet sniffing available")

        except ImportError as exc:
            self.unavailable_reason = (
                f"Scapy import failed: {exc}\n"
                "  → Install: pip install scapy"
            )
            logger.warning("Network sniffing disabled: %s", exc)

        except RuntimeError as exc:
            # This catches the WinPcap/Npcap RuntimeError
            self.unavailable_reason = (
                f"Scapy runtime error: {exc}\n"
                "  → Install Npcap: https://npcap.com/#download\n"
                "  → Enable 'WinPcap API-compatible mode' during install"
            )
            logger.warning("Network sniffing disabled: %s", exc)

        except Exception as exc:
            self.unavailable_reason = f"Unexpected error loading Scapy: {exc}"
            logger.warning("Network sniffing disabled: %s", exc)

    # ---- Public API ----

    def start(self) -> bool:
        """
        Start packet sniffing in a background thread.

        Returns:
            True if started, False if unavailable.
        """
        if not self.available:
            logger.warning(
                "Cannot start network monitor: %s",
                self.unavailable_reason,
            )
            return False

        if self._running:
            logger.warning("Network monitor already running")
            return True

        self._running = True
        self._thread = threading.Thread(
            target=self._sniff_loop,
            name="NetworkMonitor",
            daemon=True,
        )
        self._thread.start()
        logger.info("Network monitor started on interface: %s", self.interface)
        return True

    def stop(self) -> None:
        """Stop the packet sniffing thread."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("Network monitor stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get current traffic statistics (thread-safe)."""
        with self._lock:
            return self.stats.to_dict()

    def reset_stats(self) -> None:
        """Reset all statistics."""
        with self._lock:
            self.stats = NetworkStats()

    # ---- Socket Fallback ----

    def check_port(self, host: str, port: int, timeout: float = 3.0) -> bool:
        """
        Check if a TCP port is open (no pcap needed).

        This works without Npcap and without admin privileges.

        Args:
            host:    Hostname or IP address.
            port:    TCP port number.
            timeout: Connection timeout in seconds.

        Returns:
            True if the port is open and accepting connections.
        """
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def resolve_host(self, hostname: str) -> Optional[str]:
        """
        Resolve a hostname to an IP (no pcap needed).

        Args:
            hostname: Domain name to resolve.

        Returns:
            IP address string, or None on failure.
        """
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return None

    # ---- Internal ----

    def _sniff_loop(self) -> None:
        """Scapy sniffing loop (runs in a thread)."""
        try:
            logger.info("Starting Scapy sniff on %s ...", self.interface)
            self._scapy_sniff(
                iface=self.interface,
                prn=self._packet_callback,
                store=False,
                stop_filter=lambda _: not self._running,
            )
        except PermissionError:
            logger.error(
                "Permission denied for packet sniffing. "
                "Run as administrator/root."
            )
            self.available = False
        except RuntimeError as exc:
            logger.error("Scapy runtime error: %s", exc)
            self.available = False
        except Exception:
            logger.exception("Unexpected error in sniff loop")
            self.available = False

    def _packet_callback(self, packet: Any) -> None:
        """Process a captured packet and update statistics."""
        with self._lock:
            self.stats.packets_total += 1

            # Get packet size
            try:
                self.stats.bytes_total += len(packet)
            except TypeError:
                pass

            # Extract IP layer info
            if self._scapy_IP and packet.haslayer(self._scapy_IP):
                src_ip = packet[self._scapy_IP].src
                self.stats.source_ips[src_ip] += 1

                # Protocol classification
                if self._scapy_TCP and packet.haslayer(self._scapy_TCP):
                    self.stats.packets_tcp += 1
                elif self._scapy_UDP and packet.haslayer(self._scapy_UDP):
                    self.stats.packets_udp += 1
                    if self._scapy_DNS and packet.haslayer(self._scapy_DNS):
                        self.stats.packets_dns += 1
                elif self._scapy_ICMP and packet.haslayer(self._scapy_ICMP):
                    self.stats.packets_icmp += 1
                else:
                    self.stats.packets_other += 1
            else:
                self.stats.packets_other += 1

        # Fire user callback
        if self.on_packet:
            try:
                self.on_packet(packet)
            except Exception:
                logger.exception("on_packet callback error")