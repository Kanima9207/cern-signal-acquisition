"""Synthetic multi-channel signal generation for Phase 1 experiments.

The generator produces detector-style test signals before the real ADC/hardware
path is available. All random noise is controlled by a seed for reproducibility.
"""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class AcquisitionConfig:
    """Core simulation parameters."""

    fs: float = 50_000.0
    duration: float = 0.10
    num_channels: int = 8
    adc_bits: int = 16
    adc_min: float = -10.0
    adc_max: float = 10.0
    noise_rms: float = 0.0001
    seed: int = 20260901

    @property
    def num_samples(self) -> int:
        return int(round(self.fs * self.duration))

    @property
    def quantization_step(self) -> float:
        return (self.adc_max - self.adc_min) / (2**self.adc_bits - 1)


def chirp_signal(t: np.ndarray, f0: float, f1: float, amplitude: float = 1.0) -> np.ndarray:
    """Generate a linear frequency-sweep chirp."""
    duration = t[-1] if len(t) > 1 else 1.0
    k = (f1 - f0) / duration
    phase = 2.0 * np.pi * (f0 * t + 0.5 * k * t**2)
    return amplitude * np.sin(phase)


def add_harmonics(signal: np.ndarray, fundamental: float, t: np.ndarray,
                  h3: float = 0.03, h5: float = 0.01) -> np.ndarray:
    """Add controlled 3rd- and 5th-harmonic distortion."""
    return signal + h3 * np.sin(2 * np.pi * 3 * fundamental * t) + h5 * np.sin(2 * np.pi * 5 * fundamental * t)


def generate_channels(config: AcquisitionConfig | None = None):
    """Generate eight reproducible synthetic channels.

    Returns
    -------
    t : ndarray
        Time vector in seconds.
    clean : ndarray, shape (N, 8)
        Ideal channel signals in volts.
    noisy : ndarray, shape (N, 8)
        Signals after analog-like noise and interference are added.
    metadata : list[dict]
        Human-readable description of each channel.
    """
    cfg = config or AcquisitionConfig()
    rng = np.random.default_rng(cfg.seed)
    t = np.arange(cfg.num_samples) / cfg.fs
    clean = np.zeros((cfg.num_samples, cfg.num_channels), dtype=float)
    noisy = np.zeros_like(clean)

    # Eight deliberately different test conditions.
    clean[:, 0] = 2.0 * np.sin(2 * np.pi * 1_000 * t)
    clean[:, 1] = 1.5 * np.sin(2 * np.pi * 1_000 * t + np.pi / 6)
    clean[:, 2] = 1.8 * chirp_signal(t, 200, 4_000, amplitude=1.0)
    clean[:, 3] = 1.2 * np.sin(2 * np.pi * 800 * t)
    clean[:, 4] = 1.0 * np.sin(2 * np.pi * 1_200 * t)
    clean[:, 5] = 1.6 * np.sin(2 * np.pi * 1_000 * t)
    clean[:, 6] = 0.8 * np.sin(2 * np.pi * 2_000 * t)
    clean[:, 7] = 1.4 * np.sin(2 * np.pi * 500 * t)

    # Controlled nonlinear distortion on selected channels.
    clean[:, 3] = add_harmonics(clean[:, 3], 800, t)
    clean[:, 6] = add_harmonics(clean[:, 6], 2_000, t, h3=0.05, h5=0.02)

    interference = 0.20 * np.sin(2 * np.pi * 10_000 * t)
    for ch in range(cfg.num_channels):
        channel_noise = rng.normal(0.0, cfg.noise_rms, cfg.num_samples)
        noisy[:, ch] = clean[:, ch] + channel_noise

    # Deliberate 10 kHz reference/interference on channels 1, 5 and 7.
    noisy[:, 1] += interference
    noisy[:, 5] += 0.5 * interference
    noisy[:, 7] += 0.35 * interference

    # A short transient makes channel 6 useful for later robustness tests.
    transient_start = int(0.065 * cfg.fs)
    transient_end = transient_start + int(0.002 * cfg.fs)
    noisy[transient_start:transient_end, 6] += 0.6

    metadata = [
        {"channel": 1, "description": "1 kHz reference sine"},
        {"channel": 2, "description": "1 kHz sine + 10 kHz interference"},
        {"channel": 3, "description": "200 Hz to 4 kHz linear chirp"},
        {"channel": 4, "description": "800 Hz sine with 3rd/5th harmonics"},
        {"channel": 5, "description": "1.2 kHz clean test tone"},
        {"channel": 6, "description": "1 kHz sine + reduced 10 kHz interference"},
        {"channel": 7, "description": "2 kHz distorted tone + transient"},
        {"channel": 8, "description": "500 Hz sine + reduced 10 kHz interference"},
    ]
    return t, clean, noisy, metadata


def quantize(signal: np.ndarray, config: AcquisitionConfig | None = None) -> np.ndarray:
    """Apply an ideal signed ADC quantizer to a voltage signal."""
    cfg = config or AcquisitionConfig()
    clipped = np.clip(signal, cfg.adc_min, cfg.adc_max)
    codes = np.round((clipped - cfg.adc_min) / cfg.quantization_step)
    return cfg.adc_min + codes * cfg.quantization_step


def snr_db(reference: np.ndarray, measured: np.ndarray) -> float:
    """Estimate SNR from a reference signal and measured signal."""
    error = measured - reference
    signal_power = np.mean(reference**2)
    noise_power = np.mean(error**2)
    if noise_power <= 0:
        return np.inf
    return 10.0 * np.log10(signal_power / noise_power)
