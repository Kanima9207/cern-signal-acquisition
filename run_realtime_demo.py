"""Run the software-only chunk-wise multi-channel DSP demonstration."""

from __future__ import annotations

from time import perf_counter

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
    """Generate repeatable detector-like signals with 10 kHz interference."""
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
    conditioned = processor.anti_aliasing_filter(raw.T).T

    t = np.arange(raw.shape[1]) / FS
    reference = np.sin(2 * np.pi * 10_000 * t)
    lms = LMSFilter(order=ORDER, learning_rate=MU)

    chunk = int(FS * CHUNK_MS / 1000.0)
    deadline_ms = CHUNK_MS
    reference_tail = np.zeros(ORDER - 1, dtype=float)
    frames = []
    processing_times_ms = []

    for chunk_index, start in enumerate(range(0, raw.shape[1] - chunk + 1, chunk), start=1):
        stop = start + chunk
        tic = perf_counter()

        ref_chunk = reference[start:stop]
        desired_chunk = conditioned[1, start:stop]
        padded_ref = np.concatenate((reference_tail, ref_chunk))
        filtered_ch2 = np.empty_like(desired_chunk)

        for i, d_sample in enumerate(desired_chunk):
            x = padded_ref[i:i + ORDER][::-1]
            _, filtered_ch2[i], _ = lms.update(x, d_sample)
        reference_tail = padded_ref[-(ORDER - 1):].copy()

        filtered_chunk = conditioned[:, start:stop].copy()
        filtered_chunk[1] = filtered_ch2
        clean_chunk = clean[1, start:stop]
        frame_mse = residual_mse(clean_chunk, filtered_ch2)
        frame_snr = snr_db(clean_chunk, filtered_ch2)

        elapsed_ms = (perf_counter() - tic) * 1000.0
        processing_times_ms.append(elapsed_ms)
        frames.append((raw[:, start:stop], filtered_chunk, frame_snr, frame_mse))

        utilization = 100.0 * elapsed_ms / deadline_ms
        status = "OK" if elapsed_ms <= deadline_ms else "MISS"
        print(
            f"chunk {chunk_index:02d}: processing={elapsed_ms:7.3f} ms | "
            f"budget={deadline_ms:.1f} ms | utilization={utilization:6.2f}% | {status}"
        )

    times = np.asarray(processing_times_ms)
    worst_ms = float(np.max(times))
    mean_ms = float(np.mean(times))
    misses = int(np.sum(times > deadline_ms))
    print("\nTiming summary")
    print("-" * 60)
    print(f"Chunk duration / deadline : {deadline_ms:.1f} ms")
    print(f"Mean processing time      : {mean_ms:.3f} ms")
    print(f"Worst processing time     : {worst_ms:.3f} ms")
    print(f"Mean utilization          : {100.0 * mean_ms / deadline_ms:.2f}%")
    print(f"Worst-case utilization    : {100.0 * worst_ms / deadline_ms:.2f}%")
    print(f"Deadline misses           : {misses}/{len(times)}")
    print(
        "Timing result              : "
        + ("PASS (all chunks within budget)" if misses == 0 else "FAIL (deadline miss detected)")
    )

    DSPDashboard(
        DashboardConfig(
            fs=FS,
            channels=CHANNELS,
            chunk_ms=CHUNK_MS,
            history_seconds=0.02,
            fft_size=4096,
        )
    ).show(frames)


if __name__ == "__main__":
    main()
