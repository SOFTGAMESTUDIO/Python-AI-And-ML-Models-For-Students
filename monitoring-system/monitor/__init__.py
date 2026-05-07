# ============================================================
# Monitoring System — Package Initializer
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

"""
monitor — Production Monitoring Toolkit

Provides modules for website monitoring, network traffic
analysis, alerting, DDoS detection, and a dashboard API.
"""

__version__ = "2.0.0"
__author__ = "Soft Game Studio"
__license__ = "MIT"

from monitor.logger import get_logger

__all__ = [
    "get_logger",
]
