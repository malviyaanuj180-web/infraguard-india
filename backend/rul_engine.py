"""
Cross-Modal Fusion & Physics-Informed RUL Engine
================================================
Fuses Drone Computer Vision, LiDAR 3D Spatial Deflections, and IoT Vibration Telemetry.
1. Multi-Modal Defect Classifier:
   - Cosmetic Surface Cracks vs. Deep Structural Fatigue vs. Subsurface Stiffness Loss
2. Structural Health Index (SHI, 0-100)
3. Physics-Informed Remaining Useful Life (RUL) using Paris' Law fracture mechanics:
   da/dN = C * (Delta_K)^m
   Accounting for Heavy Truck Overloading, Environmental Corrosion, and Carbon-Fiber (CFRP) Retrofit.
"""

import numpy as np
from typing import Dict, Any, Tuple, List, Optional


class RULPhysicsEngine:
    def __init__(self):
        # Paris' Law baseline material constants (Structural Rebar / Steel Tendons)
        # da/dN = C * (Delta_K)^m [a in meters, Delta_K in MPa*sqrt(m)]
        self.C_base = 1.2e-12
        self.m_exp = 3.0
        self.Y_geom = 1.12  # Geometric boundary factor for surface crack
        self.K_ic = 55.0    # Fracture toughness [MPa*sqrt(m)]
        self.baseline_cyclic_stress_mpa = 42.0  # Normal traffic cyclic stress amplitude
        self.daily_truck_cycles = 12500         # Average daily heavy truck crossings

    def classify_cross_modal_state(
        self,
        crack_width_mm: float,
        deck_sag_mm: float,
        frequency_drop_pct: float,
        lstm_anomaly_score: float
    ) -> Dict[str, Any]:
        """
        Synthesizes visual, spatial, and dynamic sensors into structural pathology diagnosis:
        - Cosmetic Surface Cracks: Surface cracking without dynamic or deflection impact
        - Deep Structural Fatigue: Cracking synchronized with measurable sag and dynamic frequency loss
        - Subsurface Stiffness Loss: Deflection sag and modal softening without prominent surface visual cues
        """
        is_surface_cracked = crack_width_mm >= 0.35
        is_deflection_abnormal = deck_sag_mm >= 25.0
        is_vibration_degraded = (frequency_drop_pct >= 3.5) or (lstm_anomaly_score >= 0.40)

        if not is_surface_cracked and not is_deflection_abnormal and not is_vibration_degraded:
            diagnosis = "Nominal Healthy State"
            pathology_code = "NOMINAL_HEALTHY"
            explanation = "All structural telemetry within AASHTO / ACI allowable baseline design tolerances."
            urgency = "LOW"
        elif is_surface_cracked and not is_deflection_abnormal and not is_vibration_degraded:
            diagnosis = "Cosmetic Surface Cracks"
            pathology_code = "COSMETIC_SURFACE"
            explanation = (
                f"Crack width ({crack_width_mm:.2f}mm) detected on concrete outer shell, but LiDAR shows "
                f"no structural sag ({deck_sag_mm:.1f}mm) and natural frequencies remain stable "
                f"(drop {frequency_drop_pct:.1f}%). Primary mechanism is shrinkage or thermal curling."
            )
            urgency = "LOW"
        elif is_deflection_abnormal and is_vibration_degraded and not is_surface_cracked:
            diagnosis = "Subsurface Stiffness Loss"
            pathology_code = "SUBSURFACE_STIFFNESS_LOSS"
            explanation = (
                f"Minimal surface cracking (<0.35mm), yet bridge exhibits {deck_sag_mm:.1f}mm mid-span sag "
                f"and {frequency_drop_pct:.1f}% natural frequency softening (LSTM Anomaly: {lstm_anomaly_score:.2f}). "
                f"Indicates hidden internal degradation: tendon de-tensioning, rebar yielding, or pier foundation settlement."
            )
            urgency = "HIGH"
        elif is_surface_cracked and (is_deflection_abnormal or is_vibration_degraded):
            diagnosis = "Deep Structural Fatigue"
            pathology_code = "DEEP_STRUCTURAL_FATIGUE"
            explanation = (
                f"Critical cross-modal convergence: High crack opening ({crack_width_mm:.2f}mm), "
                f"coupled with {deck_sag_mm:.1f}mm vertical sag and {frequency_drop_pct:.1f}% fundamental modal drift. "
                f"Active tensile load redistribution indicates progressive cyclic fatigue."
            )
            urgency = "CRITICAL"
        else:
            diagnosis = "Early Incipient Deterioration"
            pathology_code = "INCIPIENT_DETERIORATION"
            explanation = "Minor localized sensor deviations detected. Monitor rate of change."
            urgency = "MODERATE"

        return {
            "diagnosis": diagnosis,
            "pathology_code": pathology_code,
            "explanation": explanation,
            "urgency": urgency
        }

    def compute_structural_health_index(
        self,
        crack_width_mm: float,
        corrosion_pct: float,
        exposed_rebar: bool,
        deck_sag_mm: float,
        sag_utilization_pct: float,
        frequency_drop_pct: float,
        lstm_anomaly_score: float
    ) -> Dict[str, Any]:
        """
        Calculates holistic Structural Health Index (SHI, 0 - 100):
        100 = Brand-new pristine condition
        0   = Total structural compromise / imminent collapse
        """
        shi = 100.0

        # 1. Vision Penalties (Max 35 points)
        # Crack width penalty
        if crack_width_mm < 0.3:
            p_crack = crack_width_mm * 10.0  # up to 3 pts
        elif crack_width_mm <= 1.0:
            p_crack = 3.0 + (crack_width_mm - 0.3) * 17.0  # up to 15 pts
        else:
            p_crack = 15.0 + min((crack_width_mm - 1.0) * 8.0, 15.0)  # up to 30 pts

        # Corrosion penalty
        p_corr = min(corrosion_pct * 1.5, 6.0)
        # Rebar penalty
        p_rebar = 10.0 if exposed_rebar else 0.0

        vision_penalty = min(p_crack + p_corr + p_rebar, 35.0)

        # 2. LiDAR Spatial Deflection Penalty (Max 35 points)
        # Scaled by sag utilization percentage against AASHTO L/800 limit
        if sag_utilization_pct < 25.0:
            lidar_penalty = sag_utilization_pct * 0.15
        elif sag_utilization_pct < 60.0:
            lidar_penalty = 3.75 + (sag_utilization_pct - 25.0) * 0.45
        else:
            lidar_penalty = 19.5 + min((sag_utilization_pct - 60.0) * 0.5, 15.5)

        # 3. Vibration Dynamics Penalty (Max 30 points)
        p_freq = min(frequency_drop_pct * 2.2, 16.0)
        p_lstm = lstm_anomaly_score * 14.0
        vibration_penalty = min(p_freq + p_lstm, 30.0)

        # Compute composite score
        total_penalty = vision_penalty + lidar_penalty + vibration_penalty
        shi_score = float(np.round(np.clip(shi - total_penalty, 0.0, 100.0), 1))

        # Federal Highway Administration (FHWA) / NBIS Condition Rating
        if shi_score >= 88.0:
            nbis_rating = 9
            condition_label = "Excellent (NBIS 9)"
            color = "#00F0FF"  # Cyan
        elif shi_score >= 75.0:
            nbis_rating = 7
            condition_label = "Good (NBIS 7)"
            color = "#10B981"  # Emerald
        elif shi_score >= 55.0:
            nbis_rating = 5
            condition_label = "Fair / Moderate (NBIS 5)"
            color = "#F59E0B"  # Amber
        elif shi_score >= 35.0:
            nbis_rating = 4
            condition_label = "Poor / Structurally Deficient (NBIS 4)"
            color = "#EF4444"  # Crimson
        else:
            nbis_rating = 2
            condition_label = "Critical / Imminent Hazard (NBIS 2)"
            color = "#DC2626"

        return {
            "shi": shi_score,
            "nbis_rating": nbis_rating,
            "condition_label": condition_label,
            "color_hex": color,
            "penalties": {
                "vision": round(vision_penalty, 1),
                "lidar": round(lidar_penalty, 1),
                "vibration": round(vibration_penalty, 1)
            }
        }

    def predict_remaining_useful_life(
        self,
        current_crack_depth_mm: float,
        truck_load_factor: float = 1.0,        # 1.0 = 100% standard legal limit, 1.5 = 150% overload
        corrosion_factor: float = 1.0,         # 1.0 = clean, 2.0 = aggressive coastal marine/deicing salt
        cfrp_retrofit_applied: bool = False    # Carbon-Fiber Reinforced Polymer crack patch
    ) -> Dict[str, Any]:
        """
        Predicts Remaining Useful Life (RUL) in cycles and days via Paris' Law:
        da/dN = C_eff * (Delta_K)^m
        Delta_K = Y * Delta_sigma * sqrt(pi * a)
        """
        # Convert initial crack depth from mm to meters
        a_0 = max(current_crack_depth_mm / 1000.0, 0.0005)  # min 0.5mm micro-crack seed
        
        # Effective cyclic stress amplitude under truck load
        delta_sigma = self.baseline_cyclic_stress_mpa * truck_load_factor

        # Carbon-Fiber Retrofit reduces crack-tip cyclic tensile stress amplitude by 45%
        if cfrp_retrofit_applied:
            delta_sigma *= 0.55

        # Corrosion accelerates Paris constant C
        C_eff = self.C_base * (corrosion_factor ** 1.6)

        # Critical crack size a_c based on fracture toughness K_ic:
        # K_ic = Y * Delta_sigma * sqrt(pi * a_c)  ==>  a_c = (1/pi) * (K_ic / (Y * Delta_sigma))^2
        a_c = (1.0 / np.pi) * ((self.K_ic / (self.Y_geom * delta_sigma)) ** 2)
        # Cap critical depth at rebar diameter or girder web thickness (e.g. 50mm = 0.05m)
        a_c = min(a_c, 0.050)

        # If already at or past critical crack depth, RUL is exhausted
        if a_0 >= a_c:
            return {
                "remaining_cycles": 0,
                "remaining_days": 0,
                "remaining_years": 0.0,
                "critical_crack_depth_mm": round(a_c * 1000.0, 2),
                "current_crack_depth_mm": round(a_0 * 1000.0, 2),
                "delta_k_current_mpa_sqrt_m": round(self.Y_geom * delta_sigma * np.sqrt(np.pi * a_0), 2),
                "stress_intensity_ratio": 1.0,
                "is_critical": True
            }

        # Analytical integration of Paris' Law for m = 3:
        # N_rem = integral_{a_0}^{a_c} da / (C * (Y * Delta_sigma * sqrt(pi))^3 * a^(1.5))
        # integral a^(-1.5) da = -2 * a^(-0.5)
        # N_rem = [ -2 / (C * (Y * Delta_sigma * sqrt(pi))^3) ] * [ a_c^(-0.5) - a_0^(-0.5) ]
        # N_rem = [ 2 / (C * (Y * Delta_sigma * sqrt(pi))^3) ] * [ (1 / sqrt(a_0)) - (1 / sqrt(a_c)) ]
        coeff = 2.0 / (C_eff * ((self.Y_geom * delta_sigma * np.sqrt(np.pi)) ** self.m_exp))
        remaining_cycles = coeff * ((1.0 / np.sqrt(a_0)) - (1.0 / np.sqrt(a_c)))
        remaining_cycles = max(0.0, float(remaining_cycles))

        # Operational days based on daily truck crossings
        effective_daily_cycles = self.daily_truck_cycles * (1.0 + (truck_load_factor - 1.0) * 0.3)
        remaining_days = remaining_cycles / effective_daily_cycles
        remaining_years = remaining_days / 365.25

        current_delta_k = self.Y_geom * delta_sigma * np.sqrt(np.pi * a_0)
        k_ratio = min(1.0, current_delta_k / self.K_ic)

        return {
            "remaining_cycles": int(remaining_cycles),
            "remaining_days": int(np.round(remaining_days)),
            "remaining_years": float(np.round(remaining_years, 2)),
            "critical_crack_depth_mm": float(np.round(a_c * 1000.0, 2)),
            "current_crack_depth_mm": float(np.round(a_0 * 1000.0, 2)),
            "delta_k_current_mpa_sqrt_m": float(np.round(current_delta_k, 2)),
            "stress_intensity_ratio": float(np.round(k_ratio, 3)),
            "is_critical": bool(remaining_days < 90),
            "parameters": {
                "truck_load_factor": float(truck_load_factor),
                "corrosion_factor": float(corrosion_factor),
                "cfrp_applied": bool(cfrp_retrofit_applied),
                "effective_delta_sigma_mpa": float(round(delta_sigma, 1))
            }
        }

    def simulate_degradation_trajectory(
        self,
        year: float,                            # 0.0 to 5.0
        truck_load_factor: float = 1.0,
        corrosion_factor: float = 1.0,
        cfrp_retrofit_applied: bool = False
    ) -> Dict[str, Any]:
        """
        Generates continuous bridge degradation physics state for the 5-Year Time Machine Scrubber:
        Year 0: Pristine baseline
        Year 1-2: Hairline fatigue nucleation, sub-millimeter sag
        Year 3: Moderate cracking (0.45mm), 18mm sag, 2.5% frequency drop
        Year 4: Deep fatigue initiation (0.95mm), 38mm sag, 5.8% frequency drop
        Year 5: Critical breach (1.85mm crack, 54mm sag, 9.4% frequency drop, rebar exposure risk)
        """
        t = float(np.clip(year, 0.0, 5.0))
        
        # Environmental and load acceleration multipliers
        accel = float((truck_load_factor ** 1.35) * (corrosion_factor ** 0.8))
        if cfrp_retrofit_applied:
            accel *= 0.45  # 55% retardation from composite wrap

        # Crack evolution: Exponential nucleation & propagation
        # a(t) = a_0 * exp(alpha * t * accel)
        crack_width_mm = float(0.08 * np.exp(0.62 * t * accel))
        # Depth is roughly proportional to surface width in concrete flexural zones
        crack_depth_mm = float(crack_width_mm * 12.0)

        # LiDAR Midspan Deflection (sag increases with concrete creep & cracking)
        # Sag(t) = baseline_elastic + creep_sag * t^1.2
        deck_sag_mm = float(6.0 + 9.5 * (t ** 1.25) * accel)
        sag_utilization_pct = float((deck_sag_mm / 150.0) * 100.0)

        # Natural Frequency Drift: f_n drops as stiffness EI degrades
        # Frequency drop % roughly proportional to sag & cracking
        frequency_drop_pct = float(min(15.0, 1.8 * (t ** 1.15) * accel))
        fundamental_freq_hz = float(max(2.65, 3.25 * (1.0 - frequency_drop_pct / 100.0)))

        # LSTM Autoencoder Anomaly Score: climbs from 0.05 to ~0.92
        lstm_anomaly_score = float(np.clip(0.05 + 0.17 * (t ** 1.1) * accel, 0.0, 1.0))

        # Corrosion surface spread
        corrosion_pct = float(np.clip(0.1 + 0.9 * (t ** 1.3) * corrosion_factor, 0.0, 25.0))
        exposed_rebar = bool((t >= 3.8 and crack_width_mm > 1.2) or (t >= 4.5 and corrosion_factor > 1.3))

        # Cross-modal diagnosis
        diagnosis = self.classify_cross_modal_state(
            crack_width_mm=crack_width_mm,
            deck_sag_mm=deck_sag_mm,
            frequency_drop_pct=frequency_drop_pct,
            lstm_anomaly_score=lstm_anomaly_score
        )

        # Structural Health Index
        shi_data = self.compute_structural_health_index(
            crack_width_mm=crack_width_mm,
            corrosion_pct=corrosion_pct,
            exposed_rebar=exposed_rebar,
            deck_sag_mm=deck_sag_mm,
            sag_utilization_pct=sag_utilization_pct,
            frequency_drop_pct=frequency_drop_pct,
            lstm_anomaly_score=lstm_anomaly_score
        )

        # Remaining Useful Life
        rul_data = self.predict_remaining_useful_life(
            current_crack_depth_mm=crack_depth_mm,
            truck_load_factor=truck_load_factor,
            corrosion_factor=corrosion_factor,
            cfrp_retrofit_applied=cfrp_retrofit_applied
        )

        # Engineering Alerts Generation
        alerts = self._generate_engineering_alerts(
            year=t,
            crack_width_mm=crack_width_mm,
            deck_sag_mm=deck_sag_mm,
            frequency_drop_pct=frequency_drop_pct,
            rul_days=rul_data["remaining_days"],
            exposed_rebar=exposed_rebar,
            shi=shi_data["shi"]
        )

        return {
            "time_year": round(t, 2),
            "telemetry": {
                "crack_width_mm": round(crack_width_mm, 2),
                "crack_depth_mm": round(crack_depth_mm, 2),
                "deck_sag_mm": round(deck_sag_mm, 2),
                "allowable_sag_limit_mm": 150.0,
                "sag_utilization_pct": round(sag_utilization_pct, 1),
                "fundamental_freq_hz": round(fundamental_freq_hz, 3),
                "baseline_freq_hz": 3.250,
                "frequency_drop_pct": round(frequency_drop_pct, 2),
                "lstm_anomaly_score": round(lstm_anomaly_score, 3),
                "corrosion_pct": round(corrosion_pct, 2),
                "exposed_rebar": exposed_rebar
            },
            "diagnosis": diagnosis,
            "shi": shi_data,
            "rul": rul_data,
            "alerts": alerts
        }

    @staticmethod
    def _generate_engineering_alerts(
        year: float,
        crack_width_mm: float,
        deck_sag_mm: float,
        frequency_drop_pct: float,
        rul_days: int,
        exposed_rebar: bool,
        shi: float
    ) -> List[Dict[str, Any]]:
        alerts = []
        
        if crack_width_mm > 1.0:
            alerts.append({
                "severity": "CRITICAL",
                "code": "ACI-224R-CRACK-EXCEEDED",
                "title": "Crack Width Exceeds ACI 224R Structural Threshold",
                "timestamp": f"Year {year:.1f}",
                "message": f"Surface crack opening at Span A-B Deck measured at {crack_width_mm:.2f}mm, violating maximum allowable 1.0mm flexural limit.",
                "action": "Dispatch emergency structural inspection team; install fiber-optic strain gauges."
            })
        elif crack_width_mm > 0.3:
            alerts.append({
                "severity": "WARNING",
                "code": "ACI-224R-CRACK-MODERATE",
                "title": "Moderate Crack Growth Detected",
                "timestamp": f"Year {year:.1f}",
                "message": f"Crack opening at {crack_width_mm:.2f}mm. Accelerated chloride ingress risk into reinforcement zone.",
                "action": "Schedule epoxy pressure injection and hydrophobic sealing within 60 days."
            })

        if deck_sag_mm > 40.0:
            alerts.append({
                "severity": "CRITICAL",
                "code": "AASHTO-SAG-WARNING",
                "title": "AASHTO Deflection Limit Alert",
                "timestamp": f"Year {year:.1f}",
                "message": f"Mid-span vertical displacement reaches {deck_sag_mm:.1f}mm (>25% allowable design limit).",
                "action": "Enact axle weight restrictions and review stay cable tension calibration."
            })

        if frequency_drop_pct > 5.0:
            alerts.append({
                "severity": "WARNING",
                "code": "SHM-MODAL-DRIFT",
                "title": "Significant Natural Frequency Shift",
                "timestamp": f"Year {year:.1f}",
                "message": f"Fundamental bending frequency dropped by {frequency_drop_pct:.1f}%, indicating localized bending stiffness (EI) loss.",
                "action": "Cross-reference with Pier #2 tilt and acoustic emission telemetry."
            })

        if exposed_rebar:
            alerts.append({
                "severity": "CRITICAL",
                "code": "FHWA-REBAR-EXPOSURE",
                "title": "Exposed Reinforcing Steel Spalling",
                "timestamp": f"Year {year:.1f}",
                "message": "Concrete cover spalled to level of longitudinal reinforcement. High galvanic corrosion rate active.",
                "action": "Immediate sandblasting, sacrificial zinc anode installation, and micro-concrete patch repair."
            })

        if rul_days < 180 and rul_days > 0:
            alerts.append({
                "severity": "CRITICAL",
                "code": "RUL-FATIGUE-LIMIT",
                "title": "Remaining Useful Life Warning (< 6 Months)",
                "timestamp": f"Year {year:.1f}",
                "message": f"Paris' Law fracture model estimates {rul_days} operational days before crack tip stress intensity reaches critical fracture toughness K_Ic.",
                "action": "Apply Carbon-Fiber Reinforced Polymer (CFRP) composite retrofit or schedule lane closure."
            })

        if not alerts:
            alerts.append({
                "severity": "NOMINAL",
                "code": "STATUS-OPTIMAL",
                "title": "Structural Integrity Within Normal Parameters",
                "timestamp": f"Year {year:.1f}",
                "message": "All vibration, deflection, and crack telemetry within nominal baseline bounds.",
                "action": "Continue automated 24/7 continuous autonomous monitoring."
            })

        return alerts
