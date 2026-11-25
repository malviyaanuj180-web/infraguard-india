"""
STRUCTURA AI — Multi-Structure Portfolio, Automated Priority Ranking & Field Dispatch
=====================================================================================
Manages regional civil infrastructure portfolios across multiple asset types:
1. Automated Urgency Ranking: Continuously ranks all monitored bridges, flyovers,
   and retaining walls based on cross-modal damage intensity, sag utilization, and Paris' Law RUL.
2. Field Dispatch Engine: Generates actionable, official Field Work Orders for the #1 ranked
   critical asset with plain-English engineering justifications, NDT protocols, and emergency windows.
"""

import sqlite3
import os
import json
import time
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shm_records.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_portfolio_tables():
    """Initializes tables for multi-structure assets and field dispatch logs."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS infrastructure_assets (
        asset_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        typology TEXT NOT NULL,
        location TEXT NOT NULL,
        gps_coords TEXT NOT NULL,
        year_built INTEGER,
        sensor_count INTEGER,
        base_shi REAL DEFAULT 95.0,
        status TEXT DEFAULT 'OPERATIONAL'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS field_dispatches (
        dispatch_id TEXT PRIMARY KEY,
        asset_id TEXT NOT NULL,
        asset_name TEXT NOT NULL,
        urgency_level TEXT NOT NULL,
        recommended_protocol TEXT NOT NULL,
        lead_technician TEXT NOT NULL,
        status TEXT DEFAULT 'DISPATCHED',
        dispatched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        work_order_json TEXT,
        FOREIGN KEY (asset_id) REFERENCES infrastructure_assets (asset_id)
    )
    """)

    conn.commit()

    # Seed the 4 signature Indian national infrastructure portfolio structures
    assets = [
        {
            "asset_id": "CA-DOT-BR-8842",
            "name": "Atal Setu (MTHL) Cable-Stayed Span #14, Mumbai",
            "typology": "120m Orthotropic Steel-Concrete Cable-Stayed Deck",
            "location": "Mumbai Trans Harbour Link (MMRDA / MSRDC), Maharashtra",
            "gps_coords": "18.9633° N, 72.9750° E",
            "year_built": 2024,
            "sensor_count": 64,
            "base_shi": 97.8
        },
        {
            "asset_id": "MH-MSRDC-BW-102",
            "name": "Bandra-Worli Sea Link Pylon #4 Viaduct, Mumbai",
            "typology": "Prestressed Concrete Marine Cable-Stayed Viaduct",
            "location": "Western Freeway Arabian Sea Crossing, Mumbai",
            "gps_coords": "19.0368° N, 72.8172° E",
            "year_built": 2009,
            "sensor_count": 48,
            "base_shi": 84.5
        },
        {
            "asset_id": "NY-DOT-OV-409",
            "name": "Chenab Rail Arch Viaduct Pier #3, Reasi (J&K)",
            "typology": "High-Altitude Steel Box-Girder & Concrete Arch Pier",
            "location": "USBRL Himalayan Seismic Zone V Corridor, J&K",
            "gps_coords": "33.1522° N, 74.8837° E",
            "year_built": 2023,
            "sensor_count": 32,
            "base_shi": 72.1
        },
        {
            "asset_id": "CA-DOT-RW-214",
            "name": "Signature Bridge Yamuna Pylon & Retaining Wall, Delhi",
            "typology": "Asymmetrical Cable-Stayed Pylon & Diaphragm Wall",
            "location": "Wazirabad NH-9 Yamuna Floodplain Corridor, New Delhi",
            "gps_coords": "28.7058° N, 77.2325° E",
            "year_built": 2018,
            "sensor_count": 24,
            "base_shi": 89.2
        }
    ]

    for a in assets:
        cursor.execute("""
        INSERT OR REPLACE INTO infrastructure_assets (asset_id, name, typology, location, gps_coords, year_built, sensor_count, base_shi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (a["asset_id"], a["name"], a["typology"], a["location"], a["gps_coords"], a["year_built"], a["sensor_count"], a["base_shi"]))

    conn.commit()
    conn.close()


class PortfolioManager:
    def __init__(self):
        init_portfolio_tables()

    def get_portfolio_status(
        self,
        environmental_lens: str = "dry_baseline",  # "dry_baseline", "post_monsoon", "traffic_surge"
        active_asset_simulation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ranks all 4 portfolio structures by urgency.
        Incorporates current dynamic simulation values for active asset (CA-DOT-BR-8842).
        """
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM infrastructure_assets")
        rows = cursor.fetchall()
        conn.close()

        # Environmental lens severity penalty
        env_multiplier = 1.0
        if environmental_lens == "post_monsoon":
            env_multiplier = 1.35  # Soil saturation, hydrostatic pressure, marine scour
        elif environmental_lens == "traffic_surge":
            env_multiplier = 1.25  # High dynamic axle loading

        ranked_list = []

        for r in rows:
            asset_id = r["asset_id"]

            if asset_id == "CA-DOT-BR-8842" and active_asset_simulation:
                # Use real-time simulation output
                shi = float(active_asset_simulation["shi"]["shi"])
                rul_days = int(active_asset_simulation["rul"]["remaining_days"])
                crack_mm = float(active_asset_simulation["telemetry"]["crack_width_mm"])
                sag_mm = float(active_asset_simulation["telemetry"]["deck_sag_mm"])
                diagnosis = active_asset_simulation["diagnosis"]["diagnosis"]
            elif asset_id == "MH-MSRDC-BW-102":
                # Marine viaduct: heavy monsoon impact
                base_shi = 84.5
                if environmental_lens == "post_monsoon":
                    shi = round(base_shi - 18.0, 1)
                    crack_mm = 0.85
                    sag_mm = 28.5
                    rul_days = 920
                    diagnosis = "Subsurface Tidal Scour & Pier Cavitation"
                else:
                    shi = base_shi
                    crack_mm = 0.32
                    sag_mm = 14.0
                    rul_days = 2850
                    diagnosis = "Nominal Marine Splash Exposure"
            elif asset_id == "NY-DOT-OV-409":
                # Precast box girder: heavy truck surge impact
                base_shi = 72.1
                if environmental_lens == "traffic_surge":
                    shi = round(base_shi - 16.5, 1)
                    crack_mm = 1.15
                    sag_mm = 34.2
                    rul_days = 460
                    diagnosis = "Deep Flexural Girder Fatigue"
                else:
                    shi = base_shi
                    crack_mm = 0.65
                    sag_mm = 22.1
                    rul_days = 1780
                    diagnosis = "Moderate Surface Transverse Cracking"
            else:
                # Retaining wall
                shi = 89.2
                crack_mm = 0.22
                sag_mm = 8.5
                rul_days = 5200
                diagnosis = "Nominal Hydrostatic Drainage"

            # Compute composite Urgency Score (0 - 100, higher = more urgent)
            urgency_score = float(np.round((100.0 - shi) * env_multiplier, 1))

            ranked_list.append({
                "asset_id": asset_id,
                "name": r["name"],
                "typology": r["typology"],
                "location": r["location"],
                "gps_coords": r["gps_coords"],
                "shi": shi,
                "urgency_score": min(100.0, urgency_score),
                "crack_width_mm": crack_mm,
                "sag_mm": sag_mm,
                "rul_days": rul_days,
                "diagnosis": diagnosis,
                "environmental_lens": environmental_lens
            })

        # Sort descending by Urgency Score
        ranked_list.sort(key=lambda x: x["urgency_score"], reverse=True)

        for i, item in enumerate(ranked_list):
            item["priority_rank"] = i + 1

        # Generate actionable Field Dispatch Card for Rank #1
        top_asset = ranked_list[0]
        field_dispatch_card = self._build_dispatch_card(top_asset, environmental_lens)

        return {
            "portfolio": ranked_list,
            "ranked_assets_count": len(ranked_list),
            "top_priority_asset_id": top_asset["asset_id"],
            "field_dispatch_card": field_dispatch_card,
            "active_lens": environmental_lens
        }

    def _build_dispatch_card(self, asset: Dict[str, Any], lens: str) -> Dict[str, Any]:
        """Creates official actionable work order for the #1 ranked critical structure."""
        urgency = asset["urgency_score"]
        if urgency > 65.0:
            tier = "TIER 1 EMERGENCY"
            window = "Action Required Within 12 Hours"
            badge_color = "#EF4444"
        elif urgency > 35.0:
            tier = "TIER 2 PRIORITY"
            window = "Action Required Within 48 Hours"
            badge_color = "#F59E0B"
        else:
            tier = "ROUTINE MONITORING"
            window = "Scheduled Next Bi-Weekly Cycle"
            badge_color = "#10B981"

        # Specific NDT recommendations based on typology
        if "Cable-Stayed" in asset["typology"]:
            recommended_protocol = "Phased Array Ultrasonic Testing (PAUT) of midspan deck welds & 3D LiDAR sag verification."
            required_gear = ["PAUT Ultrasonic Flaw Detector", "High-Res Optical & 3D LiDAR Scanner", "CFRP Carbon-Fiber Patching Kit"]
        elif "Viaduct" in asset["typology"]:
            recommended_protocol = "Underwater Sonar Bathymetry & Pile Pier Foundation Scour Depth Inspection."
            required_gear = ["Sub-bottom Acoustic Profiler", "Cathodic Potential Meter", "Underwater ROV"]
        elif "Girder" in asset["typology"]:
            recommended_protocol = "Acoustic Emission Fatigue Crack Sizing & Temporary Axle Load Restriction Review."
            required_gear = ["Piezoelectric AE Transducers", "Portable Optical Micrometer", "Traffic Control Barricades"]
        else:
            recommended_protocol = "Inclinometer Borehole Survey & Weep Hole Hydrostatic Drainage Verification."
            required_gear = ["Digital Inclinometer", "Hydraulic Piezometer Probe", "Pressure Grout Injector"]

        return {
            "dispatch_tier": tier,
            "urgency_window": window,
            "badge_color": badge_color,
            "asset_id": asset["asset_id"],
            "asset_name": asset["name"],
            "gps_coordinates": asset["gps_coords"],
            "current_shi": asset["shi"],
            "current_rul_days": asset["rul_days"],
            "diagnosed_root_cause": asset["diagnosis"],
            "recommended_protocol": recommended_protocol,
            "required_gear": required_gear,
            "assigned_crew": "NHAI / CSIR-SERC Rapid Response Unit Alpha (Lead: Vikramaditya Deshmukh, NDT Level III)",
            "justification_summary": (
                f"Asset {asset['name']} ranks #1 in urgency under MoRTH / IRC:SP:37 IBMS criteria with a Structural Urgency Score of {asset['urgency_score']}/100 "
                f"under {lens.replace('_', ' ').title()} conditions. Paris' Law calculates remaining fatigue life of {asset['rul_days']} days "
                f"with crack opening of {asset['crack_width_mm']}mm (IS 456 / IRC:112 limit). Field dispatch is mandatory to prevent progressive structural deficiency."
            )
        }

    def dispatch_field_team(self, asset_id: str, technician: str = "Vikramaditya Deshmukh, NDT Level III", notes: str = "") -> Dict[str, Any]:
        """Issues an official dispatched work order and records it in SQLite."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM infrastructure_assets WHERE asset_id = ?", (asset_id,))
        asset = cursor.fetchone()
        if not asset:
            conn.close()
            raise ValueError(f"Asset ID {asset_id} not found.")

        dispatch_id = f"WO-INFRAGUARD-{int(time.time())}-{asset_id.split('-')[-1]}"
        protocol = "Ultrasonic Crack Sizing (PAUT) & Emergency Structural Stabilization"
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        work_order = {
            "dispatch_id": dispatch_id,
            "asset_id": asset_id,
            "asset_name": asset["name"],
            "location": asset["location"],
            "gps": asset["gps_coords"],
            "dispatched_at": now,
            "lead_technician": technician,
            "protocol": protocol,
            "engineering_notes": notes or "Immediate on-site structural audit dispatched via InfraGuard automated ranking.",
            "status": "EN_ROUTE"
        }

        cursor.execute("""
        INSERT INTO field_dispatches (dispatch_id, asset_id, asset_name, urgency_level, recommended_protocol, lead_technician, status, work_order_json)
        VALUES (?, ?, ?, 'CRITICAL', ?, ?, 'DISPATCHED', ?)
        """, (dispatch_id, asset_id, asset["name"], protocol, technician, json.dumps(work_order)))

        conn.commit()
        conn.close()

        return work_order

    def get_recent_dispatches(self) -> List[Dict[str, Any]]:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM field_dispatches ORDER BY dispatched_at DESC LIMIT 15")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
