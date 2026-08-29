"""Digital signal-conditioning models for the acquisition pipeline."""

from dataclasses import dataclass
import numpy as np
from scipy import signal


@dataclass(frozen=True)
class ConditioningConfig:
    """Parameters for the simulated conditioning chain."""

    fs: float = 50_000.0
    cutoff_hz: float = 4_000.0
    filter_order: int = 4
    adc_bits: int = 16
    adc_min: float = -10.0
    adc_max: float = 10.0

    @property
    def quantization_step(self) -> float:
        return (self.adc_max - self.adc_min) / (2**self.adc_bits - 1)


class SignalProcessor:
    """Reusable signal-conditioning pipeline for one or more channels."""

    def __init__(self, config: ConditioningConfig | None = None):
        self.config = config or ConditioningConfig()
        self._sos = signal.butter(
            self.config.filter_order,
            self.config.cutoff_hz,
            btype="lowpass",
            fs=self.config.fs,
            output="sos",
        )

    def anti_aliasing_filter(self, samples: np.ndarray) -> np.ndarray:
        """Apply a zero-phase Butterworth LPF to 1-D or (N, channels) data."""
        samples = np.asarray(samples, dtype=float)
        if samples.ndim not in (1, 2):
            raise ValueError("samples must be a 1-D or 2-D array")
        axis = 0
        return signal.sosfiltfilt(self._sos, samples, axis=axis)

    def filter_response(self, worN: int = 2048):
        """Return frequency response of the designed digital LPF."""
        return signal.sosfreqz(self._sos, worN=worN, fs=self.config.fs)

    def downsample(self, samples: np.ndarray, factor: int = 2) -> np.ndarray:
        """Decimate after anti-aliasing; factor must be a positive integer."""
        if not isinstance(factor, (int, np.integer)) or factor < 1:
            raise ValueError("factor must be a positive integer")
        if factor == 1:
            return np.asarray(samples)
        samples = np.asarray(samples, dtype=float)
        return signal.resample_poly(samples, up=1, down=factor, axis=0)

    def quantize(self, samples: np.ndarray) -> np.ndarray:
        """Apply an ideal signed ADC quantizer with input-range clipping."""
        cfg = self.config
        clipped = np.clip(samples, cfg.adc_min, cfg.adc_max)
        codes = np.round((clipped - cfg.adc_min) / cfg.quantization_step)
        return cfg.adc_min + codes * cfg.quantization_step

    def normalize(self, samples: np.ndarray, peak: float = 1.0) -> np.ndarray:
        """Scale data so its maximum absolute value equals ``peak``."""
        if peak <= 0:
            raise ValueError("peak must be positive")
        samples = np.asarray(samples, dtype=float)
        max_abs = np.max(np.abs(samples))
        if max_abs == 0:
            return samples.copy()
        return samples * (peak / max_abs)

    def process(self, samples: np.ndarray, downsample_factor: int = 1) -> dict:
        """Run filter, optional decimation, and quantization."""
        filtered = self.anti_aliasing_filter(samples)
        decimated = self.downsample(filtered, downsample_factor)
        quantized = self.quantize(decimated)
        return {
            "filtered": filtered,
            "decimated": decimated,
            "quantized": quantized,
        }
