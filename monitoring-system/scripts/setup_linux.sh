#!/usr/bin/env bash
# ============================================================
# Monitoring System — Linux Setup Script
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

set -e

echo ""
echo "============================================"
echo "  Monitoring System — Linux Setup"
echo "  Soft Game Studio"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Install with:"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PY_VERSION=$(python3 --version)
echo "[OK] $PY_VERSION"

# Check libpcap
if command -v tcpdump &> /dev/null; then
    echo "[OK] libpcap available (tcpdump found)"
elif [ -f /usr/lib/libpcap.so ] || [ -f /usr/lib64/libpcap.so ]; then
    echo "[OK] libpcap found"
else
    echo "[WARNING] libpcap is NOT installed!"
    echo "  Packet sniffing will be disabled."
    echo "  Install with:"
    echo "    Ubuntu/Debian:  sudo apt install libpcap-dev"
    echo "    Fedora/RHEL:    sudo dnf install libpcap-devel"
    echo "    Arch:           sudo pacman -S libpcap"
    echo ""
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "[SETUP] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[SETUP] Installing dependencies..."
pip install -r requirements.txt

# Create directories
mkdir -p logs database

# Copy .env if not exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[OK] Created .env from .env.example"
fi

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "To run the monitoring system:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "To run with sudo (for packet sniffing):"
echo "  sudo venv/bin/python app.py"
echo ""
echo "To run tests:"
echo "  python -m pytest tests/ -v"
echo ""
