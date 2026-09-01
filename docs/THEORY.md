# Theory

This document summarizes the signal-processing theory used by the software validation pipeline.

## 1. Sampling and Nyquist criterion

For a sampling frequency `Fs`, spectral components above `Fs/2` cannot be represented uniquely after sampling. The Nyquist frequency is therefore

`f_N = Fs / 2`.

The project initially samples at 50 kHz, giving a 25 kHz Nyquist frequency. After decimation by two, the effective sampling rate is 25 kHz and the new Nyquist frequency is 12.5 kHz. A low-pass stage is applied before decimation to suppress unwanted high-frequency content and reduce aliasing risk.

## 2. Butterworth low-pass conditioning

A Butterworth response is maximally flat in the passband. For an Nth-order low-pass prototype, its magnitude-squared response can be written as

`|H(jf)|^2 = 1 / (1 + (f/fc)^(2N))`.

At the cutoff frequency `fc`, the magnitude is approximately -3.01 dB. The project uses a fourth-order Butterworth filter with `fc = 4 kHz`. The measured software response is -3.03 dB at 4 kHz and -36.13 dB at 10 kHz.

The offline validation implementation uses zero-phase `sosfiltfilt`. This is useful for characterizing the conditioning model but is non-causal and is not presented as a deployable real-time analog or embedded anti-aliasing implementation.

## 3. ADC quantization

The implemented endpoint-inclusive quantizer uses

`LSB = (Vmax - Vmin) / (2^B - 1)`.

For 16 bits and a ±10 V range, this gives approximately 0.30518 mV per code. The commonly used ideal high-resolution quantization-noise approximation is

`sigma_q ≈ LSB / sqrt(12)`.

This predicts approximately 0.08810 mV RMS. The software experiment measured approximately 0.09032 mV RMS on CH2.

## 4. Signal-to-noise ratio

For a known clean reference signal `s[n]` and an observed/processed signal `x[n]`, the residual is

`r[n] = x[n] - s[n]`.

The project reports SNR as

`SNR = 10 log10(P_signal / P_residual)` dB,

where `P_signal = mean(s[n]^2)` and `P_residual = mean(r[n]^2)`.

This definition is especially useful in simulation because the clean reference is known exactly.

## 5. LMS adaptive filtering

The Least Mean Squares algorithm updates an FIR coefficient vector using the instantaneous error. For input vector `x[n]`, coefficient vector `w[n]`, desired observation `d[n]`, filter output `y[n]`, and error `e[n]`:

`y[n] = w[n]^T x[n]`

`e[n] = d[n] - y[n]`

`w[n+1] = w[n] + mu e[n] x[n]`

where `mu` is the learning rate (step size). This is the convention implemented in `dsp/adaptive_filters.py`; some texts absorb a factor of two into the definition of the step size.

In the adaptive-noise-cancellation arrangement, the LMS input is a reference correlated with the unwanted interference. The adaptive filter learns an estimate of that interference. Subtracting the estimate from the contaminated observation leaves the cleaned output.

### Learning-rate trade-off

A small learning rate normally adapts more conservatively and can reduce steady-state misadjustment, while a larger learning rate can adapt faster but may increase residual error or become unstable. This project measures that trade-off rather than assuming a preferred value.

For the current experiment, `mu = 0.001` gives the best measured steady-state performance: 41.72 dB output SNR and 0.000076 V² residual MSE. `mu = 0.1` produces severe misadjustment and negative output SNR.

## 6. Residual MSE

Because the clean simulated signal is available, residual mean-square error is calculated as

`MSE = mean((x_processed[n] - s[n])^2)`.

This is intentionally different from simply computing the power of the LMS error/output signal, which would include the desired signal energy and would not represent reconstruction error.

## 7. Convergence measurement

Convergence time estimates how quickly the adaptive process reaches a defined error-power neighborhood. It is not sufficient by itself to judge filter quality: a large learning rate can cross a convergence threshold quickly while having poor steady-state SNR or large residual MSE. The project therefore reports convergence together with SNR and residual MSE.

## 8. Chunk-wise processing and timing budget

The real-time-paced demonstration divides acquisition data into 100 ms blocks. Adaptive-filter coefficients and the required reference-signal history persist between blocks, so adaptation is stateful across chunk boundaries.

For each block, software processing time is compared with the 100 ms acquisition interval. Deadline utilization is

`utilization = processing_time / chunk_duration * 100%`.

The current PC benchmark measured 20.27 ms mean processing time, 24.23 ms worst-case processing time, and zero deadline misses over 20 chunks.

The timed region covers the stateful LMS processing and associated per-chunk software metrics after the conditioning signal has been prepared. The conditioning stage used by this demonstration is currently computed offline with zero-phase filtering, so the result should not be interpreted as an end-to-end causal streaming benchmark.

This establishes that the measured Python LMS stage keeps pace with the chosen simulated acquisition interval on the tested computer. It does not establish hard-real-time behavior, which would require controlled scheduling, hardware-specific timing analysis and later embedded validation.

## 9. Software-to-hardware validation strategy

The software model provides expected signal-chain behavior before laboratory access. Hardware validation should later measure actual ADC noise, analog filter response, sampling timing, data-transfer behavior and adaptive-filter performance, then compare those measurements with the software reference. Hardware results should remain clearly separated from simulated results.
