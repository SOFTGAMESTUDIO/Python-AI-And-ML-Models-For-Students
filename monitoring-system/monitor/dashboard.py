# ============================================================
# Monitoring System — Dashboard API
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
dashboard.py — FastAPI Dashboard & Health Endpoints

Provides REST API endpoints:
  GET /api/health   — Health check
  GET /api/status   — Current monitoring status
  GET /api/stats    — Monitoring statistics
  GET /api/alerts   — Recent alerts
  GET /api/network  — Network traffic stats
"""

import time
import threading
from typing import Any, Callable, Dict, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from monitor.logger import get_logger

logger = get_logger(__name__)

# ---- FastAPI Application ----

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production Monitoring System Dashboard API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS (allow all in development, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else [],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Shared state — set by MonitoringEngine at startup
_state: Dict[str, Any] = {
    "start_time": time.time(),
    "get_website_stats": None,
    "get_network_stats": None,
    "get_ddos_stats": None,
    "get_recent_alerts": None,
    "get_recent_events": None,
}


def set_dashboard_state(**kwargs: Any) -> None:
    """Inject callback functions from the engine."""
    _state.update(kwargs)


# ---- Endpoints ----

@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "uptime_seconds": round(time.time() - _state["start_time"], 1),
    }


@app.get("/api/status")
async def monitoring_status() -> Dict[str, Any]:
    """Current status of all monitoring subsystems."""
    website_stats = {}
    network_stats = {}
    ddos_stats = {}

    if _state.get("get_website_stats"):
        try:
            website_stats = _state["get_website_stats"]()
        except Exception:
            website_stats = {"error": "unavailable"}

    if _state.get("get_network_stats"):
        try:
            network_stats = _state["get_network_stats"]()
        except Exception:
            network_stats = {"error": "unavailable"}

    if _state.get("get_ddos_stats"):
        try:
            ddos_stats = _state["get_ddos_stats"]()
        except Exception:
            ddos_stats = {"error": "unavailable"}

    return {
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "website": website_stats,
        "network": network_stats,
        "ddos": ddos_stats,
    }


@app.get("/api/stats")
async def monitoring_stats() -> Dict[str, Any]:
    """Detailed monitoring statistics."""
    website_stats = {}
    if _state.get("get_website_stats"):
        try:
            website_stats = _state["get_website_stats"]()
        except Exception:
            website_stats = {"error": "unavailable"}

    return {
        "uptime_seconds": round(time.time() - _state["start_time"], 1),
        "website": website_stats,
    }


@app.get("/api/alerts")
async def recent_alerts() -> Dict[str, Any]:
    """List recent alerts."""
    alerts = []
    if _state.get("get_recent_alerts"):
        try:
            alerts = _state["get_recent_alerts"]()
        except Exception:
            pass
    return {"alerts": alerts}


@app.get("/api/network")
async def network_stats_endpoint() -> Dict[str, Any]:
    """Network traffic statistics."""
    stats = {}
    if _state.get("get_network_stats"):
        try:
            stats = _state["get_network_stats"]()
        except Exception:
            stats = {"error": "unavailable"}
    return {"network": stats}


# ---- Server Runner ----

class DashboardServer:
    """Run the FastAPI dashboard in a background thread."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        self.host = host or settings.DASHBOARD_HOST
        self.port = port or settings.DASHBOARD_PORT
        self._thread: Optional[threading.Thread] = None
        self._server: Optional[uvicorn.Server] = None

    def start(self) -> None:
        """Start dashboard in a background thread."""
        self._thread = threading.Thread(
            target=self._run,
            name="DashboardAPI",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "Dashboard API started at http://%s:%d",
            self.host, self.port,
        )

    def stop(self) -> None:
        """Signal the server to shut down."""
        if self._server:
            self._server.should_exit = True
        logger.info("Dashboard API stopped")

    def _run(self) -> None:
        """Uvicorn server runner."""
        config = uvicorn.Config(
            app=app,
            host=self.host,
            port=self.port,
            log_level="warning",
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._server.run()
