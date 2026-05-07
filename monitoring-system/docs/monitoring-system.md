# Monitoring System — Technical Documentation

**Copyright (c) 2026 Soft Game Studio — MIT License**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [How Packet Sniffing Works](#how-packet-sniffing-works)
3. [Firebase Monitoring](#firebase-monitoring)
4. [Real-Time Monitoring Workflow](#real-time-monitoring-workflow)
5. [Security Considerations](#security-considerations)
6. [Production Deployment](#production-deployment)
7. [Scalability Guide](#scalability-guide)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting](#troubleshooting)
10. [Future Improvements](#future-improvements)

---

## Architecture Overview

### System Design

The monitoring system follows a **modular, event-driven architecture** with the following key components:

```
┌─────────────────────────────────────────────────┐
│                  MonitoringEngine                │
│              (app.py — Orchestrator)             │
├────────┬────────┬──────────┬────────┬───────────┤
│Website │Network │  DDoS    │ Alert  │ Dashboard │
│Monitor │Monitor │Detector  │Manager │   API     │
│(async) │(thread)│(thread)  │(async) │ (thread)  │
├────────┴────────┴──────────┴────────┴───────────┤
│              Shared Components                   │
│    Logger  │  Database  │  Security  │  Config   │
└──────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Concurrency Model |
|-----------|---------------|-------------------|
| `MonitoringEngine` | Lifecycle management, wiring | Main async loop |
| `WebsiteMonitor` | HTTP health checks, Firebase | `asyncio.Task` |
| `NetworkMonitor` | Scapy packet capture | `threading.Thread` |
| `DDoSDetector` | Rate-based anomaly detection | Called from NetworkMonitor thread |
| `AlertManager` | Multi-channel alert dispatch | Async coroutines |
| `DashboardServer` | REST API via FastAPI/Uvicorn | `threading.Thread` |
| `MonitorDatabase` | SQLite persistence | Thread-safe with locks |
| `Logger` | Rotating file + console output | Thread-safe (stdlib) |

### Data Flow

1. **Website checks** run as async tasks in the main event loop
2. **Network packets** are captured in a dedicated thread (Scapy is blocking)
3. Each captured packet is fed to the **DDoS detector**
4. Status changes and anomalies trigger the **AlertManager**
5. All events are persisted to the **SQLite database**
6. The **Dashboard API** reads from shared state and the database

---

## How Packet Sniffing Works

### The Npcap Problem

Scapy requires a **packet capture library** at the OS level:

- **Windows**: Npcap (or legacy WinPcap) — provides `wpcap.dll`
- **Linux**: libpcap — provides `libpcap.so`

Without these, Scapy throws:
```
RuntimeError: Sniffing and sending packets is not available at layer 2: winpcap is not installed
```

### Our Solution

```python
# WRONG — crashes at import time:
from scapy.all import *
sniff(prn=callback, store=False)  # RuntimeError!

# CORRECT — lazy import with detection:
class NetworkMonitor:
    def _check_availability(self):
        # 1. Check Npcap via registry / filesystem
        pcap_ok, msg = check_npcap_installed()
        if not pcap_ok:
            self.available = False
            return

        # 2. Check admin privileges
        if not is_admin():
            self.available = False
            return

        # 3. Try importing Scapy (lazy)
        try:
            from scapy.all import sniff
            self.available = True
        except (ImportError, RuntimeError):
            self.available = False
```

### Detection Methods (Windows)

1. **Filesystem check**: `C:\Windows\System32\Npcap\` directory
2. **Registry check**: `HKLM\SOFTWARE\Npcap` key
3. **Legacy check**: `HKLM\SOFTWARE\WinPcap` key
4. **DLL check**: `C:\Windows\System32\wpcap.dll`

### Fallback Behavior

When Npcap is not available:

- ✅ Website monitoring continues normally
- ✅ Dashboard API continues normally
- ✅ Alerts continue normally
- ⚠️ Packet sniffing is disabled (warning shown)
- ⚠️ DDoS detection is disabled (no packet data)
- ✅ Socket-based port checks still work (`check_port()`)

---

## Firebase Monitoring

### How It Works

Firebase Hosting sites are monitored by:

1. **HTTP health check** — standard GET request to the site URL
2. **Header inspection** — checking for Firebase-specific response headers:
   - `server: Google Frontend`
   - Custom Firebase headers
3. **SSL validation** — verifying the certificate chain
4. **Response time** — measuring latency to Firebase CDN

### Firebase-Specific Considerations

- Firebase sites use Google's CDN, so response times are typically fast
- 5xx errors may indicate Firebase outages (check https://status.firebase.google.com)
- Firebase Hosting supports custom domains — monitor both `.web.app` and custom domains

---

## Real-Time Monitoring Workflow

```
┌──────────┐    ┌───────────┐    ┌──────────┐
│  Timer   │───>│  HTTP GET │───>│ Parse    │
│ (30s)    │    │  Request  │    │ Response │
└──────────┘    └───────────┘    └────┬─────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                    ┌─────▼─────┐           ┌─────▼─────┐
                    │  Status   │           │  Status   │
                    │  UP (2xx) │           │ DOWN/5xx  │
                    └─────┬─────┘           └─────┬─────┘
                          │                       │
                    ┌─────▼─────┐           ┌─────▼─────┐
                    │  Update   │           │  Trigger  │
                    │  Stats    │           │  Alert    │
                    └─────┬─────┘           └─────┬─────┘
                          │                       │
                    ┌─────▼─────────────────▼─────┐
                    │     Log to Database          │
                    └──────────────────────────────┘
```

---

## Security Considerations

### Sensitive Data

- **API tokens** (Telegram, Discord) are loaded from environment variables
- The `.env` file is excluded from Git via `.gitignore`
- Log messages are sanitized via `mask_sensitive()` to remove tokens/passwords

### Network Security

- Packet sniffing requires **administrator/root** — this is by design
- The rate limiter prevents API abuse (default: 100 req/min)
- CORS is restricted in production mode
- Input URLs are sanitized before use

### Docker Security

- The container runs as a **non-root user** (`monitor`)
- Only `NET_RAW` and `NET_ADMIN` capabilities are added (not `--privileged`)
- No unnecessary ports are exposed

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Set `DEBUG=false`
- [ ] Configure alert credentials (Telegram/Discord)
- [ ] Set appropriate `CHECK_INTERVAL` (30–60s recommended)
- [ ] Review `DDOS_PACKET_THRESHOLD`
- [ ] Set up log rotation at the OS level
- [ ] Configure a reverse proxy (nginx) with SSL

### Docker Deployment

```bash
# Build and start
docker-compose up -d --build

# Check health
curl http://localhost:8000/api/health

# View logs
docker-compose logs -f monitoring-system

# Stop
docker-compose down
```

### Systemd Service (Linux)

```ini
[Unit]
Description=Monitoring System
After=network.target

[Service]
Type=simple
User=monitor
WorkingDirectory=/opt/monitoring-system
ExecStart=/opt/monitoring-system/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Scalability Guide

### Current Limits

- Single-process, single-machine design
- SQLite database (single-writer)
- Suitable for monitoring **1–50 websites** and **1 network interface**

### Scaling Strategies

1. **Multiple URLs**: Extend `WebsiteMonitor` to accept a list of URLs
2. **Database**: Migrate from SQLite to PostgreSQL for concurrent writes
3. **Message Queue**: Use Redis/RabbitMQ for alert delivery
4. **Distributed**: Run separate instances per region, aggregate via central API
5. **Metrics**: Export to Prometheus/Grafana for long-term storage and visualization

---

## Performance Optimization

### Current Optimizations

- **Async HTTP** via `aiohttp` — non-blocking website checks
- **Thread-based sniffing** — Scapy runs in its own thread, doesn't block async
- **Thread-safe counters** — `threading.Lock` protects shared state
- **Connection reuse** — `aiohttp.ClientSession` reuses TCP connections
- **Rotating logs** — 10MB cap prevents disk exhaustion

### Tuning Tips

| Parameter | Effect | Recommendation |
|-----------|--------|----------------|
| `CHECK_INTERVAL` | Lower = more checks, more load | 30s for production |
| `MAX_WORKERS` | Concurrent thread pool size | Match CPU cores |
| `DDOS_PACKET_THRESHOLD` | Lower = more sensitive | Tune to your baseline |
| `REQUEST_TIMEOUT` | Higher = tolerates slow sites | 10–15s |

---

## Troubleshooting

### Common Errors

#### `RuntimeError: winpcap is not installed`

**Cause**: Npcap/WinPcap is not installed on Windows.

**Fix**:
1. Download Npcap: https://npcap.com/#download
2. Install with **"WinPcap API-compatible Mode"** enabled
3. Restart your terminal
4. Re-run `python app.py`

**Alternative**: If you don't need packet sniffing, the system will automatically disable it and continue with website monitoring.

#### `ModuleNotFoundError: No module named 'scapy'`

**Fix**:
```bash
pip install scapy
# or
pip install -r requirements.txt
```

#### `PermissionError` during packet sniffing

**Cause**: Packet capture requires elevated privileges.

**Fix**:
- Windows: Run terminal as **Administrator**
- Linux: Use `sudo python app.py`

#### `aiohttp.ClientError` or connection timeouts

**Cause**: Network connectivity issue or target site is slow.

**Fix**:
- Increase `REQUEST_TIMEOUT` in `.env`
- Check your internet connection
- Verify the `WEBSITE_URL` is correct

### Windows Troubleshooting

1. **Npcap installer fails**: Run as Administrator, disable antivirus temporarily
2. **Python not found**: Add Python to PATH during installation
3. **venv activation fails**: Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
4. **Port 8000 in use**: Change `DASHBOARD_PORT` in `.env`

### Linux Troubleshooting

1. **libpcap not found**: `sudo apt install libpcap-dev`
2. **Permission denied**: Use `sudo` or add user to `pcap` group
3. **venv not available**: `sudo apt install python3-venv`

---

## Future Improvements

- [ ] Multiple URL monitoring (URL list in config)
- [ ] Email alert backend (SMTP)
- [ ] Web-based dashboard UI (React/Vue frontend)
- [ ] Prometheus metrics exporter
- [ ] Grafana dashboard templates
- [ ] PostgreSQL database option
- [ ] Redis caching layer
- [ ] Webhook alert backend (generic)
- [ ] SSL certificate expiry monitoring
- [ ] Response body content verification
- [ ] Custom alert rules engine
- [ ] Geographic latency monitoring
- [ ] API key authentication for dashboard
- [ ] Log export to JSON/CSV
- [ ] Automated performance reports

---

*Documentation maintained by Soft Game Studio*
*Last updated: May 2026*
