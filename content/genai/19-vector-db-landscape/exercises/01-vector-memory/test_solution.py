import pytest

from solution import vector_memory_mb


def test_examples():
    assert vector_memory_mb(1_000_000, 384) == 1536.0
    assert vector_memory_mb(100_000, 768) == 307.2
    assert vector_memory_mb(1_000_000, 384, 1) == 384.0
    assert vector_memory_mb(0, 384) == 0.0


def test_rounding_and_size():
    assert vector_memory_mb(1, 384) == 0.0, "1536 bytes is 0.001536 MB, which rounds to 0.0"
    assert vector_memory_mb(5_000_000, 768) == 15360.0
    assert vector_memory_mb(333, 7, 4) == 0.01


def test_negative_numbers():
    for args in [(-1, 384, 4), (10, -1, 4), (10, 384, -4)]:
        with pytest.raises(ValueError):
            vector_memory_mb(*args)
