# LMS Adaptive Filtering — Theory

## 1. Problem formulation

For adaptive noise cancellation, the measured signal is modeled as

`d[n] = s[n] + v[n]`

where `s[n]` is the desired signal and `v[n]` is unwanted interference. A reference `x[n]` is available that is correlated with `v[n]` but ideally weakly correlated with `s[n]`.

The adaptive filter estimates the interference:

`y[n] = w^T[n] x_vec[n]`

and the cleaned output is

`e[n] = d[n] - y[n]`.

## 2. LMS update

The LMS algorithm minimizes the instantaneous squared error `e²[n]` by updating the coefficient vector in the direction of the negative gradient:

`w[n+1] = w[n] + μ e[n] x_vec[n]`

where `μ` is the learning rate. This project uses the standard LMS convention above.

## 3. Learning-rate trade-off

A small `μ` generally gives slower adaptation but lower steady-state misadjustment. A larger `μ` generally adapts faster but increases misadjustment and can become unstable.

A commonly used sufficient stability guideline for white input is approximately

`0 < μ < 2 / (M P_x)`

where `M` is filter order and `P_x` is input/reference power. This is a guideline, not a guarantee for every correlated or non-stationary signal.

## 4. Project experiment

- Sampling frequency: 50 kHz
- Test channel: CH2
- Desired component: 1 kHz
- Interference: 10 kHz
- LMS order: 32
- Learning rates: 0.001, 0.01, 0.1
- Reference: correlated 10 kHz sinusoid with a small phase offset

The notebook measures baseline SNR, post-LMS SNR, MSE, learning curves, and coefficient evolution. All final performance claims must come from the executed experiment.
