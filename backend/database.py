"""
InfraSentinel - SQLite Database Layer
======================================
Provides persistent storage, querying, and CSV/JSON export for:
- IoT Vibration & Strain Telemetry
- LiDAR & Vision Defect Metrics
- 5-Year Simulation History
- Explainable Engineering (XAI) Compliance Alerts
"""

import sqlite3
import os
import csv
import json
import io
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shm_records.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initializes SQLite tables for telemetry, simulations, and alerts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Telemetry Log Table (Vibration, FBG Strain, Sag, Cracks, SHI)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        sensor_node_id TEXT,
        ax REAL,
        ay REAL,
        az REAL,
        strain_microstrain REAL,
        deck_sag_mm REAL,
        crack_width_mm REAL,
        shi_score REAL,
        rul_days INTEGER,
        anomaly_score REAL,
        anomaly_detected INTEGER
    )
    """)

    # 2. Simulation Scenarios History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulation_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        simulation_year REAL,
        truck_load_factor REAL,
        corrosion_factor REAL,
        cfrp_retrofit_applied INTEGER,
        shi_score REAL,
        rul_days INTEGER,
        rul_years REAL,
        diagnosis TEXT,
        pathology_code TEXT
    )
    """)

    # 3. Engineering Compliance Alerts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS engineering_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        severity TEXT,
        code TEXT,
        title TEXT,
        message TEXT,
        remediation_action TEXT
    )
    """)

    conn.commit()

    # Seed initial telemetry baseline if empty
    cursor.execute("SELECT COUNT(*) as count FROM telemetry_logs")
    if cursor.fetchone()["count"] == 0:
        _seed_initial_telemetry(cursor)
        conn.commit()

    conn.close()


def _seed_initial_telemetry(cursor):
    """Populates benchmark baseline telemetry points."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(25):
        t_offset = i * 60
        cursor.execute("""
        INSERT INTO telemetry_logs (
            timestamp, sensor_node_id, ax, ay, az,
            strain_microstrain, deck_sag_mm, crack_width_mm,
            shi_score, rul_days, anomaly_score, anomaly_detected
        ) VALUES (
            datetime('now', ?), 'NODE-SPAN-AB-01', 0.042, 0.018, 0.065,
            345.2, 6.2, 0.08, 97.8, 6396, 0.045, 0
        )
        """, (f"-{t_offset} seconds",))


def record_telemetry(
    sensor_node_id: str,
    ax: float,
    ay: float,
    az: float,
    strain_microstrain: float,
    deck_sag_mm: float,
    crack_width_mm: float,
    shi_score: float,
    rul_days: int,
    anomaly_score: float,
    anomaly_detected: bool
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO telemetry_logs (
        sensor_node_id, ax, ay, az, strain_microstrain,
        deck_sag_mm, crack_width_mm, shi_score, rul_days,
        anomaly_score, anomaly_detected
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sensor_node_id, ax, ay, az, strain_microstrain,
        deck_sag_mm, crack_width_mm, shi_score, rul_days,
        anomaly_score, 1 if anomaly_detected else 0
    ))
    conn.commit()
    conn.close()


def record_simulation(
    year: float,
    truck_load_factor: float,
    corrosion_factor: float,
    cfrp_retrofit_applied: bool,
    shi_score: float,
    rul_days: int,
    rul_years: float,
    diagnosis: str,
    pathology_code: str
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO simulation_runs (
        simulation_year, truck_load_factor, corrosion_factor,
        cfrp_retrofit_applied, shi_score, rul_days, rul_years,
        diagnosis, pathology_code
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        year, truck_load_factor, corrosion_factor,
        1 if cfrp_retrofit_applied else 0, shi_score, rul_days,
        rul_years, diagnosis, pathology_code
    ))
    conn.commit()
    conn.close()


def get_recent_telemetry(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM telemetry_logs
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_telemetry_csv() -> str:
    """Exports all telemetry logs as RFC-4180 CSV string."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM telemetry_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    if len(rows) > 0:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    else:
        output.write("id,timestamp,sensor_node_id,ax,ay,az,strain_microstrain,deck_sag_mm,crack_width_mm,shi_score,rul_days,anomaly_score,anomaly_detected\n")

    return output.getvalue()


def export_telemetry_json() -> List[Dict[str, Any]]:
    """Exports all telemetry logs as JSON serializable list."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM telemetry_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
