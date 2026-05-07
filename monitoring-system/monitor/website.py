# ============================================================
# Monitoring System — Website Monitor
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
website.py — Async Website & Firebase Monitoring

Provides WebsiteMonitor class that performs:
  - Periodic HTTP health checks with response time tracking
  - SSL certificate validation
  - Firebase Hosting status checks
  - Retry logic with exponential backoff
  - Statistics (uptime %, avg response time, error count)
  - Alert integration on status changes
"""

import asyncio
import ssl
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional

import aiohttp

from config import settings
from monitor.logger import get_logger
from monitor.utils import retry

logger = get_logger(__name__)


class SiteStatus(str, Enum):
    """Possible states for a monitored site."""
    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class CheckResult:
    """Result of a single website health check."""
    url: str
    status: SiteStatus
    status_code: int = 0
    response_time_ms: float = 0.0
    error: Optional[str] = None
    ssl_valid: bool = True
    timestamp: float = field(default_factory=time.time)


@dataclass
class MonitorStats:
    """Accumulated monitoring statistics."""
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    total_response_ms: float = 0.0
    last_status: SiteStatus = SiteStatus.UNKNOWN
    last_check_time: float = 0.0
    consecutive_failures: int = 0

    @property
    def uptime_percent(self) -> float:
        if self.total_checks == 0:
            return 0.0
        return (self.successful_checks / self.total_checks) * 100

    @property
    def avg_response_ms(self) -> float:
        if self.successful_checks == 0:
            return 0.0
        return self.total_response_ms / self.successful_checks

    def to_dict(self) -> Dict:
        return {
            "total_checks": self.total_checks,
            "successful": self.successful_checks,
            "failed": self.failed_checks,
            "uptime_percent": round(self.uptime_percent, 2),
            "avg_response_ms": round(self.avg_response_ms, 2),
            "last_status": self.last_status.value,
            "consecutive_failures": self.consecutive_failures,
        }


class WebsiteMonitor:
    """
    Async website health monitor with retry, stats, and alerts.

    Usage::

        monitor = WebsiteMonitor(
            url="https://example.com",
            on_alert=my_alert_callback,
        )
        await monitor.start()
    """

    def __init__(
        self,
        url: Optional[str] = None,
        interval: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        on_alert: Optional[Callable] = None,
        on_check: Optional[Callable] = None,
    ) -> None:
        self.url = url or settings.WEBSITE_URL
        self.interval = interval or settings.CHECK_INTERVAL
        self.timeout = timeout or settings.REQUEST_TIMEOUT
        self.max_retries = max_retries or settings.MAX_RETRIES
        self.on_alert = on_alert
        self.on_check = on_check

        self.stats = MonitorStats()
        self._running = False
        self._task: Optional[asyncio.Task] = None

        logger.info(
            "WebsiteMonitor created — url=%s interval=%ds",
            self.url, self.interval,
        )

    # ---- Public API ----

    async def start(self) -> None:
        """Start the monitoring loop."""
        if self._running:
            logger.warning("WebsiteMonitor already running")
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("WebsiteMonitor started for %s", self.url)

    async def stop(self) -> None:
        """Stop the monitoring loop gracefully."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("WebsiteMonitor stopped")

    async def check_once(self) -> CheckResult:
        """Perform a single health check with retries."""
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                result = await self._perform_check()
                self._update_stats(result)
                return result
            except Exception as exc:
                last_error = str(exc)
                if attempt < self.max_retries:
                    wait = settings.RETRY_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        "Check failed (attempt %d/%d): %s — retry in %ds",
                        attempt, self.max_retries, exc, wait,
                    )
                    await asyncio.sleep(wait)

        # All retries exhausted
        result = CheckResult(
            url=self.url,
            status=SiteStatus.DOWN,
            error=last_error,
        )
        self._update_stats(result)
        return result

    # ---- Firebase Monitoring ----

    async def check_firebase_status(self) -> CheckResult:
        """
        Check Firebase Hosting availability.

        Queries the site and verifies Firebase-specific headers.
        """
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                start = time.time()
                async with session.get(
                    self.url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers=settings.DEFAULT_HEADERS,
                ) as resp:
                    elapsed_ms = (time.time() - start) * 1000

                    # Check for Firebase-specific headers
                    server = resp.headers.get("server", "")
                    is_firebase = "Google Frontend" in server or "firebase" in server.lower()

                    status = SiteStatus.UP if resp.status < 400 else SiteStatus.DOWN

                    return CheckResult(
                        url=self.url,
                        status=status,
                        status_code=resp.status,
                        response_time_ms=elapsed_ms,
                    )
        except Exception as exc:
            logger.error("Firebase status check failed: %s", exc)
            return CheckResult(
                url=self.url,
                status=SiteStatus.DOWN,
                error=str(exc),
            )

    # ---- Internal ----

    async def _monitor_loop(self) -> None:
        """Main monitoring loop — runs until stopped."""
        logger.info("Monitoring loop started (interval=%ds)", self.interval)
        while self._running:
            try:
                result = await self.check_once()

                # Log the result
                if result.status == SiteStatus.UP:
                    logger.info(
                        "[bold green]✓[/] %s — %d — %.0fms",
                        result.url, result.status_code,
                        result.response_time_ms,
                    )
                else:
                    logger.warning(
                        "[bold red]✗[/] %s — %s — %s",
                        result.url, result.status.value,
                        result.error or "unknown error",
                    )

                # Fire callbacks
                if self.on_check:
                    try:
                        self.on_check(result)
                    except Exception:
                        logger.exception("on_check callback error")

                # Trigger alert on status change
                if result.status == SiteStatus.DOWN and self.on_alert:
                    try:
                        await self._fire_alert(result)
                    except Exception:
                        logger.exception("Alert callback error")

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Unexpected error in monitor loop")

            await asyncio.sleep(self.interval)

    async def _perform_check(self) -> CheckResult:
        """Execute a single HTTP GET request."""
        ssl_valid = True

        # Create connector (validate SSL by default)
        try:
            ssl_ctx = ssl.create_default_context()
            connector = aiohttp.TCPConnector(ssl=ssl_ctx)
        except Exception:
            connector = aiohttp.TCPConnector(ssl=False)
            ssl_valid = False

        async with aiohttp.ClientSession(connector=connector) as session:
            start = time.time()
            async with session.get(
                self.url,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=settings.DEFAULT_HEADERS,
            ) as resp:
                elapsed_ms = (time.time() - start) * 1000

                if resp.status < 400:
                    status = SiteStatus.UP
                elif resp.status < 500:
                    status = SiteStatus.DEGRADED
                else:
                    status = SiteStatus.DOWN

                return CheckResult(
                    url=self.url,
                    status=status,
                    status_code=resp.status,
                    response_time_ms=elapsed_ms,
                    ssl_valid=ssl_valid,
                )

    def _update_stats(self, result: CheckResult) -> None:
        """Update accumulated statistics."""
        self.stats.total_checks += 1
        self.stats.last_check_time = time.time()
        self.stats.last_status = result.status

        if result.status == SiteStatus.UP:
            self.stats.successful_checks += 1
            self.stats.total_response_ms += result.response_time_ms
            self.stats.consecutive_failures = 0
        else:
            self.stats.failed_checks += 1
            self.stats.consecutive_failures += 1

    async def _fire_alert(self, result: CheckResult) -> None:
        """Send alert via callback."""
        if self.on_alert:
            message = (
                f"🚨 WEBSITE DOWN: {result.url}\n"
                f"Status: {result.status.value}\n"
                f"Error: {result.error or 'N/A'}\n"
                f"Consecutive failures: {self.stats.consecutive_failures}"
            )
            if asyncio.iscoroutinefunction(self.on_alert):
                await self.on_alert(message, "CRITICAL")
            else:
                self.on_alert(message, "CRITICAL")