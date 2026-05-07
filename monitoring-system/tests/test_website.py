# ============================================================
# Monitoring System — Website Monitor Tests
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
test_website.py — Unit tests for WebsiteMonitor.

Tests HTTP health checks with mocked responses, stats tracking,
and status classification.
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from monitor.website import WebsiteMonitor, CheckResult, SiteStatus, MonitorStats


class TestCheckResult:
    """Tests for the CheckResult dataclass."""

    def test_defaults(self):
        result = CheckResult(url="https://example.com", status=SiteStatus.UP)
        assert result.url == "https://example.com"
        assert result.status == SiteStatus.UP
        assert result.status_code == 0
        assert result.response_time_ms == 0.0
        assert result.error is None
        assert result.ssl_valid is True

    def test_down_with_error(self):
        result = CheckResult(
            url="https://example.com",
            status=SiteStatus.DOWN,
            error="Connection refused",
        )
        assert result.status == SiteStatus.DOWN
        assert result.error == "Connection refused"


class TestMonitorStats:
    """Tests for MonitorStats accumulation."""

    def test_initial_stats(self):
        stats = MonitorStats()
        assert stats.total_checks == 0
        assert stats.uptime_percent == 0.0
        assert stats.avg_response_ms == 0.0

    def test_uptime_calculation(self):
        stats = MonitorStats(
            total_checks=100,
            successful_checks=95,
            failed_checks=5,
        )
        assert stats.uptime_percent == 95.0

    def test_avg_response(self):
        stats = MonitorStats(
            successful_checks=4,
            total_response_ms=400.0,
        )
        assert stats.avg_response_ms == 100.0

    def test_to_dict(self):
        stats = MonitorStats(total_checks=10, successful_checks=8, failed_checks=2)
        d = stats.to_dict()
        assert d["total_checks"] == 10
        assert d["uptime_percent"] == 80.0


class TestWebsiteMonitor:
    """Tests for the WebsiteMonitor class."""

    def test_init_defaults(self):
        monitor = WebsiteMonitor(url="https://test.com")
        assert monitor.url == "https://test.com"
        assert monitor.stats.total_checks == 0
        assert monitor._running is False

    @pytest.mark.asyncio
    async def test_check_once_success(self):
        """Mock a successful HTTP check."""
        monitor = WebsiteMonitor(url="https://httpbin.org/status/200")

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await monitor.check_once()

        assert monitor.stats.total_checks >= 1

    def test_update_stats_up(self):
        monitor = WebsiteMonitor(url="https://test.com")
        result = CheckResult(
            url="https://test.com",
            status=SiteStatus.UP,
            status_code=200,
            response_time_ms=150.0,
        )
        monitor._update_stats(result)
        assert monitor.stats.total_checks == 1
        assert monitor.stats.successful_checks == 1
        assert monitor.stats.consecutive_failures == 0

    def test_update_stats_down(self):
        monitor = WebsiteMonitor(url="https://test.com")
        result = CheckResult(
            url="https://test.com",
            status=SiteStatus.DOWN,
            error="timeout",
        )
        monitor._update_stats(result)
        assert monitor.stats.failed_checks == 1
        assert monitor.stats.consecutive_failures == 1


class TestSiteStatus:
    """Tests for the SiteStatus enum."""

    def test_values(self):
        assert SiteStatus.UP.value == "up"
        assert SiteStatus.DOWN.value == "down"
        assert SiteStatus.DEGRADED.value == "degraded"
        assert SiteStatus.UNKNOWN.value == "unknown"
