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
        self.raw_history = [deque(maxlen=self.history) for _ in range(self.cfg.channels)]
        self.filtered_history = [deque(maxlen=self.history) for _ in range(self.cfg.channels)]
        self.error_history = deque(maxlen=max(10, int(self.history / self.chunk)))
        self.snr_history = deque(maxlen=max(10, int(self.history / self.chunk)))
        self.fig = None
        self.wave_axes = []
        self.wave_lines = []
        self.filtered_lines = []
        self.fft_ax = None
        self.error_ax = None
        self.fft_line = None
        self.error_line = None
        self.snr_text = None
        self.animation = None

    def _setup(self) -> None:
        self.fig = plt.figure(figsize=(14, 12), constrained_layout=True)
        grid = self.fig.add_gridspec(5, 2, height_ratios=[1, 1, 1, 1, 1.35])

        # Eight separate channel panels make the multi-channel data readable.
        for ch in range(self.cfg.channels):
            ax = self.fig.add_subplot(grid[ch // 2, ch % 2])
            raw_line, = ax.plot([], [], linewidth=0.8, alpha=0.45, label="Raw")
            filt_line, = ax.plot([], [], linewidth=1.0, alpha=0.9, label="Filtered")
            ax.set_title(f"CH{ch + 1}")
            ax.set_ylabel("V")
            ax.grid(True, alpha=0.2)
            if ch >= self.cfg.channels - 2:
                ax.set_xlabel("Time relative to current chunk (s)")
            if ch == 0:
                ax.legend(loc="upper right", fontsize=8)
            self.wave_axes.append(ax)
            self.wave_lines.append(raw_line)
            self.filtered_lines.append(filt_line)

        self.fft_ax = self.fig.add_subplot(grid[4, 0])
        self.fft_line, = self.fft_ax.plot([], [], linewidth=1.0)
        self.fft_ax.set_title("CH2 Spectrum — Filtered Output")
        self.fft_ax.set_xlabel("Frequency (Hz)")
        self.fft_ax.set_ylabel("Magnitude (dB)")
        self.fft_ax.set_xlim(0, 15_000)
        self.fft_ax.set_ylim(-100, 10)
        self.fft_ax.grid(True, alpha=0.2)

        self.error_ax = self.fig.add_subplot(grid[4, 1])
        self.error_line, = self.error_ax.plot([], [], linewidth=1.0)
        self.error_ax.set_title("Adaptive Filter Residual MSE")
        self.error_ax.set_xlabel("Chunk")
        self.error_ax.set_ylabel("Residual MSE (V²)")
        self.error_ax.grid(True, alpha=0.2)
        self.snr_text = self.error_ax.text(
            0.98, 0.9, "SNR: -- dB", transform=self.error_ax.transAxes, ha="right", fontsize=11
        )
        self.fig.suptitle("Software Acquisition Demo — Initializing", fontsize=15)

    def update(
        self,
        frame: int,
        raw_chunk: np.ndarray,
        filtered_chunk: np.ndarray,
        snr_db: float,
        mse: float,
    ) -> None:
        if self.fig is None:
            self._setup()

        raw_chunk = np.asarray(raw_chunk)
        filtered_chunk = np.asarray(filtered_chunk)
        if raw_chunk.shape != filtered_chunk.shape or raw_chunk.shape[0] != self.cfg.channels:
            raise ValueError("raw_chunk and filtered_chunk must have shape (channels, samples)")

        for ch in range(self.cfg.channels):
            self.raw_history[ch].extend(raw_chunk[ch])
            self.filtered_history[ch].extend(filtered_chunk[ch])
            n = len(self.raw_history[ch])
            # Always show the most recent history ending at t=0. This avoids
            # plotting data outside the visible time window.
            x = np.arange(-n + 1, 1) / self.cfg.fs
            self.wave_lines[ch].set_data(x, np.asarray(self.raw_history[ch]))
            self.filtered_lines[ch].set_data(x, np.asarray(self.filtered_history[ch]))
            ax = self.wave_axes[ch]
            ax.set_xlim(x[0], 0.0)
            values = np.concatenate((np.asarray(self.raw_history[ch]), np.asarray(self.filtered_history[ch])))
            ymin, ymax = float(values.min()), float(values.max())
            margin = max(0.05, 0.08 * max(ymax - ymin, 1e-6))
            ax.set_ylim(ymin - margin, ymax + margin)

        y = np.asarray(self.filtered_history[1])
        n = min(len(y), self.cfg.fft_size)
        if n >= 16:
            window = np.hanning(n)
            centered = y[-n:] - np.mean(y[-n:])
            spectrum = np.fft.rfft(centered * window)
            mag = 20 * np.log10(np.maximum(np.abs(spectrum) / np.sum(window) * 2.0, 1e-12))
            freq = np.fft.rfftfreq(n, 1 / self.cfg.fs)
            self.fft_line.set_data(freq, mag)

        self.error_history.append(float(mse))
        self.snr_history.append(float(snr_db))
        chunks = np.arange(1, len(self.error_history) + 1)
        self.error_line.set_data(chunks, np.asarray(self.error_history))
        self.error_ax.relim()
        self.error_ax.autoscale_view(scalex=True, scaley=True)
        self.snr_text.set_text(f"SNR: {snr_db:.2f} dB")
        self.fig.suptitle(f"Software Acquisition Demo — chunk {frame + 1}/{self._frame_count}", fontsize=15)

    def show(self, frames: list[tuple[np.ndarray, np.ndarray, float, float]]) -> None:
        self._setup()
        self._frame_count = len(frames)

        def animate(i: int):
            self.update(i, *frames[i])
            artists = self.wave_lines + self.filtered_lines + [self.fft_line, self.error_line, self.snr_text]
            return artists

        self.animation = FuncAnimation(
            self.fig,
            animate,
            frames=len(frames),
            interval=self.cfg.chunk_ms,
            blit=False,
            repeat=False,
        )
        plt.show()
