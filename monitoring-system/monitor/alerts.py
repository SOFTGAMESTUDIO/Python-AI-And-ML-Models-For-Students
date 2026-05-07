# ============================================================
# Monitoring System — Alerts Module
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
alerts.py — Pluggable Alert System

Supports:
  - Telegram Bot API alerts
  - Discord Webhook alerts
  - Console alerts (Rich-formatted)
  - Alert severity levels (INFO, WARNING, CRITICAL)
  - Cooldown-based deduplication
"""

import asyncio
import time
from enum import Enum
from typing import Dict, List, Optional

import aiohttp

from config import settings
from monitor.logger import get_logger

logger = get_logger(__name__)


class Severity(str, Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertBackend:
    """Base class for alert delivery backends."""

    name: str = "base"

    async def send(self, message: str, severity: Severity) -> bool:
        """Send an alert. Return True on success."""
        raise NotImplementedError


class ConsoleAlertBackend(AlertBackend):
    """Print alerts to the console with Rich markup."""

    name = "console"

    async def send(self, message: str, severity: Severity) -> bool:
        color_map = {
            Severity.INFO: "blue",
            Severity.WARNING: "yellow",
            Severity.CRITICAL: "red",
        }
        color = color_map.get(severity, "white")
        logger.info(
            "[bold %s]🔔 ALERT [%s][/]: %s",
            color, severity.value, message,
        )
        return True


class TelegramAlertBackend(AlertBackend):
    """Send alerts via Telegram Bot API."""

    name = "telegram"

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> None:
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID

    @property
    def configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    async def send(self, message: str, severity: Severity) -> bool:
        if not self.configured:
            logger.debug("Telegram not configured — skipping")
            return False

        url = (
            f"https://api.telegram.org/bot{self.bot_token}"
            f"/sendMessage"
        )
        icon = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}.get(
            severity.value, "📢"
        )
        payload = {
            "chat_id": self.chat_id,
            "text": f"{icon} *{severity.value}*\n\n{message}",
            "parse_mode": "Markdown",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        logger.info("Telegram alert sent")
                        return True
                    else:
                        body = await resp.text()
                        logger.error("Telegram API error %d: %s", resp.status, body)
                        return False
        except Exception as exc:
            logger.error("Telegram send failed: %s", exc)
            return False


class DiscordAlertBackend(AlertBackend):
    """Send alerts via Discord Webhook."""

    name = "discord"

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url = webhook_url or settings.DISCORD_WEBHOOK_URL

    @property
    def configured(self) -> bool:
        return bool(self.webhook_url)

    async def send(self, message: str, severity: Severity) -> bool:
        if not self.configured:
            logger.debug("Discord not configured — skipping")
            return False

        color_map = {
            Severity.INFO: 3447003,       # Blue
            Severity.WARNING: 16776960,   # Yellow
            Severity.CRITICAL: 15158332,  # Red
        }

        payload = {
            "embeds": [{
                "title": f"🔔 {severity.value} Alert",
                "description": message,
                "color": color_map.get(severity, 0),
                "footer": {"text": settings.APP_NAME},
            }]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url, json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status in (200, 204):
                        logger.info("Discord alert sent")
                        return True
                    else:
                        body = await resp.text()
                        logger.error("Discord API error %d: %s", resp.status, body)
                        return False
        except Exception as exc:
            logger.error("Discord send failed: %s", exc)
            return False


class AlertManager:
    """
    Manages multiple alert backends with deduplication.

    Usage::

        manager = AlertManager()
        await manager.send_alert("Server is down!", Severity.CRITICAL)
    """

    def __init__(self, cooldown_seconds: int = 300) -> None:
        self.backends: List[AlertBackend] = []
        self._cooldown = cooldown_seconds
        self._last_alerts: Dict[str, float] = {}

        # Auto-register available backends
        self.backends.append(ConsoleAlertBackend())

        telegram = TelegramAlertBackend()
        if telegram.configured:
            self.backends.append(telegram)
            logger.info("Telegram alerts enabled")

        discord = DiscordAlertBackend()
        if discord.configured:
            self.backends.append(discord)
            logger.info("Discord alerts enabled")

        logger.info(
            "AlertManager initialized — %d backend(s): %s",
            len(self.backends),
            ", ".join(b.name for b in self.backends),
        )

    async def send_alert(
        self,
        message: str,
        severity: str = "WARNING",
    ) -> None:
        """
        Send an alert to all configured backends.

        Deduplicates by message hash with a cooldown period.
        """
        # Normalize severity
        try:
            sev = Severity(severity.upper())
        except ValueError:
            sev = Severity.WARNING

        # Cooldown check
        now = time.time()
        msg_key = f"{sev.value}:{message[:100]}"
        last_time = self._last_alerts.get(msg_key, 0)
        if now - last_time < self._cooldown:
            logger.debug("Alert suppressed (cooldown): %s", msg_key[:60])
            return

        self._last_alerts[msg_key] = now

        # Send to all backends
        for backend in self.backends:
            try:
                await backend.send(message, sev)
            except Exception:
                logger.exception("Error in %s backend", backend.name)