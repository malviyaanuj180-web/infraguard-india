"""
Smoke test suite for SHM modules.
"""
import sys
import os
import numpy as np

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.vision_quantifier import VisionQuantifier
from backend.lidar_fusion import LidarFusionEngine
from backend.vibration_lstm import VibrationAnalysisEngine
from backend.rul_engine import RULPhysicsEngine
from backend.sensor_trust_guard import SensorTrustGuard
from backend.portfolio_manager import PortfolioManager
from backend.auth_manager import init_auth_tables, authenticate_user, generate_and_store_otp, verify_phone_otp


def test_vision():
    print("Testing VisionQuantifier...")
    vq = VisionQuantifier(default_gsd_mm_per_px=0.25)
    
    # Create synthetic binary crack mask (line with width)
    mask = np.zeros((200, 200), dtype=np.uint8)
    mask[50:150, 100:104] = 255  # 100px long, 4px wide
    res = vq.quantify_crack_mask(mask, gsd_mm=0.25)
    assert res["length_mm"] > 20.0, f"Expected length > 20mm, got {res['length_mm']}"
    assert res["max_width_mm"] > 0.8, f"Expected max width > 0.8mm, got {res['max_width_mm']}"
    assert res["aci_tier"] in ["Moderate", "Critical"], f"Got {res['aci_tier']}"
    print(f"  [PASS] VisionQuantifier: length={res['length_mm']}mm, width={res['max_width_mm']}mm, ACI={res['aci_tier']}")


def test_lidar():
    print("Testing LidarFusionEngine...")
    engine = LidarFusionEngine()
    t0, t1, meta = engine.generate_procedural_bridge_cloud(n_points=1000, sag_magnitude_mm=35.0)
    res = engine.compute_cloud_to_cloud_displacement(t0, t1, apply_icp=True)
    assert res["icp_registration"]["converged"] is True
    assert res["deflection_summary"]["max_deck_sag_mm"] > 15.0
    print(f"  [PASS] LidarFusionEngine: Sag={res['deflection_summary']['max_deck_sag_mm']}mm, RMSE={res['icp_registration']['rmse_mm']}mm")


def test_vibration():
    print("Testing VibrationAnalysisEngine...")
    engine = VibrationAnalysisEngine(sampling_rate_hz=200.0, window_size=256)
    
    # Generate test tri-axial signal
    t = np.linspace(0, 2.0, 400)
    ax = 0.04 * np.sin(2 * np.pi * 3.2 * t) + np.random.normal(0, 0.005, len(t))
    ay = 0.02 * np.sin(2 * np.pi * 7.8 * t) + np.random.normal(0, 0.003, len(t))
    az = 0.06 * np.sin(2 * np.pi * 3.2 * t) + np.random.normal(0, 0.006, len(t))
    sig = np.stack([ax, ay, az], axis=1)
    
    res = engine.analyze_vibration_stream(sig)
    assert "modal_analysis" in res
    assert "lstm_autoencoder" in res
    assert res["modal_analysis"]["mode_1_hz"] > 0.0
    print(f"  [PASS] VibrationAnalysisEngine: Mode 1={res['modal_analysis']['mode_1_hz']}Hz, LSTM MSE={res['lstm_autoencoder']['mean_reconstruction_mse']}")


def test_rul():
    print("Testing RULPhysicsEngine...")
    engine = RULPhysicsEngine()
    
    # Year 0 test
    y0 = engine.simulate_degradation_trajectory(0.0)
    assert y0["shi"]["shi"] >= 90.0, f"Year 0 SHI should be >= 90, got {y0['shi']['shi']}"
    assert y0["rul"]["remaining_years"] > 10.0
    
    # Year 5 test
    y5 = engine.simulate_degradation_trajectory(5.0, truck_load_factor=1.4)
    assert y5["shi"]["shi"] < y0["shi"]["shi"], "Year 5 SHI should degrade"
    assert y5["rul"]["remaining_years"] < y0["rul"]["remaining_years"]
    
    # CFRP retrofit test
    y5_cfrp = engine.simulate_degradation_trajectory(5.0, truck_load_factor=1.4, cfrp_retrofit_applied=True)
    assert y5_cfrp["rul"]["remaining_days"] > y5["rul"]["remaining_days"], "CFRP should extend RUL"
    print(f"  [PASS] RULPhysicsEngine: Y0 SHI={y0['shi']['shi']}, Y5 SHI={y5['shi']['shi']}, Y5+CFRP RUL Days={y5_cfrp['rul']['remaining_days']} vs Base={y5['rul']['remaining_days']}")


def test_sensor_trust_and_portfolio():
    print("Testing SensorTrustGuard & PortfolioManager & AuthManager...")
    guard = SensorTrustGuard()
    t = np.linspace(0, 1.0, 200)
    healthy_node = {
        "node_id": "NODE-S01",
        "accel_data": np.stack([
            0.04 * np.sin(2 * np.pi * 3.2 * t) + np.random.normal(0, 0.005, len(t)),
            0.02 * np.sin(2 * np.pi * 7.8 * t) + np.random.normal(0, 0.003, len(t)),
            0.06 * np.sin(2 * np.pi * 3.2 * t) + np.random.normal(0, 0.006, len(t))
        ], axis=1),
        "strain_ue": 350.0
    }
    fleet = guard.evaluate_network_fleet([healthy_node])
    assert fleet["fleet_average_trust_pct"] >= 80.0

    pm = PortfolioManager()
    p_status = pm.get_portfolio_status(environmental_lens="post_monsoon")
    assert len(p_status["portfolio"]) == 4
    wo = pm.dispatch_field_team("CA-DOT-BR-8842", technician="Dr. Aris Thorne, PE")
    assert wo["dispatch_id"].startswith("WO-INFRAGUARD-")

    init_auth_tables()
    user = authenticate_user("engineer@infraguard.ai", "InfraGuard@2026")
    assert user is not None and user["email"] == "engineer@infraguard.ai"
    otp_res = generate_and_store_otp("+1-555-019-8842")
    assert verify_phone_otp("+1-555-019-8842", otp_res["simulated_otp_code"])["success"] is True
    print(f"  [PASS] Enterprise Modules: WorkOrder={wo['dispatch_id']}, Auth={user['email']}, OTP=Verified")


if __name__ == "__main__":
    test_vision()
    test_lidar()
    test_vibration()
    test_rul()
    test_sensor_trust_and_portfolio()
    print("\nALL INFRAGUARD PRODUCTION SMOKE TESTS PASSED PERFECTLY!")
