"""Adaptive filtering algorithms used by the acquisition project."""

import numpy as np


class LMSFilter:
    """LMS adaptive noise-cancellation filter."""

    def __init__(self, order=32, learning_rate=0.01, normalized=False, epsilon=1e-8):
        if order < 1:
            raise ValueError("order must be >= 1")
        if learning_rate <= 0:
            raise ValueError("learning_rate must be > 0")
        self.order = int(order)
        self.mu = float(learning_rate)
        self.normalized = bool(normalized)
        self.epsilon = float(epsilon)
        self.w = np.zeros(self.order, dtype=float)

    def reset(self):
        self.w.fill(0.0)

    def update(self, x, d):
        """Return estimated interference, cleaned output, and coefficients."""
        x = np.asarray(x, dtype=float)
        if x.shape != (self.order,):
            raise ValueError(f"x must have shape ({self.order},)")
        y = float(np.dot(self.w, x))
        e = float(d - y)
        step = self.mu
        if self.normalized:
            step = self.mu / (np.dot(x, x) + self.epsilon)
        self.w += step * e * x
        return y, e, self.w.copy()

    def adapt(self, reference, desired):
        """Run adaptive noise cancellation over complete 1-D signals."""
        reference = np.asarray(reference, dtype=float)
        desired = np.asarray(desired, dtype=float)
        if reference.ndim != 1 or desired.ndim != 1:
            raise ValueError("reference and desired must be 1-D arrays")
        if len(reference) != len(desired):
            raise ValueError("reference and desired must have equal length")
        n = len(desired)
        output = np.zeros(n)
        error = np.zeros(n)
        weights = np.zeros((n, self.order))
        padded = np.pad(reference, (self.order - 1, 0))
        for i in range(n):
            x = padded[i:i + self.order][::-1]
            output[i], error[i], weights[i] = self.update(x, desired[i])
        return output, error, weights


def mse(error, start=0):
    """Return mean-square value of an error/output signal."""
    error = np.asarray(error, dtype=float)
    if not 0 <= start < len(error):
        raise ValueError("start must be within the error array")
    return float(np.mean(error[start:] ** 2))


def residual_mse(clean, estimate, start=0):
    """Return MSE between the cleaned estimate and known clean signal."""
    clean = np.asarray(clean, dtype=float)
    estimate = np.asarray(estimate, dtype=float)
    if clean.shape != estimate.shape:
        raise ValueError("clean and estimate must have the same shape")
    if not 0 <= start < len(clean):
        raise ValueError("start must be within the signal arrays")
    return float(np.mean((estimate[start:] - clean[start:]) ** 2))


def snr_db(clean, estimate, start=0):
    """Compute SNR in dB between a clean reference and an estimate."""
    clean = np.asarray(clean, dtype=float)
    estimate = np.asarray(estimate, dtype=float)
    if clean.shape != estimate.shape:
        raise ValueError("clean and estimate must have the same shape")
    clean = clean[start:]
    estimate = estimate[start:]
    noise = estimate - clean
    signal_power = np.mean(clean ** 2)
    noise_power = np.mean(noise ** 2)
    if noise_power == 0:
        return np.inf
    return float(10 * np.log10(signal_power / noise_power))
