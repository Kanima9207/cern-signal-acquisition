# Results

This document records measured results from the reproducible software-only validation phase. Hardware measurements will be kept separate when laboratory validation becomes available.

## 1. Synthetic ADC signal validation

The simulation uses eight channels sampled at 50 kHz. CH2 contains a 1 kHz desired component and a strong 10 kHz interference component.

Baseline CH2 SNR: **17.50 dB**.

For a 16-bit ADC over a ±10 V input range:

- Quantization step (LSB): **0.30518 mV**
- Ideal quantization-noise RMS: **0.08810 mV**
- Simulated CH2 quantization RMS: **0.09032 mV**

The simulated quantization noise is approximately 2.5% above the ideal uniform-quantization RMS prediction.

## 2. Signal conditioning

A fourth-order Butterworth low-pass filter with a 4 kHz cutoff was used as the anti-aliasing/conditioning stage.

- Input sampling rate: **50.0 kHz**
- Filter cutoff: **4.0 kHz**
- Filter order: **4**
- Gain at 4 kHz: **-3.03 dB**
- Gain at 10 kHz: **-36.13 dB**
- Decimation factor: **2**
- Effective sampling rate after decimation: **25.0 kHz**
- New Nyquist frequency: **12.5 kHz**

The spectrum confirms preservation of the desired 1 kHz component while strongly suppressing the 10 kHz interference.

## 3. LMS adaptive filtering

The LMS adaptive-noise-cancellation experiment compared three learning rates with a 32-tap filter. Residual MSE is measured against the known clean simulated signal.

| Learning rate | Output SNR | SNR improvement | Residual MSE | Convergence time |
| ---: | ---: | ---: | ---: | ---: |
| 0.001 | **41.72 dB** | **+24.21 dB** | **0.000076 V²** | 4.68 ms |
| 0.010 | 21.07 dB | +3.57 dB | 0.008796 V² | 1.98 ms |
| 0.100 | -10.30 dB | -27.80 dB | 12.053224 V² | 1.98 ms |

For this experiment, **μ = 0.001** provides the best steady-state result. Increasing the learning rate reduces the measured initial convergence time, but increases misadjustment; μ = 0.1 produces unacceptable output quality. Convergence time must therefore be interpreted together with SNR and residual MSE rather than as a standalone performance measure.

## 4. Real-time-paced software simulation

The acquisition demonstration processes 8-channel data in stateful 100 ms chunks. LMS coefficients and reference history are retained between chunks.

Measured over 20 chunks on the development PC:

- Chunk processing deadline: **100 ms**
- Mean processing time: **20.27 ms**
- Worst-case processing time: **24.23 ms**
- Mean deadline utilization: **20.27%**
- Worst-case deadline utilization: **24.23%**
- Deadline misses: **0 / 20**
- Worst-case timing headroom: **75.77 ms**

All measured chunks completed within the simulated processing deadline.

### Interpretation

This result demonstrates that the current Python implementation can keep pace with the selected 100 ms software acquisition interval on the tested PC. It is a **real-time-paced software benchmark**, not a hard-real-time guarantee. Operating-system scheduling, different hardware, larger channel counts, smaller chunks, and embedded deployment can change the timing result.

## 5. Current software-phase conclusion

The software phase has demonstrated:

1. Reproducible eight-channel detector-like signal generation.
2. ADC quantization behavior consistent with theoretical expectations.
3. Fourth-order anti-aliasing filtering and controlled decimation.
4. LMS adaptive interference cancellation implemented from first principles.
5. A measured learning-rate/stability trade-off.
6. Stateful chunk-wise processing with live waveform, FFT, SNR and residual-MSE visualization.
7. Zero deadline misses in the current 20-chunk, 100 ms software benchmark.

## Hardware validation status

Hardware validation is pending laboratory access. Future measurements will compare real ADC noise floor, SNR, analog anti-aliasing response, acquisition timing and adaptive-filter behavior against the software model. Simulation results in this document must not be presented as hardware measurements.
