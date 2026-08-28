# Multi-Channel Digital Signal Acquisition & Adaptive Filtering

A software-first digital signal acquisition and signal-processing project designed to simulate a multi-channel detector-style readout chain and evaluate adaptive filtering techniques before hardware validation.

## Project Goals

- Simulate realistic multi-channel ADC data
- Study sampling, bandwidth, noise, harmonics, and quantization
- Implement digital signal conditioning and anti-aliasing models
- Implement adaptive LMS filtering from first principles
- Quantify SNR, MSE, convergence, and filter performance
- Build a real-time visualization/demo layer
- Keep the DSP pipeline hardware-ready for later STM32/ADC validation

## Planned Architecture

```text
Synthetic / Hardware Signal Sources
                |
                v
        Signal Conditioning
                |
                v
       ADC / Quantization Model
                |
                v
          Digital Samples
                |
                v
        Adaptive DSP (LMS)
                |
                v
       Analysis & Visualization
```

## Repository Structure

```text
cern-signal-acquisition/
├── dsp/                  # Reusable digital signal-processing modules
├── firmware/             # Future embedded acquisition code
├── data/                 # Reproducible raw and processed datasets
├── notebooks/            # Step-by-step experiments and analysis
├── visualization/        # Real-time/demo visualization
├── docs/                 # Theory, architecture, and measured results
├── tests/                # Automated validation
├── requirements.txt      # Python dependencies
└── README.md
```

## Development Roadmap

1. Signal generation and ADC simulation
2. Signal conditioning and anti-aliasing
3. LMS adaptive filtering
4. Real-time simulation and visualization
5. Documentation and reproducibility
6. Hardware validation when laboratory access is available

## Engineering Principle

All performance figures reported by this project will be measured from reproducible simulations or hardware experiments. No target result is treated as a measured result until it has been independently calculated.

## Status

**Phase 1 — Software-only development:** starting with signal-generation infrastructure.
