import pytest

from solution import dequantize, max_error, quantize


def test_quantize_maps_the_biggest_value_to_127():
    quantized, scale = quantize([12.7, -12.7, 0.0, 3.0])
    assert quantized == [127, -127, 0, 30]
    assert scale == pytest.approx(0.1)


def test_all_numbers_fit_in_one_signed_byte():
    quantized, _ = quantize([0.3, -7.1, 2.2, 100.0, -55.5])
    assert all(-127 <= q <= 127 for q in quantized)
    assert all(isinstance(q, int) for q in quantized)


def test_dequantize_multiplies_back():
    assert dequantize([127, -127, 0, 30], 0.1) == pytest.approx([12.7, -12.7, 0.0, 3.0])


def test_round_trip_error_is_at_most_half_a_step():
    values = [0.11, -0.52, 0.9, 0.333, -0.07]
    _, scale = quantize(values)
    assert max_error(values) <= scale / 2 + 1e-12


def test_all_zeros_and_empty_list_do_not_crash():
    assert quantize([0.0, 0.0]) == ([0, 0], 1.0)
    assert quantize([]) == ([], 1.0)
    assert max_error([0.0, 0.0]) == 0.0
    assert max_error([]) == 0.0


def test_one_huge_value_hurts_the_small_ones():
    small_only = max_error([0.01, 0.02, -0.03])
    with_outlier = max_error([0.01, 0.02, -0.03, 100.0])
    assert with_outlier > 100 * small_only, "an outlier makes the scale big, so small values lose detail"
