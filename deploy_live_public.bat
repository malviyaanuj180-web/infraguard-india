@echo off
title INFRAGUARD INDIA — Live Cloud & Local Deployment
cd /d "%~dp0"
echo ============================================================================
echo   INFRAGUARD INDIA - SUSTAINOVA 2026 IDEATHON (TEAM BYTE BUSTERS)
echo   Starting Production FastAPI Server (Port 8000) + Cloudflare HTTPS Tunnel
echo ============================================================================
start "InfraGuard FastAPI Server" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
echo.
echo Launching Public HTTPS Cloudflare Tunnel...
.\cloudflared.exe tunnel --url http://127.0.0.1:8000 --no-autoupdate
pause
