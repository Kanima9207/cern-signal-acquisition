# Signal Model and Simulation Parameters

## Purpose

The software-only phase uses a deterministic, reproducible synthetic acquisition model. It is not presented as measured CERN detector data; it is an engineering testbench for developing and validating the DSP pipeline before hardware access.

## Acquisition Parameters

| Parameter | Value | Reason |
|---|---:|---|
| Channels | 8 | Matches the planned multi-channel architecture |
| Sampling frequency | 50 kHz | Safely represents the 10 kHz reference/interference and leaves design margin |
| ADC resolution | 16 bit | Representative high-resolution simulation target |
| ADC input range | ±10 V | Defined full-scale simulation range |
| Analog noise RMS | 0.1 mV | Controlled low-level test noise |
| Simulation duration | 100 ms | Long enough for spectral and convergence experiments |
| Random seed | 20260901 | Makes stochastic noise reproducible |

## Channel Design

The channels intentionally exercise different signal-processing cases:

1. 1 kHz reference sine
2. 1 kHz sine with 10 kHz interference
3. 200 Hz–4 kHz linear chirp
4. 800 Hz sine with controlled 3rd/5th harmonic distortion
5. 1.2 kHz clean test tone
6. 1 kHz sine with reduced 10 kHz interference
7. 2 kHz distorted tone plus a short transient
8. 500 Hz sine with reduced 10 kHz interference

## ADC Quantization

For a 16-bit ADC spanning 20 V peak-to-peak, the ideal code width is

\[
\Delta = \frac{20}{2^{16}-1} \approx 0.30518\text{ mV}.
\]

The ideal quantization-noise RMS for a uniformly distributed quantization error is approximately

\[
\sigma_q = \frac{\Delta}{\sqrt{12}}.
\]

The software model clips the signal to the configured ADC range before rounding to the nearest ADC code.

## Sampling Note

A 10 kHz signal cannot be represented correctly by a 10 kHz sampling frequency because the Nyquist frequency would also be 5 kHz in that case. The simulation therefore uses 50 kHz sampling. A later experiment may intentionally reduce the sampling rate to demonstrate aliasing.

## Reproducibility

Noise is generated with NumPy's `default_rng` using the fixed seed above. The generated HDF5 dataset stores both signal arrays and the acquisition parameters used to create them.

## Important Interpretation

These signals are synthetic engineering test vectors. Their purpose is to provide controlled inputs for filter design, adaptive-algorithm validation, and measurement methodology. Hardware validation will replace or supplement these vectors once laboratory access is available.
