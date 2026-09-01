import numpy as np

from dsp.signal_processor import ConditioningConfig, SignalProcessor


def test_adc_step_matches_16bit_pm10v_range():
    cfg = ConditioningConfig(adc_bits=16, adc_min=-10.0, adc_max=10.0)
    expected = 20.0 / (2**16 - 1)
    assert np.isclose(cfg.quantization_step, expected)


def test_quantizer_clips_to_adc_range():
    processor = SignalProcessor()
    x = np.array([-20.0, -10.0, 0.0, 10.0, 20.0])
    y = processor.quantize(x)
    assert np.all(y >= -10.0)
    assert np.all(y <= 10.0)
    assert np.isclose(y[0], -10.0)
    assert np.isclose(y[-1], 10.0)


def test_butterworth_cutoff_is_about_minus_3db():
    processor = SignalProcessor(ConditioningConfig(fs=50_000.0, cutoff_hz=4_000.0, filter_order=4))
    f, h = processor.filter_response(worN=16384)
    idx = np.argmin(np.abs(f - 4_000.0))
    gain_db = 20.0 * np.log10(np.abs(h[idx]))
    assert -3.2 < gain_db < -2.8


def test_10khz_is_strongly_attenuated():
    processor = SignalProcessor(ConditioningConfig(fs=50_000.0, cutoff_hz=4_000.0, filter_order=4))
    f, h = processor.filter_response(worN=16384)
    idx = np.argmin(np.abs(f - 10_000.0))
    gain_db = 20.0 * np.log10(np.abs(h[idx]))
    assert gain_db < -30.0


def test_downsample_halves_sample_count():
    processor = SignalProcessor()
    x = np.sin(2 * np.pi * 1000 * np.arange(5000) / 50_000.0)
    y = processor.downsample(x, factor=2)
    assert len(y) == 2500


def test_normalize_sets_requested_peak():
    processor = SignalProcessor()
    x = np.array([-2.0, 0.5, 1.0])
    y = processor.normalize(x, peak=1.0)
    assert np.isclose(np.max(np.abs(y)), 1.0)
