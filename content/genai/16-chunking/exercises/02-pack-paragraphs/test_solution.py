import pytest

from solution import pack_paragraphs


def test_examples():
    text = "aa\n\nbb\n\ncc\n\ndd"
    assert pack_paragraphs(text, 8) == ["aa\n\nbb", "cc\n\ndd"]
    assert pack_paragraphs(text, 100) == ["aa\n\nbb\n\ncc\n\ndd"]
    assert pack_paragraphs("a long paragraph here\n\nhi", 5) == ["a long paragraph here", "hi"]
    assert pack_paragraphs("  \n\n  ", 5) == []


def test_exact_limit_fits_and_one_more_does_not():
    assert pack_paragraphs("aa\n\nbb", 6) == ["aa\n\nbb"], "length 6 equals the limit, so it fits"
    assert pack_paragraphs("aa\n\nbb", 5) == ["aa", "bb"]


def test_strip_and_blank_lines():
    assert pack_paragraphs("  one \n\n\n\n two  ", 100) == ["one\n\ntwo"]
    assert pack_paragraphs("", 10) == []


def test_last_chunk_is_not_lost_and_order_is_kept():
    text = "\n\n".join(["p1", "p2", "p3", "p4", "p5"])
    chunks = pack_paragraphs(text, 4)
    assert chunks == ["p1", "p2", "p3", "p4", "p5"]
    assert "\n\n".join(chunks) == text


def test_bad_limit():
    with pytest.raises(ValueError):
        pack_paragraphs("a", 0)
