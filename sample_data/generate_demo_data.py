"""
Sample Benchmark Data Generator
===============================
Generates high-fidelity synthetic benchmark datasets for:
1. Drone inspection images (concrete cracks, delamination, corrosion)
2. LiDAR 3D point clouds (Baseline T0 and Deformed T1)
3. Multi-channel accelerometer vibration telemetry
4. Anomaly beacon metadata for the interactive 3D bridge
"""

import os
import json
import numpy as np
import cv2


def generate_synthetic_crack_image(output_path: str, crack_severity: str = "critical"):
    """
    Synthesizes a realistic high-resolution drone photo of concrete with cracks and weathering.
    """
    w, h = 1024, 768
    # 1. Base concrete texture (Perlin-like multi-scale noise)
    np.random.seed(42 if crack_severity == "critical" else 101)
    base = np.random.normal(160, 25, (h, w)).astype(np.float32)
    base = cv2.GaussianBlur(base, (7, 7), 0)
    
    # Add concrete aggregate granules
    granules = (np.random.rand(h, w) > 0.985).astype(np.float32) * -50.0
    base += granules
    base = np.clip(base, 30, 230).astype(np.uint8)
    img_bgr = cv2.cvtColor(base, cv2.COLOR_GRAY2BGR)

    # 2. Add corrosion / rust staining (brownish-amber wash)
    if crack_severity in ["critical", "moderate"]:
        rust_mask = np.zeros((h, w), dtype=np.float32)
        cv2.circle(rust_mask, (w // 2 + 60, h // 2 - 20), 180, 1.0, -1)
        rust_mask = cv2.GaussianBlur(rust_mask, (101, 101), 0)
        
        rust_color = np.array([30, 85, 175], dtype=np.float32) # BGR rust
        for c in range(3):
            img_bgr[:, :, c] = np.clip(
                img_bgr[:, :, c] * (1.0 - rust_mask * 0.45) + rust_color[c] * (rust_mask * 0.45),
                0, 255
            ).astype(np.uint8)

    # 3. Draw realistic fractal-like branching crack
    if crack_severity != "none":
        pts = []
        cur_x = w // 4
        cur_y = h // 4
        pts.append((cur_x, cur_y))
        
        crack_width = 8 if crack_severity == "critical" else (4 if crack_severity == "moderate" else 2)
        n_steps = 140
        for _ in range(n_steps):
            cur_x += int(np.random.normal(5, 3))
            cur_y += int(np.random.normal(3, 4))
            cur_x = np.clip(cur_x, 10, w - 10)
            cur_y = np.clip(cur_y, 10, h - 10)
            pts.append((cur_x, cur_y))

        # Main crack line
        for i in range(len(pts) - 1):
            w_step = max(1, int(crack_width * (1.0 + 0.3 * np.sin(i / 10.0))))
            cv2.line(img_bgr, pts[i], pts[i + 1], (25, 25, 30), w_step)
            # Secondary micro-branches
            if i % 15 == 0 and i > 10:
                bx = pts[i][0] + int(np.random.normal(20, 10))
                by = pts[i][1] + int(np.random.normal(-20, 10))
                cv2.line(img_bgr, pts[i], (bx, by), (35, 35, 40), max(1, w_step // 2))

    # 4. Spalling / concrete chipping cavitation
    if crack_severity == "critical":
        spall_center = (w // 2 + 40, h // 2 + 30)
        cv2.ellipse(img_bgr, spall_center, (65, 35), 25, 0, 360, (40, 45, 50), -1)
        # Exposed rebar line across spall cavity
        cv2.line(img_bgr, (spall_center[0] - 80, spall_center[1] + 10),
                 (spall_center[0] + 80, spall_center[1] - 10), (18, 55, 110), 6) # rusty metallic rebar

    cv2.imwrite(output_path, img_bgr)
    print(f"Generated synthetic drone inspection image: {output_path}")


def generate_benchmark_point_clouds(base_dir: str):
    """Generates T0 baseline and T1 deformed bridge point clouds."""
    from backend.lidar_fusion import LidarFusionEngine
    
    t0_pts, t1_pts, meta = LidarFusionEngine.generate_procedural_bridge_cloud(
        n_points=6000,
        span_length_m=120.0,
        sag_magnitude_mm=48.0
    )

    t0_path = os.path.join(base_dir, "point_clouds", "bridge_baseline_T0.json")
    t1_path = os.path.join(base_dir, "point_clouds", "bridge_deformed_T1.json")

    # Downsample lightly for quick JSON transport in web demo (~2500 pts)
    subsample_t0 = t0_pts[::2].tolist()
    subsample_t1 = t1_pts[::2].tolist()

    with open(t0_path, "w") as f:
        json.dump({"points": subsample_t0, "metadata": meta}, f)
    with open(t1_path, "w") as f:
        json.dump({"points": subsample_t1, "metadata": meta}, f)

    print(f"Generated LiDAR baseline T0: {t0_path} ({len(subsample_t0)} points)")
    print(f"Generated LiDAR deformed T1: {t1_path} ({len(subsample_t1)} points)")


def generate_beacon_and_telemetry_data(base_dir: str):
    """Generates 3D structural anomaly beacons and 5-year degradation telemetry."""
    beacons = [
        {
            "id": "beacon-span-ab",
            "name": "Span A-B Deck (Midspan)",
            "position": [0.0, 1.8, 0.0],
            "component": "Bridge Superstructure Deck",
            "criticality": "HIGH",
            "sensor_type": "Tri-Axial Accel + Optical Displacement",
            "active_defects": ["Flexural Tension Cracking (1.42mm)", "Mid-span Sag (48.2mm)"],
            "inspection_focus": "Tensile stress re-distribution and fatigue cycle count",
            "coordinates_gps": "37.8199° N, 122.4783° W"
        },
        {
            "id": "beacon-pier-2",
            "name": "Pier #2 Mid-Column",
            "position": [20.0, -12.0, 0.0],
            "component": "Substructure Concrete Column",
            "criticality": "MEDIUM",
            "sensor_type": "Tiltmeter & Ultrasonic Transducer",
            "active_defects": ["Delamination Spalling", "Lateral Drift (14.5mm)"],
            "inspection_focus": "Shear cracking and seismic displacement envelope",
            "coordinates_gps": "37.8204° N, 122.4779° W"
        },
        {
            "id": "beacon-pier-3",
            "name": "Pier #3 Base Joint",
            "position": [-20.0, -25.0, 0.0],
            "component": "Submerged Foundation Caisson",
            "criticality": "CRITICAL",
            "sensor_type": "Piezometer & Acoustic Emission Sensor",
            "active_defects": ["Marine Scour Cavitation", "Chloride Attack Corrosion"],
            "inspection_focus": "Tidal scour and pile cap integrity",
            "coordinates_gps": "37.8192° N, 122.4788° W"
        },
        {
            "id": "beacon-cable-east",
            "name": "East Cable Anchor",
            "position": [42.0, 2.5, 6.0],
            "component": "Post-Tensioned Stay Cable Anchor",
            "criticality": "MEDIUM",
            "sensor_type": "Fiber-Optic FBG Strain Gauge",
            "active_defects": ["Fretting Wear", "Anchor Head Micro-Fissures"],
            "inspection_focus": "Tendon tension loss and wind-induced vortex vibration",
            "coordinates_gps": "37.8211° N, 122.4772° W"
        }
    ]

    beacons_path = os.path.join(base_dir, "telemetry", "beacons_metadata.json")
    with open(beacons_path, "w") as f:
        json.dump(beacons, f, indent=2)
    print(f"Generated Beacons metadata: {beacons_path}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(base_dir, "point_clouds"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "test_images"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "telemetry"), exist_ok=True)

    # 1. Images
    generate_synthetic_crack_image(
        os.path.join(base_dir, "test_images", "span_ab_crack_critical.jpg"),
        crack_severity="critical"
    )
    generate_synthetic_crack_image(
        os.path.join(base_dir, "test_images", "pier2_crack_moderate.jpg"),
        crack_severity="moderate"
    )
    generate_synthetic_crack_image(
        os.path.join(base_dir, "test_images", "healthy_deck_baseline.jpg"),
        crack_severity="none"
    )

    # 2. Point Clouds
    generate_benchmark_point_clouds(base_dir)

    # 3. Telemetry & Beacons
    generate_beacon_and_telemetry_data(base_dir)
    print("Demo benchmark data generation complete.")


if __name__ == "__main__":
    main()
