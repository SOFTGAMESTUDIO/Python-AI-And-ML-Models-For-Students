# ============================================================
# Monitoring System — Database Module
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
database.py — SQLite event storage for monitoring data.

Stores monitoring events, network statistics, and alert history
with thread-safe access and auto-migration.
"""

import os
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional

from monitor.logger import get_logger

logger = get_logger(__name__)

# Default database path
_DB_DIR = "database"
_DB_PATH = os.path.join(_DB_DIR, "monitor.db")

# SQL schema
_SCHEMA = """
CREATE TABLE IF NOT EXISTS monitoring_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   REAL    NOT NULL,
    event_type  TEXT    NOT NULL,
    url         TEXT,
    status_code INTEGER,
    response_ms REAL,
    message     TEXT,
    created_at  TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS network_stats (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       REAL    NOT NULL,
    packets_total   INTEGER DEFAULT 0,
    packets_tcp     INTEGER DEFAULT 0,
    packets_udp     INTEGER DEFAULT 0,
    packets_icmp    INTEGER DEFAULT 0,
    packets_other   INTEGER DEFAULT 0,
    top_source      TEXT,
    created_at      TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS alerts_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   REAL    NOT NULL,
    severity    TEXT    NOT NULL,
    channel     TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    delivered   INTEGER DEFAULT 0,
    created_at  TEXT    DEFAULT (datetime('now'))
);
"""


class MonitorDatabase:
    """Thread-safe SQLite database for monitoring events."""

    def __init__(self, db_path: str = _DB_PATH) -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._ensure_directory()
        self._migrate()
        logger.info("Database initialized at %s", self._db_path)

    def _ensure_directory(self) -> None:
        os.makedirs(os.path.dirname(self._db_path) or _DB_DIR, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _migrate(self) -> None:
        """Run schema creation (idempotent)."""
        with self._lock:
            conn = self._connect()
            try:
                conn.executescript(_SCHEMA)
                conn.commit()
            finally:
                conn.close()

    # ---- Monitoring Events ----

    def log_event(
        self,
        event_type: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        response_ms: Optional[float] = None,
        message: Optional[str] = None,
    ) -> None:
        """Insert a monitoring event."""
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    "INSERT INTO monitoring_events "
                    "(timestamp, event_type, url, status_code, response_ms, message) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (time.time(), event_type, url, status_code, response_ms, message),
                )
                conn.commit()
            finally:
                conn.close()

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent monitoring events."""
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT * FROM monitoring_events ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
                return [dict(r) for r in rows]
            finally:
                conn.close()

    # ---- Network Stats ----

    def log_network_stats(self, stats: Dict[str, Any]) -> None:
        """Insert a network statistics snapshot."""
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    "INSERT INTO network_stats "
                    "(timestamp, packets_total, packets_tcp, packets_udp, "
                    "packets_icmp, packets_other, top_source) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        time.time(),
                        stats.get("total", 0),
                        stats.get("tcp", 0),
                        stats.get("udp", 0),
                        stats.get("icmp", 0),
                        stats.get("other", 0),
                        stats.get("top_source", ""),
                    ),
                )
                conn.commit()
            finally:
                conn.close()

    # ---- Alerts ----

    def log_alert(
        self, severity: str, channel: str, message: str, delivered: bool = True,
    ) -> None:
        """Record an alert in the database."""
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    "INSERT INTO alerts_log "
                    "(timestamp, severity, channel, message, delivered) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (time.time(), severity, channel, message, int(delivered)),
                )
                conn.commit()
            finally:
                conn.close()

    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent alerts."""
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT * FROM alerts_log ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
                return [dict(r) for r in rows]
            finally:
                conn.close()
