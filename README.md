# Multi-Channel Digital Signal Acquisition & Adaptive Filtering

Eight-channel signal-acquisition and DSP pipeline for ADC modelling, signal conditioning, decimation, adaptive interference cancellation, and real-time chunk processing.

### [Launch the live Multi-Channel DAQ & Adaptive Filtering Demo](https://cern-signal-acquisition-demo.streamlit.app/)

Explore the project interactively in the deployed Streamlit demo.


## Highlights

- **8-channel** synthetic acquisition at **50 kHz**
- **4th-order Butterworth** low-pass conditioning with **4 kHz** cutoff
- **16-bit ±10 V ADC** quantization model
- LMS adaptive interference cancellation implemented from first principles
- CH2 SNR improved from **17.50 dB to 41.72 dB** at μ = 0.001
- Measured learning-rate/stability behaviour for μ = 0.001, 0.01 and 0.1
- Stateful **100 ms chunk-wise** processing
- **0/20 deadline misses** in the recorded PC timing benchmark; worst processing time **24.23 ms** against a 100 ms budget

## Signal Chain

```text
Synthetic multi-channel source
          |
          v
Signal conditioning / low-pass filtering
          |
          v
16-bit ADC quantization
          |
          v
Decimation
          |
          v
Stateful LMS interference cancellation
          |
          v
SNR / MSE / FFT / timing analysis
          |
          v
Real-time-paced visualization
```

## Measured Software Results

| Measurement | Result |
|---|---:|
| Baseline CH2 SNR | 17.50 dB |
| Best LMS output SNR | **41.72 dB** |
| Best SNR improvement | **+24.21 dB** |
| Best tested LMS μ | **0.001** |
| Residual MSE at μ = 0.001 | **0.000076 V²** |
| LMS convergence time at μ = 0.001 | 4.68 ms |
| Butterworth gain @ 4 kHz | -3.03 dB |
| Butterworth gain @ 10 kHz | -36.13 dB |
| 16-bit ADC LSB (±10 V) | 0.30518 mV |
| Simulated quantization RMS | 0.09032 mV |
| Samples before / after decimation | 5000 / 2500 |
| Effective sample rate after decimation | 25 kHz |
| Mean 100 ms chunk processing time | 20.27 ms |
| Worst measured chunk processing time | 24.23 ms |
| Deadline misses | **0 / 20** |

Detailed measurement definitions are documented in [`docs/RESULTS.md`](docs/RESULTS.md).

## LMS Step-Size Study

| μ | Output SNR | ΔSNR | Residual MSE |
|---:|---:|---:|---:|
| 0.001 | **41.72 dB** | **+24.21 dB** | 0.000076 V² |
| 0.010 | 21.07 dB | +3.57 dB | 0.008796 V² |
| 0.100 | -10.30 dB | -27.80 dB | 12.053224 V² |

The sweep demonstrates the LMS convergence/stability trade-off: increasing the step size accelerates adaptation only within a stable operating range; an excessively large value causes poor cancellation and instability.

## Run Locally

```bash
git clone https://github.com/Kanima9207/cern-signal-acquisition.git
cd cern-signal-acquisition
python -m venv .venv
pip install -r requirements.txt
python run_realtime_demo.py
```

The demo processes simulated eight-channel data in 100 ms chunks, preserves LMS state between chunks, reports SNR/residual MSE and processing time, and visualizes the channel waveforms and CH2 spectrum.

## Repository Structure

```text
dsp/                  Signal conditioning and adaptive-filter modules
data/                 Reproducible datasets / generated measurements
notebooks/            Signal-generation, conditioning and LMS experiments
visualization/        Acquisition visualization
docs/                 Theory, architecture and measured results
tests/                Validation tests
firmware/             Hardware-facing work reserved for later validation
run_realtime_demo.py  Stateful chunk-wise demonstration
requirements.txt
```

## Validation Boundary

The timing results are real-time-paced **software measurements**, not hard-real-time guarantees. They depend on the development computer, Python runtime, and operating-system scheduling.

All numerical results reported here come from reproducible simulation or measured software execution. No physical ADC, embedded target, or detector hardware performance is claimed.

## Engineering Scope

The project covers sampling and Nyquist constraints, digital signal conditioning, ADC quantization, decimation, spectral analysis, adaptive interference rejection, multi-channel processing, reproducible measurement, and processing-time budgeting.

The more extensive fault-tolerant DAQ/RTL work is maintained separately in [RADIANT-DAQ](https://github.com/Kanima9207/radiant-daq).

## Author

**Kanishka Malakar** — Instrumentation Engineering
