# 🛡️ Monitoring System

**Production-Ready Network & Website Monitoring Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)

> Built by **Soft Game Studio** — Open Source Monitoring Toolkit

---

## 📋 Overview

A professional, production-ready monitoring system built in Python that provides real-time website monitoring, network traffic analysis, DDoS detection, and multi-channel alerting. Designed for both Windows and Linux with graceful fallback handling for packet capture dependencies.

### Key Highlights

- ✅ **Windows + Linux** cross-platform support
- ✅ **Npcap/WinPcap auto-detection** with graceful fallback
- ✅ **Async architecture** for high-performance monitoring
- ✅ **FastAPI dashboard** with REST API endpoints
- ✅ **Telegram & Discord** alert integration
- ✅ **Docker** ready for production deployment

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Website Monitoring** | Async HTTP health checks with response time tracking |
| **Firebase Monitoring** | Firebase Hosting status and header validation |
| **Packet Sniffing** | Scapy-based network traffic capture (requires Npcap) |
| **Network Analysis** | Protocol classification (TCP/UDP/ICMP/DNS) |
| **DDoS Detection** | Sliding-window packet rate monitoring per source IP |
| **Telegram Alerts** | Real-time alerts via Telegram Bot API |
| **Discord Alerts** | Alerts via Discord Webhooks |
| **Dashboard API** | FastAPI REST endpoints for health, status, stats |
| **Logging** | Rotating file logs + Rich console output |
| **Database** | SQLite event storage with auto-migration |
| **Retry System** | Exponential backoff for failed checks |
| **Rate Limiting** | Token-bucket rate limiter for security |
| **Docker Support** | Dockerfile + docker-compose.yml included |
| **Graceful Shutdown** | Signal handling for clean process termination |

---

## 📁 Project Structure

```
monitoring-system/
│
├── app.py                  # Main entry point & MonitoringEngine
├── config.py               # Configuration with env var support
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── LICENSE                  # MIT License
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── Dockerfile              # Docker container build
├── docker-compose.yml      # Docker Compose orchestration
│
├── monitor/                # Core monitoring package
│   ├── __init__.py         # Package metadata & exports
│   ├── website.py          # Website & Firebase monitor
│   ├── network.py          # Network traffic monitor (Scapy)
│   ├── alerts.py           # Alert manager (Telegram/Discord)
│   ├── logger.py           # Logging system (rotating files)
│   ├── database.py         # SQLite event storage
│   ├── dashboard.py        # FastAPI dashboard API
│   ├── ddos.py             # DDoS detection engine
│   ├── utils.py            # Utilities (Npcap check, retry, etc.)
│   └── security.py         # Security helpers (rate limit, sanitize)
│
├── tests/                  # Unit tests
│   ├── test_website.py     # Website monitor tests
│   ├── test_network.py     # Network monitor tests
│   └── test_alerts.py      # Alert system tests
│
├── docs/                   # Documentation
│   └── monitoring-system.md
│
├── scripts/                # Setup scripts
│   ├── setup_windows.ps1   # Windows PowerShell setup
│   └── setup_linux.sh      # Linux Bash setup
│
├── logs/                   # Log files (auto-created)
└── database/               # SQLite database (auto-created)
```

---

## 🔧 Installation

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Npcap** (optional — for packet sniffing on Windows)

### Windows Setup

```powershell
# 1. Clone the repository
git clone https://github.com/softgamestudio/monitoring-system.git
cd monitoring-system

# 2. Run the setup script
.\scripts\setup_windows.ps1

# OR manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env with your settings

# 4. Run
python app.py
```

### Linux Setup

```bash
# 1. Clone the repository
git clone https://github.com/softgamestudio/monitoring-system.git
cd monitoring-system

# 2. Run the setup script
chmod +x scripts/setup_linux.sh
./scripts/setup_linux.sh

# OR manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run
python app.py

# For packet sniffing (requires root):
sudo venv/bin/python app.py
```

---

## 🖥️ Npcap Installation Guide (Windows)

Packet sniffing requires **Npcap** on Windows. Without it, the system will still run — website monitoring continues, only packet sniffing is disabled.

### Steps

1. Download Npcap from: **https://npcap.com/#download**
2. Run the installer **as Administrator**
3. ✅ Check **"WinPcap API-compatible Mode"**
4. ✅ Check **"Install Npcap in WinPcap API-compatible Mode"**
5. Complete the installation
6. **Restart your terminal**
7. Run `python app.py` — packet sniffing should now work

### Verify Installation

```powershell
# Check if Npcap is installed:
Test-Path "$env:SystemRoot\System32\Npcap"

# Or check for wpcap.dll:
Test-Path "$env:SystemRoot\System32\wpcap.dll"
```

---

## 🌐 API Routes

The dashboard API runs on `http://localhost:8000` by default.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check — returns system status |
| `/api/status` | GET | Current monitoring status (all subsystems) |
| `/api/stats` | GET | Detailed monitoring statistics |
| `/api/alerts` | GET | Recent alert history |
| `/api/network` | GET | Network traffic statistics |
| `/api/docs` | GET | Interactive Swagger documentation |
| `/api/redoc` | GET | ReDoc API documentation |

### Example Response — `/api/health`

```json
{
  "status": "healthy",
  "app": "Monitoring System",
  "version": "2.0.0",
  "uptime_seconds": 3600.5
}
```

---

## ⚙️ Configuration

All settings are loaded from environment variables (`.env` file).

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `development` or `production` |
| `WEBSITE_URL` | `https://softgamestudios.web.app` | URL to monitor |
| `CHECK_INTERVAL` | `30` | Seconds between checks |
| `REQUEST_TIMEOUT` | `10` | HTTP request timeout (seconds) |
| `TELEGRAM_BOT_TOKEN` | — | Telegram Bot API token |
| `TELEGRAM_CHAT_ID` | — | Telegram chat ID for alerts |
| `DISCORD_WEBHOOK_URL` | — | Discord webhook URL |
| `DASHBOARD_PORT` | `8000` | Dashboard API port |
| `ENABLE_PACKET_MONITORING` | `true` | Enable/disable packet sniffing |
| `ENABLE_DDOS_DETECTION` | `true` | Enable/disable DDoS detection |

See `.env.example` for all available options.

---

## 🐳 Docker Usage

### Build and Run

```bash
# Build the image
docker build -t monitoring-system .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker Compose Configuration

The `docker-compose.yml` includes:
- Automatic restart (`unless-stopped`)
- Volume mounts for logs and database persistence
- Health checks
- `NET_RAW` + `NET_ADMIN` capabilities for packet capture

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_website.py -v

# Run with coverage
python -m pytest tests/ --cov=monitor -v
```

---

## ⚠️ Security Warning

- **Never commit your `.env` file** — it may contain API tokens and secrets
- The `.gitignore` is configured to exclude `.env` automatically
- Packet sniffing requires **administrator/root** privileges
- Use environment variables for all sensitive configuration
- The rate limiter helps prevent API abuse
- In production, restrict CORS origins in `dashboard.py`

---

## 📊 Screenshots

> *Screenshots will be added after the first production deployment.*

| Dashboard API | Terminal UI | Alert Example |
|:---:|:---:|:---:|
| *Coming soon* | *Coming soon* | *Coming soon* |

---

## 🚀 Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Set `DEBUG=false`
3. Configure Telegram/Discord alert credentials
4. Use Docker Compose for container deployment
5. Set up a reverse proxy (nginx) for the dashboard API
6. Enable SSL/TLS for the API endpoint
7. Monitor logs in `logs/system.log`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

### Code Standards

- Use type hints on all functions
- Add docstrings to all public methods
- Follow PEP 8 style guidelines
- Write unit tests for new features
- Keep modules focused and single-responsibility

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

**Copyright (c) 2026 Soft Game Studio**

---

## 📞 Support

- **Issues**: Open a GitHub issue
- **Organization**: [Soft Game Studio](https://github.com/softgamestudio)

---

*Built with ❤️ by Soft Game Studio*
