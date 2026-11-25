"""
IoT Vibration Telemetry & PyTorch LSTM Autoencoder Module
=========================================================
Processes multi-channel tri-axial accelerometer telemetry from bridge sensors:
1. Signal Processing: Fast Fourier Transform (FFT) and Welch Power Spectral Density (PSD)
   to track structural modal natural frequencies (Mode 1, Mode 2, Mode 3).
2. Deep Learning Anomaly Detection: PyTorch LSTM Autoencoder trained on baseline vibration
   dynamics. Reconstructs temporal sequences and flags anomalies via reconstruction error (MSE).
"""

import numpy as np
import scipy.signal as signal
from typing import Dict, Any, Tuple, List, Optional
import os
import torch
import torch.nn as nn


class LSTMAutoencoder(nn.Module):
    """
    Bidirectional/Stacked LSTM Autoencoder for temporal vibration sequences.
    Encodes 3-axis accelerometer windows into latent representations, then reconstructs them.
    """
    def __init__(self, input_dim: int = 3, hidden_dim: int = 32, latent_dim: int = 16):
        super().__init__()
        self.encoder_lstm = nn.LSTM(input_dim, hidden_dim, num_layers=2, batch_first=True, dropout=0.1)
        self.encoder_linear = nn.Linear(hidden_dim, latent_dim)
        
        self.decoder_linear = nn.Linear(latent_dim, hidden_dim)
        self.decoder_lstm = nn.LSTM(hidden_dim, hidden_dim, num_layers=2, batch_first=True, dropout=0.1)
        self.output_linear = nn.Linear(hidden_dim, input_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Encode
        enc_out, (hn, cn) = self.encoder_lstm(x)
        latent = torch.relu(self.encoder_linear(hn[-1]))  # [batch, latent_dim]
        
        # Repeat latent vector across sequence length
        seq_len = x.size(1)
        dec_in = self.decoder_linear(latent).unsqueeze(1).repeat(1, seq_len, 1)
        
        # Decode
        dec_out, _ = self.decoder_lstm(dec_in)
        reconstruction = self.output_linear(dec_out)
        return reconstruction


class VibrationAnalysisEngine:
    def __init__(self, sampling_rate_hz: float = 200.0, window_size: int = 256):
        self.fs = sampling_rate_hz
        self.window_size = window_size
        self.device = torch.device("cpu")
        self.model = LSTMAutoencoder(input_dim=3, hidden_dim=32, latent_dim=16).to(self.device)
        self.baseline_mse_threshold = 0.08
        self._initialize_pretrained_weights()

    def _initialize_pretrained_weights(self):
        """Initializes and trains or fits weights on normal operational ambient vibrations."""
        # Generate short synthetic baseline to prime autoencoder weights
        t_base = np.linspace(0, 10.0, int(self.fs * 10))
        # Normal ambient vibration: Mode 1 (3.2 Hz), Mode 2 (7.8 Hz), Mode 3 (14.5 Hz) + micro-tremor
        ax = 0.04 * np.sin(2 * np.pi * 3.2 * t_base) + 0.015 * np.sin(2 * np.pi * 7.8 * t_base) + np.random.normal(0, 0.005, len(t_base))
        ay = 0.02 * np.sin(2 * np.pi * 3.2 * t_base) + 0.010 * np.sin(2 * np.pi * 14.5 * t_base) + np.random.normal(0, 0.004, len(t_base))
        az = 0.06 * np.sin(2 * np.pi * 3.2 * t_base) + 0.025 * np.sin(2 * np.pi * 7.8 * t_base) + np.random.normal(0, 0.006, len(t_base))
        baseline_signal = np.stack([ax, ay, az], axis=1)

        # Slice into windows
        windows = []
        step = self.window_size // 2
        for i in range(0, len(baseline_signal) - self.window_size, step):
            windows.append(baseline_signal[i:i + self.window_size])
        
        if len(windows) > 0:
            x_tensor = torch.tensor(np.array(windows), dtype=torch.float32)
            optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
            criterion = nn.MSELoss()
            
            self.model.train()
            # Fast calibration loop (15 epochs)
            for _ in range(15):
                optimizer.zero_grad()
                pred = self.model(x_tensor)
                loss = criterion(pred, x_tensor)
                loss.backward()
                optimizer.step()
            
            self.model.eval()
            with torch.no_grad():
                baseline_recon = self.model(x_tensor)
                baseline_losses = torch.mean((x_tensor - baseline_recon) ** 2, dim=(1, 2)).numpy()
                self.baseline_mse_threshold = float(np.percentile(baseline_losses, 95) * 1.5)

    def extract_modal_frequencies(self, signal_1d: np.ndarray) -> Dict[str, Any]:
        """
        Uses Welch's Power Spectral Density (PSD) and peak detection to extract
        dominant bridge natural frequencies (Mode 1, Mode 2, Mode 3).
        """
        nperseg = min(len(signal_1d), int(self.fs * 4))
        freqs, psd = signal.welch(signal_1d, fs=self.fs, nperseg=nperseg, noverlap=nperseg // 2)

        # Restrict search between 0.5 Hz and 30.0 Hz (structural bridge envelope)
        valid_idx = (freqs >= 0.5) & (freqs <= 30.0)
        valid_freqs = freqs[valid_idx]
        valid_psd = psd[valid_idx]

        # Find prominent peaks
        peaks, props = signal.find_peaks(valid_psd, height=np.max(valid_psd) * 0.05, distance=int(1.5 / (valid_freqs[1] - valid_freqs[0])))
        
        peak_freqs = valid_freqs[peaks]
        peak_powers = valid_psd[peaks]
        # Sort by peak power
        sorted_order = np.argsort(peak_powers)[::-1]
        dominant_freqs = peak_freqs[sorted_order]

        # Extract Mode 1 (Fundamental), Mode 2 (Torsional), Mode 3 (Higher Bending)
        mode_1 = float(dominant_freqs[0]) if len(dominant_freqs) > 0 else 3.20
        mode_2 = float(dominant_freqs[1]) if len(dominant_freqs) > 1 else 7.80
        mode_3 = float(dominant_freqs[2]) if len(dominant_freqs) > 2 else 14.50

        # Theoretical baseline healthy modes for this bridge design:
        baseline_modes = {"mode_1_hz": 3.25, "mode_2_hz": 7.85, "mode_3_hz": 14.60}
        
        # Calculate natural frequency drop percentage (Euler-Bernoulli: f proportional to sqrt(EI))
        delta_f1_pct = float(np.round(((baseline_modes["mode_1_hz"] - mode_1) / baseline_modes["mode_1_hz"]) * 100.0, 2))
        stiffness_loss_pct = float(np.round((1.0 - (mode_1 / baseline_modes["mode_1_hz"]) ** 2) * 100.0, 2)) if mode_1 <= baseline_modes["mode_1_hz"] else 0.0

        return {
            "mode_1_hz": round(mode_1, 3),
            "mode_2_hz": round(mode_2, 3),
            "mode_3_hz": round(mode_3, 3),
            "baseline_mode_1_hz": baseline_modes["mode_1_hz"],
            "frequency_drop_pct": max(0.0, delta_f1_pct),
            "estimated_stiffness_loss_pct": max(0.0, stiffness_loss_pct),
            "spectrum": {
                "frequencies": [round(float(f), 2) for f in freqs[::4]],
                "psd": [round(float(p), 6) for p in psd[::4]]
            }
        }

    def compute_anomaly_score(self, accel_xyz: np.ndarray) -> Dict[str, Any]:
        """
        Runs the PyTorch LSTM Autoencoder on acceleration telemetry windows [N, 3].
        Computes reconstruction MSE loss and outputs a normalized structural anomaly score [0.0 - 1.0].
        """
        self.model.eval()
        n_samples = len(accel_xyz)
        if n_samples < self.window_size:
            # Pad if shorter than window
            pad_len = self.window_size - n_samples
            accel_xyz = np.pad(accel_xyz, ((0, pad_len), (0, 0)), mode="edge")

        windows = []
        step = self.window_size // 2
        for i in range(0, len(accel_xyz) - self.window_size + 1, step):
            windows.append(accel_xyz[i:i + self.window_size])

        x_tensor = torch.tensor(np.array(windows), dtype=torch.float32).to(self.device)
        
        with torch.no_grad():
            recon = self.model(x_tensor)
            # Window-level reconstruction MSE
            window_mse = torch.mean((x_tensor - recon) ** 2, dim=(1, 2)).cpu().numpy()

        mean_mse = float(np.mean(window_mse))
        max_mse = float(np.max(window_mse))

        # Normalized anomaly score: 0.0 (clean) to 1.0 (severe degradation)
        normalized_anomaly = float(np.clip((mean_mse - 0.01) / (self.baseline_mse_threshold * 3.5), 0.0, 1.0))
        normalized_anomaly = float(np.round(normalized_anomaly, 3))

        is_anomalous = mean_mse > self.baseline_mse_threshold

        return {
            "mean_reconstruction_mse": round(mean_mse, 6),
            "max_reconstruction_mse": round(max_mse, 6),
            "threshold_mse": round(self.baseline_mse_threshold, 6),
            "anomaly_score_normalized": normalized_anomaly,
            "anomaly_detected": is_anomalous,
            "status": "CRITICAL" if normalized_anomaly > 0.7 else ("WARNING" if normalized_anomaly > 0.35 else "NOMINAL")
        }

    def analyze_vibration_stream(self, accel_xyz: np.ndarray) -> Dict[str, Any]:
        """Full end-to-end vibration diagnosis (FFT/Welch + LSTM AE)."""
        # Vertical acceleration is primary for beam bending (Z-axis)
        az = accel_xyz[:, 2] if accel_xyz.shape[1] >= 3 else accel_xyz[:, 0]
        modal_info = self.extract_modal_frequencies(az)
        anomaly_info = self.compute_anomaly_score(accel_xyz)

        return {
            "modal_analysis": modal_info,
            "lstm_autoencoder": anomaly_info,
            "rms_acceleration_g": float(np.round(np.sqrt(np.mean(accel_xyz ** 2)), 4)),
            "peak_acceleration_g": float(np.round(np.max(np.abs(accel_xyz)), 4))
        }
