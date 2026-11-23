import json

from solution import load_config


def test_examples(tmp_path):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({"port": 9000}), encoding="utf-8")
    assert load_config(p, {"port": 8000, "debug": False}) == {"port": 9000, "debug": False}
    assert load_config(tmp_path / "missing.json", {"port": 8000}) == {"port": 8000}


def test_defaults_untouched(tmp_path):
    defaults = {"a": 1}
    p = tmp_path / "c.json"
    p.write_text('{"a": 2, "b": 3}', encoding="utf-8")
    result = load_config(str(p), defaults)
    assert result == {"a": 2, "b": 3}
    assert defaults == {"a": 1}, "do not change defaults"
    missing = load_config(tmp_path / "nope.json", defaults)
    assert missing == defaults and missing is not defaults, "return a copy"
