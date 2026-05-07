# ============================================================
# Monitoring System — Network Monitor Tests
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
test_network.py — Unit tests for NetworkMonitor.

Tests Npcap detection, availability checks, fallback behavior,
and socket-based utilities.
"""

import pytest
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from monitor.network import NetworkMonitor, NetworkStats
from monitor.utils import check_npcap_installed, is_admin, format_bytes, format_duration


class TestNetworkStats:
    """Tests for the NetworkStats dataclass."""

    def test_defaults(self):
        stats = NetworkStats()
        assert stats.packets_total == 0
        assert stats.packets_tcp == 0
        assert stats.bytes_total == 0

    def test_packets_per_second(self):
        stats = NetworkStats(packets_total=100)
        # elapsed will be > 0 since start_time is set at creation
        assert stats.packets_per_second >= 0

    def test_top_source_empty(self):
        stats = NetworkStats()
        assert stats.top_source is None

    def test_top_source(self):
        stats = NetworkStats()
        stats.source_ips["192.168.1.1"] = 50
        stats.source_ips["10.0.0.1"] = 10
        assert stats.top_source == "192.168.1.1"

    def test_to_dict(self):
        stats = NetworkStats(packets_total=42, packets_tcp=20)
        d = stats.to_dict()
        assert d["packets_total"] == 42
        assert d["packets_tcp"] == 20
        assert "packets_per_second" in d


class TestNetworkMonitor:
    """Tests for NetworkMonitor initialization and fallback."""

    def test_init_creates_instance(self):
        """Monitor should initialize even without Npcap."""
        monitor = NetworkMonitor()
        # It should have checked availability
        assert isinstance(monitor.available, bool)
        assert isinstance(monitor.unavailable_reason, str)

    def test_stats_initially_empty(self):
        monitor = NetworkMonitor()
        stats = monitor.get_stats()
        assert stats["packets_total"] == 0

    def test_check_port_localhost(self):
        """Port check should work without Npcap."""
        monitor = NetworkMonitor()
        # Port 99999 should not be open
        assert monitor.check_port("127.0.0.1", 99, timeout=1.0) is False

    def test_resolve_host(self):
        """DNS resolution should work without Npcap."""
        monitor = NetworkMonitor()
        ip = monitor.resolve_host("localhost")
        assert ip is not None  # should resolve to 127.0.0.1

    def test_start_when_unavailable(self):
        """Start should return False if sniffing is unavailable."""
        monitor = NetworkMonitor()
        monitor.available = False
        monitor.unavailable_reason = "Test — disabled"
        assert monitor.start() is False

    def test_reset_stats(self):
        monitor = NetworkMonitor()
        monitor.stats.packets_total = 100
        monitor.reset_stats()
        assert monitor.stats.packets_total == 0


class TestNpcapDetection:
    """Tests for the Npcap/libpcap detection utility."""

    def test_returns_tuple(self):
        installed, message = check_npcap_installed()
        assert isinstance(installed, bool)
        assert isinstance(message, str)
        assert len(message) > 0


class TestFormatHelpers:
    """Tests for formatting utility functions."""

    def test_format_bytes(self):
        assert format_bytes(0) == "0.00 B"
        assert "KB" in format_bytes(1024)
        assert "MB" in format_bytes(1024 * 1024)
        assert "GB" in format_bytes(1024 ** 3)

    def test_format_duration_ms(self):
        assert "ms" in format_duration(0.5)

    def test_format_duration_seconds(self):
        assert "s" in format_duration(45)

    def test_format_duration_hours(self):
        result = format_duration(3661)
        assert "1h" in result
        assert "1m" in result
