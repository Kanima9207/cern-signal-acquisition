"""Run the software-only real-time multi-channel DSP demonstration."""

from __future__ import annotations

import numpy as np

from dsp.adaptive_filters import LMSFilter
from dsp.signal_processor import SignalProcessor
from visualization.dsp_dashboard import DashboardConfig, DSPDashboard


FS = 50_000.0
DURATION = 2.0
CHANNELS = 8
CHUNK_MS = 100.0
MU = 0.001
ORDER = 32


def make_dataset(fs: float, duration: float, channels: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate repeatable 8-channel detector-like signals and references."""
    rng = np.random.default_rng(42)
    t = np.arange(int(fs * duration)) / fs
    clean = np.zeros((channels, len(t)))
    raw = np.zeros_like(clean)
    for ch in range(channels):
        amp = 2.0 * (1.0 - 0.05 * ch)
        clean[ch] = amp * np.sin(2 * np.pi * 1000 * t)
        interference = (0.20 + 0.03 * (ch % 4)) * np.sin(2 * np.pi * 10_000 * t + 0.1 * ch)
        noise = 0.0001 * rng.standard_normal(len(t))
        raw[ch] = clean[ch] + interference + noise
    return raw, clean


def main() -> None:
    raw, clean = make_dataset(FS, DURATION, CHANNELS)
    processor = SignalProcessor(fs=int(FS), num_channels=CHANNELS)
    conditioned = processor.anti_aliasing_filter(raw, cutoff=4000.0)

    # CH2 reference is correlated with its 10 kHz interference.
    t = np.arange(raw.shape[1]) / FS
    reference = np.sin(2 * np.pi * 10_000 * t)
    lms = LMSFilter(order=ORDER, learning_rate=MU)
    _, filtered_ch2, _, _ = lms.adapt(reference, conditioned[1], return_history=True)

    # Preserve equal array lengths by padding the initial LMS transient.
    filtered_full = conditioned.copy()
    pad = conditioned.shape[1] - len(filtered_ch2)
    filtered_full[1] = np.pad(filtered_ch2, (pad, 0), mode="edge")

    chunk = int(FS * CHUNK_MS / 1000)
    frames = []
    for start in range(0, raw.shape[1] - chunk + 1, chunk):
        stop = start + chunk
        y = filtered_full[1, start:stop]
        s = clean[1, start:stop]
        residual_mse = float(np.mean((y - s) ** 2))
        signal_power = np.mean(s ** 2)
        snr = 10 * np.log10(signal_power / max(residual_mse, 1e-15))
        frames.append((raw[:, start:stop], filtered_full[:, start:stop], snr, residual_mse))

    DSPDashboard(DashboardConfig(fs=FS, channels=CHANNELS, chunk_ms=CHUNK_MS)).show(frames)


if __name__ == "__main__":
    main()
