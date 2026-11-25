@echo off
title INFRAGUARD — Autonomous Structural Health Monitoring Platform
echo ============================================================================
echo   INFRAGUARD // AUTONOMOUS STRUCTURAL INTEGRITY & DIGITAL TWIN PLATFORM
echo ============================================================================
echo.
cd /d "%~dp0"

if not exist "sample_data\test_images\span_ab_crack_critical.jpg" (
    echo [1/2] Generating benchmark structural sample datasets...
    python -m sample_data.generate_demo_data
)

echo [2/2] Starting INFRAGUARD FastAPI Production Server on http://127.0.0.1:8000 ...
echo       Open your browser to: http://127.0.0.1:8000
echo       Interactive API Docs: http://127.0.0.1:8000/docs
echo.
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
