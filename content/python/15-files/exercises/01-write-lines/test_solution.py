from pathlib import Path

from solution import write_lines


def test_examples(tmp_path):
    p = tmp_path / "out.txt"
    write_lines(p, ["a", "b"])
    assert p.read_text(encoding="utf-8") == "a\nb\n"
    q = tmp_path / "empty.txt"
    write_lines(str(q), [])
    assert q.read_text(encoding="utf-8") == ""


def test_overwrites(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text("old old old\n", encoding="utf-8")
    write_lines(p, ["new"])
    assert p.read_text(encoding="utf-8") == "new\n", "old content must be replaced"
