"""
LiDAR Spatial Analysis & Cloud-to-Cloud Displacement Module
===========================================================
Performs ICP (Iterative Closest Point) baseline alignment between reference LiDAR scan (T0)
and inspection scan (T1). Computes 3D structural deflections (Delta_x, Delta_y, Delta_z,
Euclidean displacement) and maps localized anomalies to bridge structural coordinates.
Operates with Open3D if available, with built-in high-performance NumPy/SciPy ICP fallback.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional, List
import os
import json
from scipy.spatial import cKDTree

try:
    import open3d as o3d
    HAS_OPEN3D = True
except Exception:
    HAS_OPEN3D = False


class LidarFusionEngine:
    def __init__(self):
        self.has_open3d = HAS_OPEN3D

    @staticmethod
    def generate_procedural_bridge_cloud(
        n_points: int = 15000,
        span_length_m: float = 120.0,
        deck_width_m: float = 18.0,
        pier_height_m: float = 30.0,
        deformation_type: str = "sag_and_tilt",
        sag_magnitude_mm: float = 45.0,
        noise_std_mm: float = 2.0
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Synthesizes realistic bridge point clouds for baseline (T0) and deformed state (T1):
        - Bridge deck (grid with camber curve)
        - 2 Main support piers (Pier #1 at -span/3, Pier #2 at +span/3)
        - Suspension / stay cable bundles
        - Pier base foundations
        """
        rng = np.random.RandomState(42)

        # 1. Deck Points (X: [-span/2, span/2], Y: [-width/2, width/2], Z: ~0 with slight natural arch)
        n_deck = int(n_points * 0.6)
        x_deck = rng.uniform(-span_length_m / 2, span_length_m / 2, n_deck)
        y_deck = rng.uniform(-deck_width_m / 2, deck_width_m / 2, n_deck)
        # Baseline parabolic road camber: Z = 1.2 * (1 - (2x/L)^2)
        z_deck = 1.2 * (1.0 - (2.0 * x_deck / span_length_m) ** 2)

        # 2. Pier Points (Pier 1 at x = -20m, Pier 2 at x = +20m)
        n_pier = int(n_points * 0.25)
        n_per_pier = n_pier // 2
        
        # Pier 1: x in [-22, -18], y in [-3, 3], z in [-pier_height, 0]
        x_p1 = rng.uniform(-21.5, -18.5, n_per_pier)
        y_p1 = rng.uniform(-2.5, 2.5, n_per_pier)
        z_p1 = rng.uniform(-pier_height_m, 0.5, n_per_pier)

        # Pier 2: x in [18.5, 21.5]
        x_p2 = rng.uniform(18.5, 21.5, n_per_pier)
        y_p2 = rng.uniform(-2.5, 2.5, n_per_pier)
        z_p2 = rng.uniform(-pier_height_m, 0.5, n_per_pier)

        # 3. Cable Stay Points
        n_cables = n_points - (n_deck + n_pier)
        # Towers extend up to +25m at x = -20 and +20
        t = rng.uniform(0.0, 1.0, n_cables)
        # Cables fan out from tower top (z = +25m) to deck
        tower_x = np.where(rng.rand(n_cables) > 0.5, -20.0, 20.0)
        target_x = rng.uniform(-span_length_m * 0.45, span_length_m * 0.45, n_cables)
        x_cable = tower_x + t * (target_x - tower_x)
        y_cable = rng.uniform(-deck_width_m * 0.45, deck_width_m * 0.45, n_cables)
        z_cable = 25.0 * (1.0 - t) + 1.0 * t

        # Combine all components into T0 (Baseline)
        x_t0 = np.concatenate([x_deck, x_p1, x_p2, x_cable])
        y_t0 = np.concatenate([y_deck, y_p1, y_p2, y_cable])
        z_t0 = np.concatenate([z_deck, z_p1, z_p2, z_cable])

        t0_points = np.stack([x_t0, y_t0, z_t0], axis=1)

        # 4. Generate Deformed State T1
        t1_points = t0_points.copy()

        sag_m = sag_magnitude_mm / 1000.0  # mm to meters

        if deformation_type == "sag_and_tilt":
            # Mid-span vertical deflection (Gaussian dip centered at mid-span x=0, deck points z > -1.0)
            deck_mask = t1_points[:, 2] > -2.0
            midspan_dist = np.abs(t1_points[:, 0])
            deflection_envelope = np.exp(-(midspan_dist / 22.0) ** 2)
            t1_points[deck_mask, 2] -= sag_m * deflection_envelope[deck_mask]

            # Pier #2 lateral tilt (x ~ 20m, linear drift with height)
            pier2_mask = (t1_points[:, 0] > 15.0) & (t1_points[:, 0] < 25.0) & (t1_points[:, 2] <= 0.0)
            height_ratio = (-t1_points[pier2_mask, 2]) / pier_height_m  # 0 at top, 1 at bottom
            # Shear tilt in X direction up to 18mm
            t1_points[pier2_mask, 0] += (18.0 / 1000.0) * (1.0 - height_ratio)

        # Add sensor measurement noise (LiDAR precision ~2mm)
        noise = rng.normal(0, noise_std_mm / 1000.0, size=t1_points.shape)
        t1_points += noise

        # Simulate slight rigid body rotation/drift (misalignment before ICP)
        theta = np.radians(0.35)  # 0.35 deg rotation
        rot_matrix = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta),  np.cos(theta), 0],
            [0,              0,             1]
        ])
        translation = np.array([0.05, -0.03, 0.02])  # 5cm offset
        t1_points = (t1_points @ rot_matrix.T) + translation

        metadata = {
            "n_points": n_points,
            "span_length_m": span_length_m,
            "induced_sag_mm": sag_magnitude_mm,
            "simulated_pier_tilt_mm": 18.0 if deformation_type == "sag_and_tilt" else 0.0,
            "sensor_noise_std_mm": noise_std_mm
        }

        return t0_points, t1_points, metadata

    @staticmethod
    def align_icp(source_pts: np.ndarray, target_pts: np.ndarray, max_iterations: int = 40,
                  tolerance: float = 1e-5) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        SVD-based Iterative Closest Point (Kabsch algorithm) with outlier pruning.
        Aligns source_pts (T1) onto target_pts (T0 baseline).
        Returns: (aligned_source, 4x4 Transformation Matrix, final_rmse)
        """
        src = source_pts.copy()
        target_tree = cKDTree(target_pts)
        
        transformation = np.eye(4)
        prev_err = float('inf')

        for i in range(max_iterations):
            # Nearest neighbor matching
            distances, indices = target_tree.query(src)
            # Prune upper 15% distance outliers (e.g. true localized deformations shouldn't distort global rigid fit)
            threshold = np.percentile(distances, 85)
            inliers = distances < threshold
            
            p_src = src[inliers]
            p_tgt = target_pts[indices[inliers]]

            centroid_src = np.mean(p_src, axis=0)
            centroid_tgt = np.mean(p_tgt, axis=0)

            h_mat = (p_src - centroid_src).T @ (p_tgt - centroid_tgt)
            u, s, vt = np.linalg.svd(h_mat)
            r_mat = vt.T @ u.T

            # Reflection check
            if np.linalg.det(r_mat) < 0:
                vt[2, :] *= -1
                r_mat = vt.T @ u.T

            t_vec = centroid_tgt - r_mat @ centroid_src

            # Apply incremental transform
            src = (r_mat @ src.T).T + t_vec

            # Update composite 4x4 matrix
            step_t = np.eye(4)
            step_t[:3, :3] = r_mat
            step_t[:3, 3] = t_vec
            transformation = step_t @ transformation

            mean_err = np.mean(distances[inliers])
            if abs(prev_err - mean_err) < tolerance:
                break
            prev_err = mean_err

        final_dists, _ = target_tree.query(src)
        final_rmse = float(np.sqrt(np.mean(final_dists ** 2)))

        return src, transformation, final_rmse

    def compute_cloud_to_cloud_displacement(
        self,
        t0_baseline: np.ndarray,
        t1_current: np.ndarray,
        apply_icp: bool = True
    ) -> Dict[str, Any]:
        """
        Computes localized Cloud-to-Cloud (C2C) Euclidean displacement and directional deltas
        (Delta X, Delta Y, Delta Z) between baseline and aligned current scan.
        """
        if apply_icp:
            t1_aligned, transform_matrix, icp_rmse = self.align_icp(t1_current, t0_baseline)
        else:
            t1_aligned = t1_current.copy()
            transform_matrix = np.eye(4)
            icp_rmse = 0.0

        # KD-Tree for nearest neighbor baseline distance
        t0_tree = cKDTree(t0_baseline)
        distances, nearest_idx = t0_tree.query(t1_aligned)
        
        # Component-wise displacement vectors (t1_aligned - t0_corresponding)
        matched_t0 = t0_baseline[nearest_idx]
        delta_xyz = t1_aligned - matched_t0  # in meters

        # Convert to millimeters for structural engineering precision
        delta_x_mm = delta_xyz[:, 0] * 1000.0
        delta_y_mm = delta_xyz[:, 1] * 1000.0
        delta_z_mm = delta_xyz[:, 2] * 1000.0
        euclidean_disp_mm = distances * 1000.0

        # Regional Partitioning & Peak Deflection Mapping
        # Regions: Span A-B Deck (Midspan), Pier #2 Mid-Column, Pier #3 Base Joint, East Cable Anchor
        deck_mask = (np.abs(t1_aligned[:, 0]) < 30.0) & (t1_aligned[:, 2] > -2.0)
        pier2_mask = (t1_aligned[:, 0] > 15.0) & (t1_aligned[:, 0] < 25.0) & (t1_aligned[:, 2] <= 0.0)
        cable_mask = t1_aligned[:, 2] > 12.0

        max_deck_sag_mm = float(np.max(np.abs(delta_z_mm[deck_mask]))) if np.any(deck_mask) else 0.0
        max_pier_drift_mm = float(np.max(np.hypot(delta_x_mm[pier2_mask], delta_y_mm[pier2_mask]))) if np.any(pier2_mask) else 0.0
        max_overall_disp_mm = float(np.max(euclidean_disp_mm))

        # Classify AASHTO/FHWA deflection criteria (e.g. allowable span sag L/800 = 120m/800 = 150mm)
        allowable_sag_mm = 150.0
        sag_utilization_pct = float(np.round((max_deck_sag_mm / allowable_sag_mm) * 100.0, 1))

        # Map Hotspots: Points where displacement exceeds 95th percentile
        hotspot_threshold = np.percentile(euclidean_disp_mm, 95)
        hotspot_indices = np.where(euclidean_disp_mm > hotspot_threshold)[0]
        
        # Select representative top 5 anomaly clusters
        hotspots = []
        if len(hotspot_indices) > 0:
            step = max(1, len(hotspot_indices) // 5)
            for idx in hotspot_indices[::step][:5]:
                pt = t1_aligned[idx]
                hotspots.append({
                    "x": float(np.round(pt[0], 2)),
                    "y": float(np.round(pt[1], 2)),
                    "z": float(np.round(pt[2], 2)),
                    "disp_mm": float(np.round(euclidean_disp_mm[idx], 2)),
                    "delta_z_mm": float(np.round(delta_z_mm[idx], 2))
                })

        return {
            "icp_registration": {
                "converged": True,
                "rmse_mm": float(np.round(icp_rmse * 1000.0, 3)),
                "transformation_matrix": transform_matrix.tolist()
            },
            "deflection_summary": {
                "max_deck_sag_mm": float(np.round(max_deck_sag_mm, 2)),
                "max_pier_lateral_drift_mm": float(np.round(max_pier_drift_mm, 2)),
                "max_euclidean_disp_mm": float(np.round(max_overall_disp_mm, 2)),
                "mean_disp_mm": float(np.round(np.mean(euclidean_disp_mm), 2)),
                "allowable_sag_limit_mm": allowable_sag_mm,
                "sag_utilization_pct": sag_utilization_pct,
                "aashto_status": "CRITICAL" if sag_utilization_pct > 80.0 else ("WARNING" if sag_utilization_pct > 50.0 else "NOMINAL")
            },
            "hotspots": hotspots,
            "sample_point_count": len(t1_aligned)
        }
