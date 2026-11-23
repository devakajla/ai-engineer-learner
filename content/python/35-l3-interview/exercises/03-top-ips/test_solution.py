import pytest

from solution import top_ips


def test_basic():
    assert top_ips(["1.1.1.1 GET /", "2.2.2.2 GET /", "1.1.1.1 GET /a", ""], 1) == [("1.1.1.1", 2)]


def test_ties_sorted_by_ip():
    assert top_ips(["b GET /", "a GET /"], 2) == [("a", 1), ("b", 1)]


def test_fewer_ips_than_k():
    assert top_ips(["a x", "a y"], 5) == [("a", 2)]


def test_empty_and_blank():
    assert top_ips([], 3) == []
    assert top_ips(["", "   "], 3) == []


def test_bad_k():
    with pytest.raises(ValueError):
        top_ips(["a x"], 0)


def test_reads_a_generator_once_without_a_list():
    read = []

    def lines():
        for i in range(200_000):
            read.append(1)
            yield f"10.0.0.{i % 50} GET /page/{i}"

    out = top_ips(lines(), 3)
    assert len(read) == 200_000
    assert out == [("10.0.0.0", 4000), ("10.0.0.1", 4000), ("10.0.0.10", 4000)]


def test_order_by_count_then_ip():
    data = ["c x"] * 3 + ["a x"] * 3 + ["b x"] * 5
    assert top_ips(iter(data), 3) == [("b", 5), ("a", 3), ("c", 3)]
