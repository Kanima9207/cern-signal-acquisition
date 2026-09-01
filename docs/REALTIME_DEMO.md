# Week 4 — Real-Time Visualization Demo

## Purpose

This stage presents the validated software DSP pipeline as a streaming acquisition demonstration. Synthetic 8-channel data is processed in 100 ms chunks and displayed continuously.

## Dashboard

The Matplotlib dashboard shows:

- eight raw/filtered channel waveforms;
- CH2 frequency spectrum;
- adaptive-filter residual error power;
- live SNR readout.

## Architecture

```text
Synthetic 8-channel ADC stream
            |
            v
     Signal conditioning
      (4 kHz LPF model)
            |
            +--------------------+
            |                    |
            v                    v
      Raw channel data      CH2 LMS filtering
                                 |
                                 v
                         Filtered CH2 output
                                 |
                                 v
                       SNR + residual MSE
                                 |
                                 v
                           Live dashboard
```

## Run

From the repository root, activate the project virtual environment and run:

```powershell
python run_realtime_demo.py
```

The demo uses deterministic random-seed data so the experiment is reproducible.

## Interpretation

This is a software real-time simulation, not a claim of hard real-time hardware performance. The 100 ms chunking models streaming behavior while keeping the experiment easy to reproduce on a PC. Hardware timing, ADC throughput, DMA, interrupt latency, and embedded implementation will be validated separately if laboratory access is approved.
