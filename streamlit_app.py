"""Interactive Streamlit demo for the multi-channel acquisition and LMS pipeline."""

from __future__ import annotations

import numpy as np
import streamlit as st

from dsp.adaptive_filters import LMSFilter, residual_mse, snr_db
from dsp.signal_processor import ConditioningConfig, SignalProcessor

FS = 50_000.0
CHANNELS = 8
ORDER = 32

st.set_page_config(page_title="Multi-Channel DAQ & Adaptive Filtering", page_icon="📡", layout="wide")
st.title("📡 Multi-Channel DAQ & Adaptive Filtering")
st.caption("Interactive software demonstration of an 8-channel acquisition, conditioning and LMS interference-cancellation pipeline.")

with st.sidebar:
    st.header("Acquisition controls")
    duration = st.slider("Signal duration (s)", 0.2, 2.0, 1.0, 0.1)
    channel = st.selectbox("Displayed channel", list(range(CHANNELS)), index=1)
    mu = st.select_slider("LMS step size μ", options=[0.001, 0.01, 0.1], value=0.001)
    interference_hz = st.slider("Interference frequency (Hz)", 6000, 12000, 10000, 500)

rng = np.random.default_rng(42)
t = np.arange(int(FS * duration)) / FS
clean = np.zeros((CHANNELS, len(t)))
raw = np.zeros_like(clean)
for ch in range(CHANNELS):
    amp = 2.0 * (1.0 - 0.05 * ch)
    clean[ch] = amp * np.sin(2 * np.pi * 1000 * t)
    interference = (0.20 + 0.03 * (ch % 4)) * np.sin(2 * np.pi * interference_hz * t + 0.1 * ch)
    raw[ch] = clean[ch] + interference + 0.0001 * rng.standard_normal(len(t))

processor = SignalProcessor(ConditioningConfig(fs=FS, cutoff_hz=4000.0, filter_order=4))
conditioned = processor.anti_aliasing_filter(raw.T).T

reference = np.sin(2 * np.pi * interference_hz * t)
lms = LMSFilter(order=ORDER, learning_rate=mu)
padded = np.concatenate((np.zeros(ORDER - 1), reference))
filtered = np.empty_like(conditioned[1])
for i, sample in enumerate(conditioned[1]):
    x = padded[i:i + ORDER][::-1]
    _, filtered[i], _ = lms.update(x, sample)

baseline_snr = snr_db(clean[1], conditioned[1])
output_snr = snr_db(clean[1], filtered)
mse = residual_mse(clean[1], filtered)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Channels", CHANNELS)
c2.metric("Sampling rate", f"{FS/1000:.0f} kHz")
c3.metric("CH2 output SNR", f"{output_snr:.2f} dB", f"{output_snr-baseline_snr:+.2f} dB")
c4.metric("Residual MSE", f"{mse:.6f} V²")

st.subheader(f"Channel {channel} acquisition")
stride = max(1, len(t) // 5000)
st.line_chart({"Raw": raw[channel, ::stride], "Conditioned": conditioned[channel, ::stride]})

st.subheader("CH2 adaptive interference cancellation")
st.line_chart({"Clean reference": clean[1, ::stride], "Before LMS": conditioned[1, ::stride], "After LMS": filtered[::stride]})

st.info("Software simulation only. The displayed measurements are not physical ADC or embedded-hardware validation results.")
