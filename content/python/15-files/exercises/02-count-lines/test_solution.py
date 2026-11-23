from solution import count_lines


def test_examples(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("a\n\nb\n   \nc", encoding="utf-8")
    assert count_lines(p) == 3


def test_more(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("", encoding="utf-8")
    assert count_lines(p) == 0
    q = tmp_path / "one.txt"
    q.write_text("hello\n", encoding="utf-8")
    assert count_lines(str(q)) == 1
