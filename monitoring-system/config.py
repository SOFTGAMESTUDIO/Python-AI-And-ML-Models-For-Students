# ============================================================
# Monitoring System — Configuration Module
# Copyright (c) 2026 Soft Game Studio
# License: MIT
#
# Production-ready configuration with environment variable
# support, validation, and sensible defaults.
# ============================================================

"""
config.py — Centralized Configuration

Loads all settings from environment variables (via .env file)
with typed defaults and validation. Provides a singleton
Settings instance for the entire application.
"""

import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


def _env_bool(key: str, default: bool = False) -> bool:
    """Parse a boolean environment variable."""
    val = os.getenv(key, str(default)).lower()
    return val in ("true", "1", "yes", "on")


def _env_int(key: str, default: int = 0) -> int:
    """Parse an integer environment variable safely."""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


@dataclass
class Settings:
    """
    Application settings loaded from environment variables.

    All values have sensible defaults so the application can
    start without a .env file in development mode.
    """

    # ----- Application -----
    APP_NAME: str = "Monitoring System"
    APP_VERSION: str = "2.0.0"
    ORGANIZATION: str = "Soft Game Studio"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # ----- Website Monitoring -----
    WEBSITE_URL: str = "https://softgamestudios.web.app"
    CHECK_INTERVAL: int = 30          # seconds between checks
    REQUEST_TIMEOUT: int = 10         # HTTP request timeout
    MAX_RETRIES: int = 3              # retry count on failure
    RETRY_DELAY: int = 2              # seconds between retries

    # ----- Network Monitoring -----
    ENABLE_PACKET_MONITORING: bool = True
    NETWORK_INTERFACE: str = "Wi-Fi"  # Windows default
    PACKET_COUNT_LIMIT: int = 0       # 0 = unlimited

    # ----- Alert Settings -----
    ENABLE_ALERTS: bool = True
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    DISCORD_WEBHOOK_URL: str = ""

    # ----- Email Alerts -----
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    ALERT_EMAIL: str = ""

    # ----- Firebase -----
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_API_KEY: str = ""

    # ----- Dashboard / API -----
    DASHBOARD_HOST: str = "0.0.0.0"
    DASHBOARD_PORT: int = 8000

    # ----- Database -----
    DATABASE_URL: str = "sqlite:///database/monitor.db"

    # ----- Logging -----
    LOG_DIR: str = "logs"
    LOG_FILE: str = "logs/system.log"
    ENABLE_FILE_LOGGING: bool = True
    ENABLE_CONSOLE_LOGGING: bool = True

    # ----- Security -----
    MAX_REQUESTS_PER_MINUTE: int = 100
    ENABLE_RATE_LIMITING: bool = True
    BLOCK_SUSPICIOUS_IPS: bool = False

    # ----- DDoS Detection -----
    ENABLE_DDOS_DETECTION: bool = True
    DDOS_PACKET_THRESHOLD: int = 1000  # packets/minute

    # ----- Performance -----
    MAX_WORKERS: int = 10
    ENABLE_ASYNC_MONITORING: bool = True

    # ----- Headers -----
    DEFAULT_HEADERS: dict = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 Monitoring-System/2.0"
    })

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.CHECK_INTERVAL <= 0:
            raise ValueError("CHECK_INTERVAL must be > 0")
        if self.REQUEST_TIMEOUT <= 0:
            raise ValueError("REQUEST_TIMEOUT must be > 0")
        if self.DASHBOARD_PORT < 1 or self.DASHBOARD_PORT > 65535:
            raise ValueError("DASHBOARD_PORT must be 1–65535")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def telegram_configured(self) -> bool:
        """Check if Telegram alerts are fully configured."""
        return bool(self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_CHAT_ID)

    @property
    def discord_configured(self) -> bool:
        """Check if Discord alerts are fully configured."""
        return bool(self.DISCORD_WEBHOOK_URL)

    @property
    def email_configured(self) -> bool:
        """Check if email alerts are fully configured."""
        return bool(self.EMAIL_USER and self.EMAIL_PASSWORD and self.ALERT_EMAIL)


def load_settings() -> Settings:
    """
    Create a Settings instance populated from environment variables.

    Returns:
        Settings: Fully validated configuration object.
    """
    return Settings(
        # Application
        ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
        DEBUG=_env_bool("DEBUG", False),

        # Website Monitoring
        WEBSITE_URL=os.getenv("WEBSITE_URL", "https://softgamestudios.web.app"),
        CHECK_INTERVAL=_env_int("CHECK_INTERVAL", 30),
        REQUEST_TIMEOUT=_env_int("REQUEST_TIMEOUT", 10),
        MAX_RETRIES=_env_int("MAX_RETRIES", 3),
        RETRY_DELAY=_env_int("RETRY_DELAY", 2),

        # Network
        ENABLE_PACKET_MONITORING=_env_bool("ENABLE_PACKET_MONITORING", True),
        NETWORK_INTERFACE=os.getenv("NETWORK_INTERFACE", "Wi-Fi"),

        # Alerts
        ENABLE_ALERTS=_env_bool("ENABLE_ALERTS", True),
        TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID", ""),
        DISCORD_WEBHOOK_URL=os.getenv("DISCORD_WEBHOOK_URL", ""),

        # Email
        SMTP_SERVER=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        SMTP_PORT=_env_int("SMTP_PORT", 587),
        EMAIL_USER=os.getenv("EMAIL_USER", ""),
        EMAIL_PASSWORD=os.getenv("EMAIL_PASSWORD", ""),
        ALERT_EMAIL=os.getenv("ALERT_EMAIL", ""),

        # Firebase
        FIREBASE_PROJECT_ID=os.getenv("FIREBASE_PROJECT_ID", ""),
        FIREBASE_API_KEY=os.getenv("FIREBASE_API_KEY", ""),

        # Dashboard
        DASHBOARD_HOST=os.getenv("DASHBOARD_HOST", "0.0.0.0"),
        DASHBOARD_PORT=_env_int("DASHBOARD_PORT", 8000),

        # Database
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///database/monitor.db"),

        # Logging
        LOG_DIR=os.getenv("LOG_DIR", "logs"),
        LOG_FILE=os.getenv("LOG_FILE", "logs/system.log"),
        ENABLE_FILE_LOGGING=_env_bool("ENABLE_FILE_LOGGING", True),
        ENABLE_CONSOLE_LOGGING=_env_bool("ENABLE_CONSOLE_LOGGING", True),

        # Security
        MAX_REQUESTS_PER_MINUTE=_env_int("MAX_REQUESTS_PER_MINUTE", 100),
        ENABLE_RATE_LIMITING=_env_bool("ENABLE_RATE_LIMITING", True),

        # DDoS
        ENABLE_DDOS_DETECTION=_env_bool("ENABLE_DDOS_DETECTION", True),
        DDOS_PACKET_THRESHOLD=_env_int("DDOS_PACKET_THRESHOLD", 1000),

        # Performance
        MAX_WORKERS=_env_int("MAX_WORKERS", 10),
    )


# ----- Singleton Settings Instance -----
settings = load_settings()