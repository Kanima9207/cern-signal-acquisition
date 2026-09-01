# Multi-Channel Digital Signal Acquisition & Adaptive Filtering

A software-first signal-acquisition and DSP project that models an eight-channel detector-style readout chain, validates signal conditioning and adaptive LMS filtering, and provides a stateful real-time-paced visualization demo before hardware validation.

## Highlights

- **8-channel** synthetic acquisition at **50 kHz**
- **4th-order Butterworth** conditioning filter with **4 kHz** cutoff
- **16-bit ±10 V ADC** quantization model
- LMS adaptive noise cancellation implemented **from first principles**
- CH2 SNR improved from **17.50 dB to 41.72 dB** at μ = 0.001
- Measured LMS learning-rate/stability trade-off for μ = 0.001, 0.01 and 0.1
- Stateful **100 ms chunk-wise** processing and live dashboard
- **0/20 deadline misses** in the current PC timing benchmark; worst measured processing time **24.23 ms** for a 100 ms budget

## Processing Architecture

```text
Synthetic signal source / future hardware ADC
                    |
                    v
          Multi-channel acquisition
                    |
                    v
       Anti-aliasing / conditioning
                    |
                    v
        ADC quantization / samples
                    |
                    v
       Stateful adaptive LMS stage
                    |
                    v
       SNR / MSE / FFT / timing
                    |
                    v
          Real-time-paced dashboard
```

## Key Measured Software Results

| Measurement | Result |
| --- | ---: |
| Baseline CH2 SNR | 17.50 dB |
| Best LMS output SNR | **41.72 dB** |
| Best SNR improvement | **+24.21 dB** |
| Best tested LMS μ | **0.001** |
| Residual MSE at μ=0.001 | **0.000076 V²** |
| LMS convergence time at μ=0.001 | 4.68 ms |
| Butterworth gain @ 4 kHz | -3.03 dB |
| Butterworth gain @ 10 kHz | -36.13 dB |
| 16-bit ADC LSB (±10 V) | 0.30518 mV |
| Simulated quantization RMS | 0.09032 mV |
| Mean 100 ms chunk processing time | 20.27 ms |
| Worst measured chunk processing time | 24.23 ms |
| Deadline misses | **0 / 20** |

Full measurement definitions and interpretation are in [`docs/RESULTS.md`](docs/RESULTS.md).

## Repository Structure

```text
cern-signal-acquisition/
├── dsp/                  # Signal conditioning and adaptive-filter modules
├── firmware/             # Reserved for future embedded acquisition code
├── data/                 # Reproducible datasets / generated measurements
├── notebooks/            # Signal generation, conditioning and LMS experiments
├── visualization/        # Matplotlib acquisition dashboard
├── docs/                 # Theory, architecture and measured results
├── tests/                # Validation tests
├── run_realtime_demo.py  # Stateful chunk-wise software demonstration
├── requirements.txt
└── README.md
```

## Run the Demo

Create/activate a Python virtual environment and install the project dependencies, then run:

```bash
pip install -r requirements.txt
python run_realtime_demo.py
```

The demonstration processes simulated multi-channel data in 100 ms chunks, retains LMS state between chunks, measures SNR/residual MSE and processing time, and displays the channel waveforms and CH2 spectrum.

## Engineering Notes

The current timing measurements are **real-time-paced software benchmarks**, not hard-real-time guarantees. They depend on the development PC, Python runtime and operating-system scheduling.

All numerical results reported here come from reproducible simulations or measured software execution. Hardware results will be documented separately after laboratory access is available; simulation results will not be presented as hardware measurements.

## Relevance

The project exercises signal-chain concepts relevant to instrumentation and detector readout: sampling and Nyquist constraints, anti-aliasing, ADC quantization, spectral analysis, interference rejection, adaptive filtering, multi-channel processing, reproducible measurement and processing-time budgeting. The software-first architecture is intended to make later hardware validation a comparison against an already characterized reference pipeline rather than a first attempt at the DSP design.
