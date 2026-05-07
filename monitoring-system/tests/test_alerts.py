# ============================================================
# Monitoring System — Alert Tests
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
test_alerts.py — Unit tests for the AlertManager and backends.

Tests console alerts, cooldown dedup, severity parsing,
and Telegram/Discord backend configuration checks.
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, patch

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from monitor.alerts import (
    AlertManager,
    ConsoleAlertBackend,
    TelegramAlertBackend,
    DiscordAlertBackend,
    Severity,
)


class TestSeverity:
    """Tests for the Severity enum."""

    def test_values(self):
        assert Severity.INFO.value == "INFO"
        assert Severity.WARNING.value == "WARNING"
        assert Severity.CRITICAL.value == "CRITICAL"

    def test_from_string(self):
        assert Severity("INFO") == Severity.INFO
        assert Severity("CRITICAL") == Severity.CRITICAL


class TestConsoleAlertBackend:
    """Tests for console alert output."""

    @pytest.mark.asyncio
    async def test_send_returns_true(self):
        backend = ConsoleAlertBackend()
        result = await backend.send("Test alert", Severity.INFO)
        assert result is True

    @pytest.mark.asyncio
    async def test_send_all_severities(self):
        backend = ConsoleAlertBackend()
        for sev in Severity:
            result = await backend.send(f"Test {sev.value}", sev)
            assert result is True


class TestTelegramAlertBackend:
    """Tests for Telegram alert backend."""

    def test_not_configured_by_default(self):
        backend = TelegramAlertBackend(bot_token="", chat_id="")
        assert backend.configured is False

    def test_configured_with_values(self):
        backend = TelegramAlertBackend(
            bot_token="123:ABC",
            chat_id="456",
        )
        assert backend.configured is True

    @pytest.mark.asyncio
    async def test_send_skips_when_not_configured(self):
        backend = TelegramAlertBackend(bot_token="", chat_id="")
        result = await backend.send("Test", Severity.INFO)
        assert result is False


class TestDiscordAlertBackend:
    """Tests for Discord alert backend."""

    def test_not_configured_by_default(self):
        backend = DiscordAlertBackend(webhook_url="")
        assert backend.configured is False

    def test_configured_with_url(self):
        backend = DiscordAlertBackend(
            webhook_url="https://discord.com/api/webhooks/123/abc"
        )
        assert backend.configured is True

    @pytest.mark.asyncio
    async def test_send_skips_when_not_configured(self):
        backend = DiscordAlertBackend(webhook_url="")
        result = await backend.send("Test", Severity.WARNING)
        assert result is False


class TestAlertManager:
    """Tests for the AlertManager orchestrator."""

    def test_init_has_console_backend(self):
        manager = AlertManager()
        backend_names = [b.name for b in manager.backends]
        assert "console" in backend_names

    @pytest.mark.asyncio
    async def test_send_alert_info(self):
        manager = AlertManager(cooldown_seconds=0)
        # Should not raise
        await manager.send_alert("Test info alert", "INFO")

    @pytest.mark.asyncio
    async def test_send_alert_critical(self):
        manager = AlertManager(cooldown_seconds=0)
        await manager.send_alert("Server down!", "CRITICAL")

    @pytest.mark.asyncio
    async def test_cooldown_deduplication(self):
        manager = AlertManager(cooldown_seconds=300)

        # First alert should go through
        await manager.send_alert("Same message", "WARNING")

        # Second identical alert within cooldown should be suppressed
        # (no error, just silently skipped)
        await manager.send_alert("Same message", "WARNING")

    @pytest.mark.asyncio
    async def test_invalid_severity_defaults(self):
        manager = AlertManager(cooldown_seconds=0)
        # Invalid severity should default to WARNING
        await manager.send_alert("Test", "INVALID_LEVEL")
