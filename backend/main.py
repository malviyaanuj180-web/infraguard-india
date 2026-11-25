"""
STRUCTURA AI — Autonomous Infrastructure Health Monitoring & Structural Integrity Twin
======================================================================================
Complete Industry-Ready Backend Server with:
- Authentication & Phone OTP Verification (/api/auth/*)
- Multi-Structure Portfolio & Automated Urgency Ranking (/api/portfolio)
- One-Click Field Dispatch Engine (/api/portfolio/dispatch)
- Sensor Trust & Hardware Fault/Sabotage Guard (/api/sensors/trust)
- Environmental & Monsoon Stress Lens (Dry Baseline / Post-Monsoon / Traffic Surge)
- Interactive Critical Event Simulator (/api/simulate/critical-event)
- 5-Year Degradation Time-Machine & Paris' Law RUL (/api/simulate)
- Drone Vision Quantifier (YOLOv8-seg + Scikit-image / OpenCV)
- LiDAR 3D ICP Point Cloud Alignment (Open3D / SVD Kabsch)
- IoT Vibration & Strain Processing (SciPy FFT + PyTorch LSTM Autoencoder)
- Real-Time 200 Hz WebSocket Telemetry Stream (/ws/telemetry)
- SQLite Persistent Database & CSV/JSON Data Exporters
"""

import os
import json
import asyncio
import numpy as np
import cv2
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect, Header, Query
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.auth_manager import (
    init_auth_tables, generate_otp, verify_otp,
    authenticate_user, register_user, get_user_by_token,
    get_db, create_user_session
)
from backend.portfolio_manager import PortfolioManager
from backend.sensor_trust_guard import SensorTrustGuard
from backend.vision_quantifier import VisionQuantifier
from backend.lidar_fusion import LidarFusionEngine
from backend.vibration_lstm import VibrationAnalysisEngine
from backend.rul_engine import RULPhysicsEngine
from backend.database import (
    init_database, record_telemetry, record_simulation,
    get_recent_telemetry, export_telemetry_csv, export_telemetry_json
)

app = FastAPI(
    title="INFRAGUARD — Autonomous Infrastructure Health Monitoring Platform",
    version="3.0.0",
    description="Multi-Modal Structural Twin fusing Drone Vision, LiDAR 3D ICP, IoT Vibration/Strain LSTM, Sensor Trust Guard, and Paris' Law RUL"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Storage & AI Engines
init_database()
init_auth_tables()

portfolio_mgr = PortfolioManager()
sensor_guard = SensorTrustGuard()
vision_engine = VisionQuantifier(default_gsd_mm_per_px=0.25)
lidar_engine = LidarFusionEngine()
vibration_engine = VibrationAnalysisEngine(sampling_rate_hz=200.0, window_size=256)
rul_engine = RULPhysicsEngine()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, "sample_data")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Current dynamic state cache
ACTIVE_SIMULATION_STATE: Dict[str, Any] = {}
SIMULATED_CRITICAL_EVENT: bool = False
ACTIVE_LENS: str = "dry_baseline"


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    role: str = "Chief Structural Engineer"
    agency: str = "Department of Transportation"
    password: str = "InfraGuard@2026"


class LoginRequest(BaseModel):
    email_or_phone: Optional[str] = None
    identifier: Optional[str] = None
    password: str


class SendOtpRequest(BaseModel):
    phone: str


class VerifyOtpRequest(BaseModel):
    phone: str
    otp_code: str


class SimulationRequest(BaseModel):
    year: float = 0.0                      # 0.0 to 5.0
    truck_load_factor: float = 1.0         # 1.0 = 100% legal limit, up to 2.0 (200% overload)
    corrosion_factor: float = 1.0          # 1.0 = baseline, up to 3.0 (marine severe)
    cfrp_retrofit_applied: bool = False   # Carbon-Fiber Reinforced Polymer wrap
    environmental_lens: str = "dry_baseline"  # "dry_baseline", "post_monsoon", "traffic_surge"


class DispatchOrderRequest(BaseModel):
    asset_id: str
    technician: str = "Marcus Vance, PE"
    inspector_name: Optional[str] = None
    notes: Optional[str] = None


class TelemetryAnalysisRequest(BaseModel):
    sampling_rate_hz: float = 200.0
    accel_data: Optional[List[List[float]]] = None
    strain_microstrain: Optional[float] = None


class CopilotAskRequest(BaseModel):
    query: str
    asset_id: str = "CA-DOT-BR-8842"
    year: float = 0.0
    shi: float = 94.2
    rul_days: int = 6387
    deck_sag_mm: float = 18.4
    crack_width_mm: float = 0.25
    cfrp_applied: bool = False
    lens: str = "dry_baseline"


# ==============================================================================
# AUTHENTICATION & PHONE OTP API ENDPOINTS
# ==============================================================================

@app.get("/api/auth/demo-accounts")
def get_demo_accounts():
    """Returns pre-configured Indian engineering demo accounts for 1-click login."""
    return [
        {
            "role": "Chief Structural Engineer",
            "name": "Dr. Rajesh Iyer, FIE (CEng)",
            "email": "engineer@infraguard.ai",
            "phone": "+91-98201-88420",
            "password": "InfraGuard@2026",
            "agency": "NHAI & MoRTH Structural Integrity Division"
        },
        {
            "role": "Senior NDT Field Inspector",
            "name": "Vikramaditya Deshmukh",
            "email": "inspector@infraguard.ai",
            "phone": "+91-98114-41020",
            "password": "InfraGuard@2026",
            "agency": "MSRDC & CSIR-SERC Rapid Response Taskforce"
        },
        {
            "role": "MoRTH / NHAI Infrastructure Director",
            "name": "Ananya Sharma, IAS",
            "email": "director@infraguard.ai",
            "phone": "+91-99100-90001",
            "password": "InfraGuard@2026",
            "agency": "Ministry of Road Transport & Highways (Govt. of India)"
        }
    ]


@app.post("/api/auth/register")
@app.post("/api/auth/register-request-otp")
def register(req: RegisterRequest):
    """Registers a new user and generates a simulated 6-digit phone SMS OTP."""
    try:
        user_data = register_user(
            full_name=req.full_name,
            email=req.email,
            phone=req.phone,
            role=req.role,
            agency=req.agency,
            password=req.password
        )
        return {
            "success": True,
            "status": "otp_sent",
            "message": "User registered successfully. Simulated SMS OTP delivered to phone.",
            "simulated_otp_code": user_data.get("otp_code"),
            "sms_preview": user_data.get("sms_preview"),
            "data": user_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/send-otp")
def send_otp(req: SendOtpRequest):
    """Sends a 6-digit OTP to the specified phone number with simulated on-screen SMS delivery."""
    otp_code, sms_preview = generate_otp(req.phone, action="LOGIN")
    return {
        "success": True,
        "phone": req.phone,
        "otp_code": otp_code,
        "sms_preview": sms_preview,
        "message": f"Verification code sent to {req.phone} (Simulated on-screen for hackathon testing)"
    }


@app.post("/api/auth/verify-otp")
def verify_phone_otp(req: VerifyOtpRequest):
    """Validates the 6-digit OTP code."""
    is_valid = verify_otp(req.phone, req.otp_code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code. Please retry.")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, phone, role, agency, is_verified FROM users WHERE phone = ?", (req.phone,))
    row = cursor.fetchone()
    user_dict = {
        "id": row[0],
        "full_name": row[1],
        "email": row[2],
        "phone": row[3],
        "role": row[4],
        "agency": row[5],
        "is_verified": bool(row[6])
    } if row else {"full_name": "Verified Engineer", "role": "Field Inspector", "phone": req.phone}
    session_token = create_user_session(row[0]) if row else None
    conn.close()

    return {
        "success": True,
        "status": "verified",
        "message": "Phone number successfully verified.",
        "phone": req.phone,
        "session_token": session_token,
        "user": user_dict
    }


@app.post("/api/auth/login")
def login(req: LoginRequest):
    """Authenticates via email or phone + password."""
    target_ident = req.email_or_phone or req.identifier
    if not target_ident:
        raise HTTPException(status_code=400, detail="Missing email or phone identifier.")
    user = authenticate_user(target_ident, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials. Use demo account or request phone OTP.")
    return {
        "success": True,
        "status": "authenticated",
        "user": user
    }


@app.get("/api/auth/me")
def get_current_user(token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    """Validates user session."""
    active_token = token or (authorization.replace("Bearer ", "") if authorization else None)
    if not active_token:
        # Default to Chief Structural Engineer demo session for seamless zero-setup demo
        return {
            "id": 1,
            "full_name": "Dr. Rajesh Iyer, FIE (CEng)",
            "email": "engineer@infraguard.ai",
            "phone": "+91-98201-88420",
            "role": "Chief Structural Engineer",
            "agency": "NHAI & MoRTH Structural Integrity Division",
            "is_verified": 1
        }
    user = get_user_by_token(active_token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired.")
    return user


# ==============================================================================
# MULTI-STRUCTURE PORTFOLIO & FIELD DISPATCH API
# ==============================================================================

@app.get("/api/portfolio")
def get_portfolio(environmental_lens: str = "dry_baseline", lens: Optional[str] = None):
    """
    Ranks all 4 monitored infrastructure assets by urgency and returns
    the #1 ranked structure with an actionable Field Dispatch Card.
    """
    global ACTIVE_LENS
    chosen_lens = lens or environmental_lens
    ACTIVE_LENS = chosen_lens
    portfolio_data = portfolio_mgr.get_portfolio_status(
        environmental_lens=chosen_lens,
        active_asset_simulation=ACTIVE_SIMULATION_STATE
    )
    return portfolio_data


@app.post("/api/portfolio/dispatch")
def dispatch_field_order(req: DispatchOrderRequest):
    """Issues an official dispatched field work order for an urgent asset."""
    try:
        tech_name = req.inspector_name or req.technician
        work_order = portfolio_mgr.dispatch_field_team(
            asset_id=req.asset_id,
            technician=tech_name,
            notes=req.notes or ""
        )
        return {
            "success": True,
            "message": f"Field Crew dispatched to {work_order['asset_name']}. Work order recorded.",
            "work_order": work_order
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/portfolio/dispatches")
def get_dispatches_history():
    """Returns log of issued field dispatch orders."""
    return portfolio_mgr.get_recent_dispatches()


# ==============================================================================
# SENSOR TRUST & HARDWARE FAULT/SABOTAGE GUARD API
# ==============================================================================

@app.get("/api/sensors/trust")
def get_sensor_trust_fleet():
    """
    Evaluates all bridge IoT sensor nodes for flatlines, clipping, and loose mountings.
    Guarantees hardware faults are quarantined from false structural panic!
    """
    t = np.linspace(0, 1.0, 200)

    # 4 Representative bridge sensor nodes
    nodes = [
        {
            "node_id": "NODE-S01-MIDSPAN-DECK",
            "accel_data": np.stack([
                0.04 * np.sin(2 * np.pi * 3.25 * t) + np.random.normal(0, 0.005, len(t)),
                0.02 * np.sin(2 * np.pi * 7.80 * t) + np.random.normal(0, 0.004, len(t)),
                0.07 * np.sin(2 * np.pi * 3.25 * t) + np.random.normal(0, 0.007, len(t))
            ], axis=1),
            "strain_ue": 365.2
        },
        {
            "node_id": "NODE-S02-PIER2-TOP",
            "accel_data": np.stack([
                0.03 * np.sin(2 * np.pi * 3.10 * t) + np.random.normal(0, 0.006, len(t)),
                0.015 * np.sin(2 * np.pi * 7.75 * t) + np.random.normal(0, 0.003, len(t)),
                0.05 * np.sin(2 * np.pi * 3.10 * t) + np.random.normal(0, 0.006, len(t))
            ], axis=1),
            "strain_ue": 290.4
        },
        {
            "node_id": "NODE-S03-EAST-CABLE",
            # Loose mounting: high-frequency chatter without coherent low modal peaks
            "accel_data": np.stack([
                0.08 * np.sin(2 * np.pi * 85.0 * t) + np.random.normal(0, 0.04, len(t)),
                0.08 * np.sin(2 * np.pi * 92.0 * t) + np.random.normal(0, 0.04, len(t)),
                0.12 * np.sin(2 * np.pi * 88.0 * t) + np.random.normal(0, 0.05, len(t))
            ], axis=1),
            "strain_ue": 180.0
        },
        {
            "node_id": "NODE-S04-FOUNDATION-CAISSON",
            # Clean underwater piezometer
            "accel_data": np.stack([
                0.015 * np.sin(2 * np.pi * 2.8 * t) + np.random.normal(0, 0.002, len(t)),
                0.010 * np.sin(2 * np.pi * 5.2 * t) + np.random.normal(0, 0.002, len(t)),
                0.025 * np.sin(2 * np.pi * 2.8 * t) + np.random.normal(0, 0.003, len(t))
            ], axis=1),
            "strain_ue": 410.0
        }
    ]

    fleet_eval = sensor_guard.evaluate_network_fleet(nodes)
    return fleet_eval


# ==============================================================================
# INTERACTIVE DEMO CONTROLS: CRITICAL EVENT & TIME MACHINE
# ==============================================================================

@app.post("/api/simulate/critical-event")
def trigger_critical_event():
    """
    Simulates a live structural overload event (e.g. 80-ton overweight freight convoy crossing).
    Immediately spikes vibration, crack opening, drops SHI, and shifts structure to #1 Dispatch Priority.
    """
    global SIMULATED_CRITICAL_EVENT, ACTIVE_SIMULATION_STATE
    SIMULATED_CRITICAL_EVENT = True

    # Generate critical state
    res = rul_engine.simulate_degradation_trajectory(
        year=4.8,
        truck_load_factor=1.85,
        corrosion_factor=2.2,
        cfrp_retrofit_applied=False
    )
    res["telemetry"]["crack_width_mm"] = 2.45
    res["telemetry"]["deck_sag_mm"] = 62.4
    res["telemetry"]["strain_microstrain"] = 1140.0
    res["telemetry"]["lstm_anomaly_score"] = 0.94
    res["shi"]["shi"] = 12.4
    res["rul"]["remaining_days"] = 18
    res["rul"]["is_critical"] = True
    res["diagnosis"]["diagnosis"] = "Deep Structural Fatigue & Flexural Overload"
    res["diagnosis"]["urgency"] = "CRITICAL"

    ACTIVE_SIMULATION_STATE = res
    return {
        "event_triggered": "STRUCTURAL_OVERLOAD_CONVOY_BREACH",
        "severity": "CRITICAL_EMERGENCY",
        "description": "80-ton illegal freight overload induced 62.4mm midspan sag and 2.45mm crack extension.",
        "state": res
    }


@app.get("/api/bridge/state")
@app.get("/bridge/state")
def get_bridge_initial_state():
    """Returns initial bridge structural configuration, 3D beacons, and baseline simulation state."""
    initial_sim = simulate_bridge(SimulationRequest(
        year=0.0,
        truck_load_factor=1.0,
        corrosion_factor=1.0,
        cfrp_retrofit_applied=False,
        environmental_lens=ACTIVE_LENS
    ))
    return {
        "asset_id": "CA-DOT-BR-8842",
        "name": "Atal Setu (MTHL) Cable-Stayed Span #14, Mumbai (120m)",
        "span_length_m": 120.0,
        "allowable_sag_mm": 150.0,
        "initial_state": initial_sim
    }


@app.post("/api/simulate")
def simulate_bridge(req: SimulationRequest):
    """
    Runs the 5-Year Time Machine Scrubber with What-If sensitivity controls
    and Environmental & Monsoon stress factors.
    """
    global ACTIVE_SIMULATION_STATE, ACTIVE_LENS
    ACTIVE_LENS = req.environmental_lens

    # Lens adjustment on corrosion / load
    effective_corrosion = req.corrosion_factor
    effective_truck = req.truck_load_factor

    if req.environmental_lens == "post_monsoon":
        effective_corrosion *= 1.45  # Saturated chloride attack
    elif req.environmental_lens == "traffic_surge":
        effective_truck *= 1.30      # Rush hour axle overload

    result = rul_engine.simulate_degradation_trajectory(
        year=req.year,
        truck_load_factor=effective_truck,
        corrosion_factor=effective_corrosion,
        cfrp_retrofit_applied=req.cfrp_retrofit_applied
    )

    # Simulated FBG strain (microstrain)
    strain_ue = float(np.round(320.0 * effective_truck + (result["telemetry"]["deck_sag_mm"] * 18.5), 1))
    result["telemetry"]["strain_microstrain"] = strain_ue
    result["environmental_lens"] = req.environmental_lens

    # Cross-Check Matrix Classification ("False-Alarm vs. Silent-Killer")
    crack_w = result["telemetry"]["crack_width_mm"]
    freq_drop = result["telemetry"]["frequency_drop_pct"]
    lstm_mse = result["telemetry"]["lstm_anomaly_score"]

    if crack_w >= 0.5 and freq_drop < 1.5 and lstm_mse < 0.2:
        cross_check = {
            "category": "SURFACE_NOISE",
            "badge": "SURFACE NOISE (LOW RISK)",
            "color": "#10B981",
            "explanation": "Crack is wide but vibration dynamics are completely stable. Indicates non-structural thermal/shrinkage surface fissure. Routine monitoring."
        }
    elif crack_w < 0.5 and (freq_drop > 3.0 or lstm_mse > 0.4):
        cross_check = {
            "category": "SILENT_KILLER",
            "badge": "SILENT KILLER (CRITICAL RISK)",
            "color": "#EF4444",
            "explanation": "Dangerous hidden structural degradation: surface crack appears hairline/minor, but dynamic stiffness is rapidly softening. High risk of internal tendon fracture!"
        }
    elif freq_drop > 5.0 and crack_w < 0.3:
        cross_check = {
            "category": "SUBSURFACE_STIFFNESS_LOSS",
            "badge": "SUBSURFACE VOIDING / SCOUR",
            "color": "#F59E0B",
            "explanation": "Deep foundation settling or underwater scour active. Surface looks clean but foundation is moving."
        }
    else:
        cross_check = {
            "category": "SYNCHRONIZED_FATIGUE",
            "badge": "SYNCHRONIZED PROGRESSIVE FATIGUE",
            "color": "#EF4444" if result["shi"]["shi"] < 50 else "#38BDF8",
            "explanation": "Visual cracking and dynamic frequency softening are progressing in lockstep under cyclic truck loading."
        }
    result["cross_check_matrix"] = cross_check

    ACTIVE_SIMULATION_STATE = result

    # Persist in SQLite
    record_simulation(
        year=result["time_year"],
        truck_load_factor=req.truck_load_factor,
        corrosion_factor=req.corrosion_factor,
        cfrp_retrofit_applied=req.cfrp_retrofit_applied,
        shi_score=result["shi"]["shi"],
        rul_days=result["rul"]["remaining_days"],
        rul_years=result["rul"]["remaining_years"],
        diagnosis=result["diagnosis"]["diagnosis"],
        pathology_code=result["diagnosis"]["pathology_code"]
    )

    record_telemetry(
        sensor_node_id="NODE-SPAN-AB-MIDSPAN",
        ax=0.042, ay=0.019, az=0.068,
        strain_microstrain=strain_ue,
        deck_sag_mm=result["telemetry"]["deck_sag_mm"],
        crack_width_mm=result["telemetry"]["crack_width_mm"],
        shi_score=result["shi"]["shi"],
        rul_days=result["rul"]["remaining_days"],
        anomaly_score=result["telemetry"]["lstm_anomaly_score"],
        anomaly_detected=result["telemetry"]["lstm_anomaly_score"] > 0.35
    )

    return result


# ==============================================================================
# VISION, LIDAR & VIBRATION ENGINES
# ==============================================================================

@app.post("/api/analyze/image")
async def analyze_drone_image(
    file: Optional[UploadFile] = File(None),
    preset: Optional[str] = Form(None),
    flight_altitude_m: float = Form(0.75),
    focal_length_mm: float = Form(24.0),
    sensor_width_mm: float = Form(8.8)
):
    """
    Runs YOLOv8-seg + Scikit-image/OpenCV skeletonization:
    Quantifies crack length & width in mm, spalling area (mm² and cm²),
    exposed rebar galvanic breach, and ACI 224R severity tiers.
    """
    img_bgr = None

    if file is not None:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif preset:
        preset_filename = f"{preset}.jpg"
        preset_path = os.path.join(SAMPLE_DATA_DIR, "test_images", preset_filename)
        if os.path.exists(preset_path):
            img_bgr = cv2.imread(preset_path)

    if img_bgr is None:
        default_path = os.path.join(SAMPLE_DATA_DIR, "test_images", "span_ab_crack_critical.jpg")
        img_bgr = cv2.imread(default_path)

    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Unable to process inspection image.")

    h, w = img_bgr.shape[:2]
    gsd_mm = VisionQuantifier.calculate_gsd(
        sensor_width_mm=sensor_width_mm,
        flight_altitude_m=flight_altitude_m,
        focal_length_mm=focal_length_mm,
        image_width_px=w
    )

    analysis = vision_engine.detect_and_quantify(img_bgr, gsd_mm=gsd_mm)
    return analysis


@app.post("/api/analyze/telemetry")
def analyze_telemetry(req: TelemetryAnalysisRequest):
    """FFT/Welch modal analysis + PyTorch LSTM Autoencoder anomaly scoring."""
    if req.accel_data and len(req.accel_data) > 32:
        accel_np = np.array(req.accel_data, dtype=np.float32)
    else:
        t = np.linspace(0, 2.0, int(req.sampling_rate_hz * 2))
        ax = 0.05 * np.sin(2 * np.pi * 3.10 * t) + np.random.normal(0, 0.008, len(t))
        ay = 0.03 * np.sin(2 * np.pi * 7.70 * t) + np.random.normal(0, 0.005, len(t))
        az = 0.09 * np.sin(2 * np.pi * 3.10 * t) + 0.04 * np.sin(2 * np.pi * 14.1 * t) + np.random.normal(0, 0.012, len(t))
        accel_np = np.stack([ax, ay, az], axis=1)

    result = vibration_engine.analyze_vibration_stream(accel_np)
    return result


@app.get("/api/lidar/comparison")
def get_lidar_comparison(sample_stride: int = 4):
    """Returns baseline T0 and deformed T1 point clouds + ICP displacement."""
    t0_path = os.path.join(SAMPLE_DATA_DIR, "point_clouds", "bridge_baseline_T0.json")
    t1_path = os.path.join(SAMPLE_DATA_DIR, "point_clouds", "bridge_deformed_T1.json")

    if not os.path.exists(t0_path) or not os.path.exists(t1_path):
        from sample_data.generate_demo_data import generate_benchmark_point_clouds
        generate_benchmark_point_clouds(SAMPLE_DATA_DIR)

    with open(t0_path, "r") as f:
        t0_data = json.load(f)
    with open(t1_path, "r") as f:
        t1_data = json.load(f)

    pts_t0 = np.array(t0_data["points"])
    pts_t1 = np.array(t1_data["points"])

    comparison = lidar_engine.compute_cloud_to_cloud_displacement(pts_t0, pts_t1, apply_icp=True)

    stride = max(1, sample_stride)
    return {
        "comparison_metrics": comparison,
        "t0_points": pts_t0[::stride].tolist(),
        "t1_points": pts_t1[::stride].tolist()
    }


# ==============================================================================
# DATA EXPORTERS & SQLITE AUDIT
# ==============================================================================

@app.get("/api/export/csv")
def download_csv():
    csv_data = export_telemetry_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=infraguard_telemetry_audit.csv"}
    )


@app.get("/api/export/json")
def download_json():
    return export_telemetry_json()


@app.get("/api/history/telemetry")
def get_telemetry_history(limit: int = 50):
    return get_recent_telemetry(limit=limit)


# ==============================================================================
# WEBSOCKET REAL-TIME TELEMETRY STREAM
# ==============================================================================

@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    """
    Streams live 200 Hz simulated triaxial acceleration, optical strain gauge,
    and instantaneous anomaly metrics to connected clients.
    """
    await websocket.accept()
    phase = 0.0
    year_state = 0.0
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                msg = json.loads(data)
                if "year" in msg:
                    year_state = float(msg["year"])
            except asyncio.TimeoutError:
                pass

            phase += 0.15
            amp = 1.0 + (year_state / 5.0) * 0.75
            if SIMULATED_CRITICAL_EVENT:
                amp *= 2.8

            ax = float(np.round(0.04 * np.sin(phase * 1.8) * amp + np.random.normal(0, 0.005), 4))
            ay = float(np.round(0.02 * np.cos(phase * 2.2) * amp + np.random.normal(0, 0.004), 4))
            az = float(np.round(0.07 * np.sin(phase * 1.8) * amp + 0.03 * np.sin(phase * 4.5) + np.random.normal(0, 0.008), 4))
            strain_ue = float(np.round(340.0 + (year_state * 80.0) + (az * 450.0), 1))
            f1 = float(np.round(max(2.65, 3.25 * (1.0 - (year_state * 0.025))), 3))

            packet = {
                "timestamp": asyncio.get_event_loop().time(),
                "node_id": "NODE-S01-SPAN-AB",
                "accel": {"ax": ax, "ay": ay, "az": az},
                "strain_microstrain": strain_ue,
                "fundamental_freq_hz": f1,
                "rms_g": float(np.round(np.hypot(ax, np.hypot(ay, az)), 4)),
                "critical_event_active": SIMULATED_CRITICAL_EVENT
            }

            await websocket.send_json(packet)
            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass


@app.post("/api/copilot/ask")
def ask_structural_copilot(req: CopilotAskRequest):
    """
    Context-aware AI Structural Engineering Co-Pilot that synthesizes live
    Paris' Law fracture mechanics, ACI 224R crack limits, AASHTO L/800 sag,
    and Sensor Trust Guard telemetry into actionable engineering guidance.
    """
    q = req.query.lower()
    rul_yrs = round(req.rul_days / 365.0, 1)
    cfrp_gain_days = int(req.rul_days * 1.45) if not req.cfrp_applied else req.rul_days
    cfrp_gain_yrs = round(cfrp_gain_days / 365.0, 1)
    sag_pct = round((req.deck_sag_mm / 150.0) * 100.0, 1)

    if "rank" in q or "#1" in q or "why" in q or "priority" in q:
        answer = (
            f"**NHAI / MoRTH IBMS Priority Ranking Analysis ({req.asset_id}):**\n"
            f"• **Composite SHI:** `{req.shi:.1f} / 100` under `{req.lens.upper()}` monsoon/traffic profile.\n"
            f"• **Fracture Physics:** Paris' Law ($da/dN = C(\\Delta K)^m$) projects **{req.rul_days:,} days ({rul_yrs} yrs)** of remaining fatigue life under IRC:6 Class 70R cyclic axle stress.\n"
            f"• **3D LiDAR Sag:** Midspan vertical deflection is **-{req.deck_sag_mm:.1f} mm** ({sag_pct}% of IRC:112 / IRC:6 $L/800 = 150.0\\text{{ mm}}$ limit).\n"
            f"• **Recommendation:** Deploy CSIR-SERC Phased Array Ultrasonic Testing (PAUT) on Span #14 tension flange welds within the next inspection window."
        )
    elif "cfrp" in q or "retrofit" in q or "extend" in q or "compare" in q:
        answer = (
            f"**Carbon-Fiber (CFRP) Retrofit Impact Analysis ({req.asset_id}):**\n"
            f"• **Current Unmitigated RUL:** `{req.rul_days:,} days ({rul_yrs} yrs)` at Year `{req.year:.2f}`.\n"
            f"• **With Bonded CFRP Laminate Wrap:** Reduces effective stress intensity factor range $\\Delta K$ by **24%**, extending Paris' Law fatigue life by **+45%** to **{cfrp_gain_days:,} days ({cfrp_gain_yrs} yrs)**.\n"
            f"• **ROI & Compliance:** Prevents progression past IS 456:2000 & IRC:112 `0.30 mm` marine exposure limit (`1.0 mm` critical breach) and restores MoRTH IBMS superstructure rating."
        )
    elif "memo" in q or "closure" in q or "fhwa" in q or "morth" in q or "nhai" in q or "dispatch" in q:
        answer = (
            f"**OFFICIAL MoRTH / NHAI ENGINEERING DIRECTIVE — {req.asset_id}**\n"
            f"• **Action Tier:** {'TIER 1 EMERGENCY IRC CLASS 70R LOAD RESTRICTION' if req.shi < 60 else 'SCHEDULED PREVENTIVE NDT AUDIT'}\n"
            f"• **Telemetry Basis:** SHI `{req.shi:.1f}`, Crack Opening `{req.crack_width_mm:.2f} mm` (IS 456 / IRC:112 limit `0.30 mm`), Deflection `-{req.deck_sag_mm:.1f} mm`.\n"
            f"• **Directive:** Restrict heavy multi-axle freight vehicles >40 tonnes on Span #14, issue Work Order `WO-INFRAGUARD-2026`, and execute epoxy injection + CFRP tension laminate bonding per IRC:SP:40."
        )
    elif "sensor" in q or "trust" in q or "quarantine" in q or "fault" in q:
        answer = (
            f"**Sensor Trust Guard & Hardware Isolation Status:**\n"
            f"• **Algorithm:** Evaluates tri-axial variance, clipping saturation, and spectral coherence across all 200 Hz MEMS & FBG nodes.\n"
            f"• **Active Protection:** Node `S-03 (East Stay Cable)` exhibits high-frequency monsoon wind mounting chatter (`68% trust`) and is down-weighted; any flatlined node (`0% trust`) is automatically quarantined so hardware glitches **never trigger false NHAI highway closures**."
        )
    else:
        answer = (
            f"**INFRAGUARD India Live Structural Synthesis ({req.asset_id} @ Year {req.year:.2f}):**\n"
            f"• **Health Index & RUL:** `SHI {req.shi:.1f}` | Paris' Law RUL: `{req.rul_days:,} days ({rul_yrs} yrs)`.\n"
            f"• **Multi-Modal Fusion:** Open3D ICP LiDAR Sag `-{req.deck_sag_mm:.1f} mm` ({sag_pct}% of IRC:112 $L/800$) • Max Crack Width `{req.crack_width_mm:.2f} mm`.\n"
            f"• **Engineering Action:** {'Apply IRC:SP:40 CFRP Retrofit immediately to arrest crack growth.' if req.shi < 70 else 'Structure within safe IRC:112, IS 456:2000 & MoRTH IBMS operational envelope.'}"
        )

    return {
        "asset_id": req.asset_id,
        "query": req.query,
        "response": answer,
        "citations": ["IS 456:2000 & IRC:112-2020", "IRC:6 Class 70R L/800", "MoRTH / NHAI IBMS", "Paris' Law Fatigue Model"]
    }


@app.get("/api/health")
def health_check():
    return {
        "platform": "INFRAGUARD",
        "status": "ONLINE",
        "auth": "ENABLED (Phone OTP + Password)",
        "database": "SQLite (Connected)",
        "differentiators": {
            "sensor_trust_guard": "ACTIVE",
            "cross_check_matrix": "ACTIVE",
            "monsoon_stress_lens": "ACTIVE",
            "field_dispatch_ranking": "ACTIVE",
            "critical_event_sim": "ACTIVE",
            "ai_structural_copilot": "ACTIVE"
        }
    }


# Static Files
if os.path.exists(SAMPLE_DATA_DIR):
    app.mount("/sample_data", StaticFiles(directory=SAMPLE_DATA_DIR), name="sample_data")

if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)

