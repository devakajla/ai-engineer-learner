from solution import fits_on_gpu, model_memory_gb


def test_memory_for_common_sizes():
    assert model_memory_gb(7, 16) == 14
    assert model_memory_gb(7, 8) == 7
    assert model_memory_gb(7, 4) == 3.5
    assert model_memory_gb(70, 16) == 140


def test_fits_with_overhead():
    assert fits_on_gpu(7, 16, 24) is True      # 14 * 1.2 = 16.8
    assert fits_on_gpu(13, 16, 24) is False    # 26 * 1.2 = 31.2
    assert fits_on_gpu(13, 4, 24) is True      # 6.5 * 1.2 = 7.8


def test_exact_boundary_counts_as_fit():
    assert fits_on_gpu(10, 8, 12, overhead=1.2) is True    # 10 * 1.2 = 12.0


def test_custom_overhead():
    assert fits_on_gpu(7, 16, 16, overhead=1.0) is True
    assert fits_on_gpu(7, 16, 16, overhead=1.2) is False
