# ============================================================
# Monitoring System — Main Entry Point
# Copyright (c) 2026 Soft Game Studio
# License: MIT
#
# Production-ready entry point with async orchestration,
# graceful shutdown, system checks, and Rich terminal UI.
# ============================================================

"""
app.py — Application Entry Point

Starts the MonitoringEngine which orchestrates:
  - Website health monitoring (async)
  - Network traffic analysis (threaded)
  - DDoS detection
  - Alert management
  - Dashboard API (FastAPI)
  - Logging & database
"""

import asyncio
import os
import signal
import sys
import time
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from colorama import init as colorama_init

# Initialize colorama for Windows ANSI support
colorama_init()

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from monitor.logger import get_logger, setup_root_logger
from monitor.utils import (
    check_npcap_installed,
    get_platform_info,
    is_admin,
    is_windows,
)

logger = get_logger(__name__)
console = Console()

# ============================================================
# ASCII BANNER
# ============================================================

BANNER = r"""
 ███╗   ███╗ ██████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗
 ████╗ ████║██╔═══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗
 ██╔████╔██║██║   ██║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝
 ██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗
 ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║
 ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
"""


# ============================================================
# MONITORING ENGINE
# ============================================================

class MonitoringEngine:
    """
    Central orchestrator that manages all monitoring subsystems.

    Handles startup, shutdown, and inter-component wiring.
    """

    def __init__(self) -> None:
        self.start_time = time.time()
        self._shutdown_event = asyncio.Event()

        # Components (initialized in start())
        self.website_monitor = None
        self.network_monitor = None
        self.ddos_detector = None
        self.alert_manager = None
        self.dashboard = None
        self.database = None

    async def start(self) -> None:
        """Initialize and start all subsystems."""
        self._print_banner()
        self._print_system_info()

        # ---- Initialize components ----

        # 1. Database
        from monitor.database import MonitorDatabase
        self.database = MonitorDatabase()
        logger.info("Database ready")

        # 2. Alert Manager
        from monitor.alerts import AlertManager
        self.alert_manager = AlertManager()

        # 3. DDoS Detector
        from monitor.ddos import DDoSDetector
        self.ddos_detector = DDoSDetector(
            on_alert=lambda msg, sev: asyncio.run_coroutine_threadsafe(
                self.alert_manager.send_alert(msg, sev),
                asyncio.get_event_loop(),
            ),
        )

        # 4. Network Monitor
        from monitor.network import NetworkMonitor
        self.network_monitor = NetworkMonitor(
            on_packet=self._on_packet,
            on_alert=lambda msg, sev: asyncio.run_coroutine_threadsafe(
                self.alert_manager.send_alert(msg, sev),
                asyncio.get_event_loop(),
            ),
        )
        self._print_network_status()

        if settings.ENABLE_PACKET_MONITORING and self.network_monitor.available:
            self.network_monitor.start()

        # 5. Website Monitor
        from monitor.website import WebsiteMonitor
        self.website_monitor = WebsiteMonitor(
            on_alert=self.alert_manager.send_alert,
            on_check=self._on_website_check,
        )
        await self.website_monitor.start()

        # 6. Dashboard API
        from monitor.dashboard import DashboardServer, set_dashboard_state
        set_dashboard_state(
            start_time=self.start_time,
            get_website_stats=lambda: self.website_monitor.stats.to_dict(),
            get_network_stats=lambda: self.network_monitor.get_stats(),
            get_ddos_stats=lambda: self.ddos_detector.get_stats(),
            get_recent_alerts=lambda: self.database.get_recent_alerts(20),
            get_recent_events=lambda: self.database.get_recent_events(20),
        )
        self.dashboard = DashboardServer()
        self.dashboard.start()

        # ---- Startup complete ----
        self._print_startup_summary()
        logger.info("All systems online — monitoring started")

        # Wait for shutdown signal
        await self._shutdown_event.wait()

    async def stop(self) -> None:
        """Gracefully shut down all subsystems."""
        console.print("\n[bold yellow]⏳ Shutting down gracefully...[/]")
        logger.info("Shutdown initiated")

        if self.website_monitor:
            await self.website_monitor.stop()

        if self.network_monitor:
            self.network_monitor.stop()

        if self.dashboard:
            self.dashboard.stop()

        console.print("[bold green]✓ Shutdown complete[/]")
        logger.info("Shutdown complete")

    def request_shutdown(self) -> None:
        """Signal the engine to shut down."""
        self._shutdown_event.set()

    # ---- Callbacks ----

    def _on_packet(self, packet) -> None:
        """Called for each captured packet — feed to DDoS detector."""
        if self.ddos_detector and self.network_monitor:
            try:
                IP = self.network_monitor._scapy_IP
                if IP and packet.haslayer(IP):
                    self.ddos_detector.record_packet(packet[IP].src)
            except Exception:
                pass

    def _on_website_check(self, result) -> None:
        """Called after each website check — log to database."""
        if self.database:
            try:
                self.database.log_event(
                    event_type="website_check",
                    url=result.url,
                    status_code=result.status_code,
                    response_ms=result.response_time_ms,
                    message=result.error or result.status.value,
                )
            except Exception:
                logger.exception("Failed to log website check")

    # ---- Terminal Output ----

    def _print_banner(self) -> None:
        """Display the startup banner."""
        console.print(
            Panel(
                Text(BANNER, style="bold cyan"),
                title="[bold white]Soft Game Studio[/]",
                subtitle=f"[dim]v{settings.APP_VERSION}[/]",
                border_style="bright_cyan",
            )
        )

    def _print_system_info(self) -> None:
        """Display system compatibility information."""
        info = get_platform_info()

        table = Table(
            title="System Information",
            show_header=False,
            border_style="dim",
            padding=(0, 2),
        )
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="white")

        table.add_row("OS", f"{info['os']} {info['os_version'][:30]}")
        table.add_row("Python", info["python_version"])
        table.add_row("Architecture", info["architecture"])
        table.add_row("Hostname", info["hostname"])
        table.add_row("Environment", settings.ENVIRONMENT)
        table.add_row(
            "Admin Privileges",
            "[green]Yes[/]" if is_admin() else "[yellow]No[/]",
        )

        console.print(table)
        console.print()

    def _print_network_status(self) -> None:
        """Display network monitoring availability."""
        if self.network_monitor.available:
            console.print(
                "[bold green]✓[/] Packet sniffing: "
                "[green]Available[/]"
            )
        else:
            console.print(
                "[bold yellow]⚠[/] Packet sniffing: "
                "[yellow]Disabled[/]"
            )
            # Print the reason in a warning panel
            console.print(
                Panel(
                    self.network_monitor.unavailable_reason,
                    title="[yellow]Network Sniffing Unavailable[/]",
                    border_style="yellow",
                )
            )
            console.print(
                "[dim]Website monitoring will continue without "
                "packet sniffing.[/]\n"
            )

    def _print_startup_summary(self) -> None:
        """Display a summary of all active components."""
        table = Table(
            title="Monitoring Status",
            border_style="bright_green",
            padding=(0, 2),
        )
        table.add_column("Component", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Details", style="dim")

        # Website monitor
        table.add_row(
            "Website Monitor",
            "[green]● Active[/]",
            settings.WEBSITE_URL,
        )

        # Network monitor
        if self.network_monitor.available and settings.ENABLE_PACKET_MONITORING:
            table.add_row(
                "Network Monitor",
                "[green]● Active[/]",
                f"Interface: {self.network_monitor.interface}",
            )
        else:
            table.add_row(
                "Network Monitor",
                "[yellow]○ Disabled[/]",
                "Npcap not found or not admin",
            )

        # DDoS detection
        if settings.ENABLE_DDOS_DETECTION:
            table.add_row(
                "DDoS Detection",
                "[green]● Active[/]",
                f"Threshold: {settings.DDOS_PACKET_THRESHOLD}/min",
            )
        else:
            table.add_row(
                "DDoS Detection",
                "[yellow]○ Disabled[/]",
                "",
            )

        # Alerts
        alert_details = []
        if settings.telegram_configured:
            alert_details.append("Telegram")
        if settings.discord_configured:
            alert_details.append("Discord")
        alert_details.append("Console")
        table.add_row(
            "Alerts",
            "[green]● Active[/]",
            ", ".join(alert_details),
        )

        # Dashboard
        table.add_row(
            "Dashboard API",
            "[green]● Active[/]",
            f"http://localhost:{settings.DASHBOARD_PORT}",
        )

        console.print()
        console.print(table)
        console.print()
        console.print(
            f"[bold green]🚀 {settings.APP_NAME} is running![/]"
        )
        console.print(
            f"[dim]Dashboard: http://localhost:{settings.DASHBOARD_PORT}/api/docs[/]"
        )
        console.print(
            "[dim]Press Ctrl+C to stop[/]\n"
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Application entry point."""
    # Setup logging first
    setup_root_logger(
        log_dir=settings.LOG_DIR,
        log_file=settings.LOG_FILE,
        enable_file=settings.ENABLE_FILE_LOGGING,
        enable_console=settings.ENABLE_CONSOLE_LOGGING,
    )

    # Create directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("database", exist_ok=True)

    engine = MonitoringEngine()

    # ---- Signal Handlers for graceful shutdown ----
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def _handle_signal() -> None:
        logger.info("Received shutdown signal")
        engine.request_shutdown()

    # Register signal handlers
    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _handle_signal)

    # ---- Run ----
    try:
        loop.run_until_complete(engine.start())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Interrupted by user[/]")
    finally:
        loop.run_until_complete(engine.stop())
        loop.close()


if __name__ == "__main__":
    main()