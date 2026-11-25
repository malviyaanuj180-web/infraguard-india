# INFRAGUARD — Autonomous Infrastructure Health Monitoring & Structural Integrity Twin

An enterprise multi-page structural health monitoring (SHM) platform that fuses **Drone Computer Vision (YOLOv8-seg + Scikit-image/OpenCV)**, **3D LiDAR Point Clouds (Open3D / SVD Kabsch ICP)**, **IoT Vibration & Strain Telemetry (SciPy Welch PSD + PyTorch LSTM Autoencoder)**, **Sensor Trust Guard (Hardware Fault Quarantine)**, and **Physics-Informed Fracture Mechanics (Paris' Law RUL)** inside the **Kage / ThreeUI Cyber-Structural Command Center**.

---

## 🌟 6-Page Enterprise Web Application Architecture

1. **📊 Overview (`#overview`)**
   - **4-KPI Telemetry Ribbon:** Structural Health Index (`0–100` mapped to FHWA NBIS `1–9`), Paris' Law RUL (days & $\Delta K / K_{IC}$ fracture margin), 3D LiDAR Sag Deflection vs. AASHTO $L/800$, and the **"False-Alarm vs. Silent-Killer" Cross-Check Matrix**.
   - **Regional Portfolio Fleet Hub:** Automated urgency ranking across state highway structures (`CA-DOT-BR-8842`, `MH-MSRDC-BW-102`, `NY-DOT-OV-409`, `CA-DOT-RW-214`) with **Environmental & Monsoon Stress Lens** switching (*Dry Baseline*, *Post-Monsoon*, *Traffic Surge*).
   - **Actionable Field Dispatch Card & Embedded GIS Map:** One-click dispatch for the #1 ranked asset + Geotechnical GIS corridor view.
2. **🌐 3D Digital Twin (`#twin`)**
   - **Interactive Three.js Holographic Bridge:** Glowing wireframe + structural mesh, Ghost $T_0$ baseline overlay, Open3D ICP 3D LiDAR point cloud overlay (`LiDAR Cloud (ICP)`), animated laser scanline, and 4 clickable/hoverable 3D Anomaly Beacons.
   - **5-Year Degradation Time-Machine Scrubber (`Year 0` → `Year 5`):** Smoothly animates deck sag deformation, crack propagation, natural frequency loss, and RUL decay.
   - **"What-If" Stress & Retrofit Sensitivity Engine:** Live sliders for **Heavy Truck Load (`50%–200%`)**, **Environmental Corrosion (`0.5x–3.0x`)**, and **Carbon-Fiber (CFRP) Retrofit (`+45%` fatigue life extension)**.
3. **🚁 Drone AI Vision (`#vision`)**
   - **High-Resolution Drone RGB Inspection Lab:** Preset switcher + custom drone photo uploader (`📤 Upload Drone Photo`) + live Camera GSD calibration (`Flight Altitude m`, `Focal Length mm`).
   - **Physical Quantification & ACI 224R Grading:** Extracts crack width (mm), skeletonized crack length (mm), spalling area ($\text{cm}^2$), corrosion coverage (%), and exposed rebar galvanic risk.
4. **📡 IoT & Sensor Trust (`#telemetry`)**
   - **Live 200 Hz WebSocket Oscilloscope:** Real-time tri-axial accelerometer waveform (`ws://localhost:8000/ws/telemetry`), Optical FBG Strain ($\mu\varepsilon$), Welch PSD Mode 1 Frequency (Hz), and PyTorch LSTM Autoencoder MSE.
   - **Sensor Trust Guard & Fault Quarantine:** Live audit table that isolates flatlines, clipping, and loose mountings (`🛡️ Test Fault Quarantine`) so hardware faults never trigger false structural panic.
5. **📋 Field Dispatch (`#dispatch`)**
   - **Enterprise Work Orders Hub:** Active & dispatched structural work orders (`WO-INFRAGUARD-...`), live emergency crew dispatch creation, and printable Official Field Work Order sheets.
6. **📑 Reports & Audit (`#reports`)**
   - **Explainable Engineering (XAI) Notices & Regulatory Reference:** Plain-English engineering directives citing **ACI 224R-01**, **AASHTO L/800**, and **FHWA NBIS Item 58/59**.
   - **SQLite Persistent Telemetry Audit Log:** Live view of `backend/shm_records.db` with 1-click **CSV**, **JSON**, and **Print Executive Report** exporters.

---

## 🔐 Authentication & Phone SMS OTP 2FA

Click the user profile chip in the top-right navbar to sign in or test 2FA onboarding:
- **1-Click Evaluator Demo Accounts:**
  - **Chief Structural Engineer:** `engineer@infraguard.ai` / `InfraGuard@2026`
  - **Senior NDT Field Inspector:** `inspector@infraguard.ai` / `InfraGuard@2026`
  - **DOT Infrastructure Director:** `director@infraguard.ai` / `InfraGuard@2026`
- **Passwordless Phone SMS OTP Login & New Engineer Registration:**
  - Click **`📲 Login via Phone SMS OTP`** or register a new engineer with a mobile number to trigger an on-screen simulated **Mobile SMS Push Notification** with a 6-digit verification passcode.

---

## 🚀 Quickstart (Local Development)

### Option A: 1-Click Launcher
- **Windows:** Double-click `start_infraguard.bat` (or run `.\start_infraguard.bat`)
- **Linux / macOS:** Run `bash start_infraguard.sh`

### Option B: Manual CLI
```bash
pip install -r requirements.txt
python -m sample_data.generate_demo_data
python smoke_test.py
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in your browser.

---

## ☁️ Production & Cloud Deployment Guide

This repository is pre-configured for one-step deployment to **Docker**, **Render**, **Railway**, **Fly.io**, or any Linux VPS:

### 1. Docker & Docker Compose
```bash
docker compose up --build -d
```
The container automatically generates benchmark datasets, exposes port `8000`, and monitors `/api/health`.

### 2. Render.com (Blueprint Deployment)
1. Push this directory to a GitHub repository.
2. In Render, click **New +** → **Blueprint** (or **Web Service**) and connect your repository.
3. Render automatically detects [`render.yaml`](render.yaml) and deploys the FastAPI + Static Web application.

### 3. Railway.app
1. Push to GitHub and click **New Project** → **Deploy from GitHub repo** in Railway.
2. Railway automatically uses [`railway.json`](railway.json) and [`Dockerfile`](Dockerfile) with `/api/health` readiness checks.

---

## 🗂️ Project Directory Structure
```text
infra-health-monitor/
├── backend/
│   ├── main.py                     # FastAPI REST & WebSocket server
│   ├── auth_manager.py             # SHA-256 Auth, Demo Accounts & Phone SMS OTP 2FA
│   ├── portfolio_manager.py        # Multi-asset ranking, Monsoon Lens & Work Orders
│   ├── sensor_trust_guard.py       # Hardware fault isolation & sabotage guard
│   ├── database.py                 # SQLite persistence layer & CSV/JSON exporters
│   ├── vision_quantifier.py        # YOLOv8-seg + Scikit-image/OpenCV skeletonization
│   ├── lidar_fusion.py             # Open3D & SVD Kabsch ICP alignment & displacement
│   ├── vibration_lstm.py           # SciPy FFT/Welch + PyTorch LSTM autoencoder
│   └── rul_engine.py               # Cross-modal matrix, SHI (0-100), Paris' Law RUL
├── frontend/
│   ├── index.html                  # 6-page INFRAGUARD enterprise web application
│   ├── styles.css                  # Kage / ThreeUI cyber-structural design system
│   ├── app.js                      # Multi-page router, Three.js twin, WebSocket & Auth
│   └── libs/                       # Bundled offline Three.js & OrbitControls
├── sample_data/
│   ├── generate_demo_data.py       # Benchmark synthetic datasets generator
│   ├── point_clouds/               # Baseline T0 and Deformed T1 3D point clouds
│   ├── test_images/                # Sample drone inspection images
│   └── telemetry/                  # 3D anomaly beacons metadata
├── Dockerfile                      # Production container definition
├── docker-compose.yml              # One-command container orchestration
├── render.yaml                     # Render.com cloud blueprint
├── railway.json                    # Railway.app deployment manifest
├── Procfile                        # PaaS process declaration
├── start_infraguard.bat            # Windows 1-click launcher
├── start_infraguard.sh             # Linux/macOS 1-click launcher
├── smoke_test.py                   # Automated end-to-end test suite
├── requirements.txt
└── README.md
```
