"""Run the software-only real-time multi-channel DSP demonstration."""

from __future__ import annotations

import numpy as np

from dsp.adaptive_filters import LMSFilter, residual_mse, snr_db
from dsp.signal_processor import ConditioningConfig, SignalProcessor
from visualization.dsp_dashboard import DashboardConfig, DSPDashboard


FS = 50_000.0
DURATION = 2.0
CHANNELS = 8
CHUNK_MS = 100.0
MU = 0.001
ORDER = 32


def make_dataset(fs: float, duration: float, channels: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate repeatable 8-channel detector-like signals and references.

    Arrays use shape (channels, samples) for the dashboard and are transposed
    when passed to SignalProcessor, whose DSP axis is the sample axis.
    """
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

    config = ConditioningConfig(fs=FS, cutoff_hz=4000.0, filter_order=4)
    processor = SignalProcessor(config)

    # SignalProcessor operates along axis 0, so convert (channels, samples)
    # to (samples, channels) and transpose the result back for the dashboard.
    conditioned = processor.anti_aliasing_filter(raw.T).T

    # CH2 reference is correlated with its 10 kHz interference.
    t = np.arange(raw.shape[1]) / FS
    reference = np.sin(2 * np.pi * 10_000 * t)
    lms = LMSFilter(order=ORDER, learning_rate=MU)
    _, filtered_ch2, _ = lms.adapt(reference, conditioned[1])

    filtered_full = conditioned.copy()
    filtered_full[1] = filtered_ch2

    chunk = int(FS * CHUNK_MS / 1000)
    frames = []
    for start in range(0, raw.shape[1] - chunk + 1, chunk):
        stop = start + chunk
        y = filtered_full[1, start:stop]
        s = clean[1, start:stop]
        frame_mse = residual_mse(s, y)
        frame_snr = snr_db(s, y)
        frames.append((raw[:, start:stop], filtered_full[:, start:stop], frame_snr, frame_mse))

    DSPDashboard(
        DashboardConfig(fs=FS, channels=CHANNELS, chunk_ms=CHUNK_MS)
    ).show(frames)


if __name__ == "__main__":
    main()
