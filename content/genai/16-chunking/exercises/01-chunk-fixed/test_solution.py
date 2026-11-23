import pytest

from solution import chunk_fixed


def test_examples():
    assert chunk_fixed("abcdefghij", 4) == ["abcd", "efgh", "ij"]
    assert chunk_fixed("abcdefghij", 4, 1) == ["abcd", "defg", "ghij"]
    assert chunk_fixed("abc", 10) == ["abc"]
    assert chunk_fixed("", 4) == []


def test_exact_fit_has_no_extra_chunk():
    assert chunk_fixed("abcdefgh", 4) == ["abcd", "efgh"]
    assert chunk_fixed("abcdefgh", 4, 2) == ["abcd", "cdef", "efgh"], "no trailing chunk of already-seen text"


def test_every_character_is_covered():
    text = "the quick brown fox jumps over the lazy dog"
    for size, overlap in [(5, 0), (7, 3), (10, 9), (1, 0)]:
        chunks = chunk_fixed(text, size, overlap)
        assert chunks[0].startswith(text[:1]) and text.endswith(chunks[-1])
        assert all(0 < len(c) <= size for c in chunks)


def test_bad_values():
    for size, overlap in [(0, 0), (-1, 0), (4, -1), (4, 4), (4, 9)]:
        with pytest.raises(ValueError):
            chunk_fixed("abcdef", size, overlap)
