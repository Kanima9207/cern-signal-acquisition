"""Real-time multi-channel DSP dashboard for the software acquisition demo."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


@dataclass
class DashboardConfig:
    fs: float = 50_000.0
    channels: int = 8
    chunk_ms: float = 100.0
    history_seconds: float = 1.0
    fft_size: int = 2048


class DSPDashboard:
    """Matplotlib dashboard for an offline real-time-streaming simulation."""

    def __init__(self, config: DashboardConfig | None = None) -> None:
        self.cfg = config or DashboardConfig()
        self.chunk = max(1, int(self.cfg.fs * self.cfg.chunk_ms / 1000.0))
        self.history = max(self.chunk, int(self.cfg.fs * self.cfg.history_seconds))
        self.time = np.arange(self.history) / self.cfg.fs
        self.raw_history = [deque(maxlen=self.history) for _ in range(self.cfg.channels)]
        self.filtered_history = [deque(maxlen=self.history) for _ in range(self.cfg.channels)]
        self.error_history = deque(maxlen=self.history)
        self.snr_history = deque(maxlen=max(10, int(1000 / self.cfg.chunk_ms)))
        self.fig = None
        self.wave_ax = None
        self.fft_ax = None
        self.error_ax = None
        self.wave_lines = []
        self.filtered_lines = []
        self.fft_line = None
        self.error_line = None
        self.snr_text = None
        self.animation = None  # Keep a strong reference so Matplotlib does not garbage-collect it.

    def _setup(self) -> None:
        self.fig = plt.figure(figsize=(13, 9), constrained_layout=True)
        grid = self.fig.add_gridspec(3, 1, height_ratios=[2.0, 1.4, 1.1])
        self.wave_ax = self.fig.add_subplot(grid[0])
        self.fft_ax = self.fig.add_subplot(grid[1])
        self.error_ax = self.fig.add_subplot(grid[2])

        for ch in range(self.cfg.channels):
            line, = self.wave_ax.plot([], [], linewidth=0.8, alpha=0.45)
            filt, = self.wave_ax.plot([], [], linewidth=1.0, alpha=0.9)
            self.wave_lines.append(line)
            self.filtered_lines.append(filt)
        self.wave_ax.set_title("8-Channel Acquisition: Raw vs Filtered")
        self.wave_ax.set_xlabel("Time (s)")
        self.wave_ax.set_ylabel("Amplitude (V)")
        self.wave_ax.grid(True, alpha=0.2)

        self.fft_line, = self.fft_ax.plot([], [], linewidth=1.0)
        self.fft_ax.set_title("CH2 Spectrum")
        self.fft_ax.set_xlabel("Frequency (Hz)")
        self.fft_ax.set_ylabel("Magnitude (dB)")
        self.fft_ax.set_xlim(0, 15_000)
        self.fft_ax.set_ylim(-100, 10)
        self.fft_ax.grid(True, alpha=0.2)

        self.error_line, = self.error_ax.plot([], [], linewidth=1.0)
        self.error_ax.set_title("Adaptive Filter Error Power")
        self.error_ax.set_xlabel("Chunk")
        self.error_ax.set_ylabel("Mean squared error (V²)")
        self.error_ax.grid(True, alpha=0.2)
        self.snr_text = self.error_ax.text(0.99, 0.9, "SNR: -- dB", transform=self.error_ax.transAxes, ha="right")

    def update(self, frame: int, raw_chunk: np.ndarray, filtered_chunk: np.ndarray, snr_db: float, mse: float) -> None:
        if self.fig is None:
            self._setup()
        raw_chunk = np.asarray(raw_chunk)
        filtered_chunk = np.asarray(filtered_chunk)
        if raw_chunk.shape != filtered_chunk.shape or raw_chunk.shape[0] != self.cfg.channels:
            raise ValueError("raw_chunk and filtered_chunk must have shape (channels, samples)")

        for ch in range(self.cfg.channels):
            self.raw_history[ch].extend(raw_chunk[ch])
            self.filtered_history[ch].extend(filtered_chunk[ch])
            self.wave_lines[ch].set_data(self.time[-len(self.raw_history[ch]):], self.raw_history[ch])
            self.filtered_lines[ch].set_data(self.time[-len(self.filtered_history[ch]):], self.filtered_history[ch])

        y = np.asarray(self.filtered_history[1])
        n = min(len(y), self.cfg.fft_size)
        if n >= 16:
            window = np.hanning(n)
            spectrum = np.fft.rfft((y[-n:] - np.mean(y[-n:])) * window)
            mag = 20 * np.log10(np.maximum(np.abs(spectrum) / np.sum(window) * 2, 1e-12))
            freq = np.fft.rfftfreq(n, 1 / self.cfg.fs)
            self.fft_line.set_data(freq, mag)

        self.error_history.append(float(mse))
        self.snr_history.append(float(snr_db))
        self.error_line.set_data(np.arange(len(self.error_history)), self.error_history)
        self.error_ax.relim()
        self.error_ax.autoscale_view(scalex=True, scaley=True)
        self.wave_ax.relim()
        self.wave_ax.autoscale_view(scalex=False, scaley=True)
        self.snr_text.set_text(f"SNR: {snr_db:.2f} dB")
        self.fig.suptitle(f"Software Acquisition Demo — chunk {frame + 1}")

    def show(self, frames: list[tuple[np.ndarray, np.ndarray, float, float]]) -> None:
        self._setup()

        def animate(i: int):
            self.update(i, *frames[i])
            artists = self.wave_lines + self.filtered_lines + [self.fft_line, self.error_line, self.snr_text]
            return artists

        # Keep the animation object alive for the lifetime of the figure.
        self.animation = FuncAnimation(
            self.fig,
            animate,
            frames=len(frames),
            interval=self.cfg.chunk_ms,
            blit=False,
            repeat=False,
        )
        plt.show()
