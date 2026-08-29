# Signal Conditioning Architecture

## Simulated acquisition chain

```text
Analog / detector-like signal
            |
            v
      Gain / scaling
            |
            v
  4 kHz Butterworth LPF
     (anti-aliasing)
            |
            v
       ADC sampling
            |
            v
      16-bit quantization
            |
            v
       Digital samples
```

## Design parameters

| Parameter | Value |
|---|---:|
| Sampling frequency | 50 kHz |
| Anti-aliasing cutoff | 4 kHz |
| Filter | 4th-order Butterworth LPF |
| ADC resolution | 16 bit |
| ADC input range | -10 V to +10 V |
| Optional decimation | 2x |

## Why the filter is before the ADC

An ADC samples the continuous-time input. Frequency components above the allowed input bandwidth can alias into the sampled spectrum and cannot be removed reliably after sampling. The anti-aliasing filter therefore limits the analog bandwidth before conversion.

The software pipeline models this behavior digitally so that the acquisition architecture can be evaluated before laboratory hardware is available.

## Important interpretation

The `sosfiltfilt` implementation is a **simulation model**, not a literal real-time analog implementation. It is used to characterize the filter response without introducing phase distortion in the offline analysis. A future hardware implementation will use an actual analog anti-aliasing filter before the ADC.
