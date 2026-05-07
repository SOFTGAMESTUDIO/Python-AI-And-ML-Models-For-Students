# ============================================================
# Monitoring System — Windows Setup Script
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Monitoring System — Windows Setup" -ForegroundColor Cyan
Write-Host "  Soft Game Studio" -ForegroundColor DarkCyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERROR] Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}

$pyVersion = python --version 2>&1
Write-Host "[OK] $pyVersion" -ForegroundColor Green

# Check Npcap
$npcapPath = "$env:SystemRoot\System32\Npcap"
$wpcapDll = "$env:SystemRoot\System32\wpcap.dll"

if (Test-Path $npcapPath) {
    Write-Host "[OK] Npcap found at $npcapPath" -ForegroundColor Green
} elseif (Test-Path $wpcapDll) {
    Write-Host "[OK] WinPcap/Npcap DLL found" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Npcap is NOT installed!" -ForegroundColor Yellow
    Write-Host "  Packet sniffing will be disabled." -ForegroundColor Yellow
    Write-Host "  Download Npcap: https://npcap.com/#download" -ForegroundColor Yellow
    Write-Host "  Enable 'WinPcap API-compatible mode' during install." -ForegroundColor Yellow
    Write-Host ""
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "[SETUP] Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate venv
Write-Host "[SETUP] Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "[SETUP] Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Create directories
New-Item -ItemType Directory -Force -Path logs | Out-Null
New-Item -ItemType Directory -Force -Path database | Out-Null

# Copy .env if not exists
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "[OK] Created .env from .env.example" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run the monitoring system:" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "  python app.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run tests:" -ForegroundColor White
Write-Host "  python -m pytest tests/ -v" -ForegroundColor Yellow
Write-Host ""
