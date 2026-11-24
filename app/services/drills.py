"""Mini drills for a weak topic: Claude writes them, the server checks them for real.

Claude gives a reference `solution` and a list of `calls` (expressions such as `next_word("I", table)`).
The server runs the solution on the calls and stores what it returned as the expected answers, so a wrong
expected value from Claude cannot happen. Dev's code is checked by running the same calls.
The solution and the expected values never go to the browser.
"""

from __future__ import annotations

import json
import re

from app.services.runner import run_script

_MARK = "@@RESULT@@"
_MAX_REPR = 300

_HARNESS = """

import json as _json
_calls = _json.loads({calls})
_out = []
for _c in _calls:
    try:
        _out.append({{"ok": True, "repr": repr(eval(_c))}})
    except BaseException as _e:
        _out.append({{"ok": False, "repr": type(_e).__name__ + ": " + str(_e)}})
print("{mark}" + _json.dumps(_out))
"""


async def run_calls(code: str, calls: list[str], timeout: float = 5) -> tuple[list[dict] | None, str]:
    """Run `code`, then evaluate each call. Returns (results or None, error text)."""
    script = code + _HARNESS.format(calls=repr(json.dumps(calls)), mark=_MARK)
    r = await run_script(script, timeout=timeout)
    if r.timed_out:
        return None, r.stderr
    for line in r.stdout.splitlines():
        if line.startswith(_MARK):
            return json.loads(line[len(_MARK) :]), ""
    return None, r.stderr.strip() or "The code did not finish."


def parse_drills_json(text: str) -> list[dict]:
    """Claude's reply holds a JSON array (maybe inside a ``` fence). Returns [] if it cannot be read."""
    text = re.sub(r"```(?:json)?", "", text)
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end <= start:
        return []
    try:
        data = json.loads(text[start : end + 1])
    except ValueError:
        return []
    return [d for d in data if isinstance(d, dict)] if isinstance(data, list) else []


async def validate(raw: dict) -> dict | None:
    """Keep a drill only if its solution runs and gives short answers for every call."""
    try:
        title, prompt, starter, solution = (str(raw[k]).strip() for k in ("title", "prompt", "starter", "solution"))
        calls = [str(c).strip() for c in raw["calls"]]
        name = str(raw.get("function_name", "")).strip()
    except (KeyError, TypeError):
        return None
    if not (title and prompt and starter and solution) or not 2 <= len(calls) <= 6 or len(calls) != len(set(calls)):
        return None
    if starter == solution or (name and f"def {name}" not in starter):
        return None
    results, _ = await run_calls(solution, calls)
    if not results or len(results) != len(calls):
        return None
    if any(not x["ok"] or len(x["repr"]) > _MAX_REPR for x in results):
        return None
    return {
        "title": title[:80], "prompt": prompt, "starter": starter, "solution": solution,
        "calls": calls, "expected": [x["repr"] for x in results],
    }  # fmt: skip


async def check(code: str, calls: list[str], expected: list[str]) -> dict:
    results, error = await run_calls(code, calls)
    if results is None:
        return {"passed": False, "results": [], "error": error}
    out = []
    for call, want, got in zip(calls, expected, results, strict=True):
        ok = got["ok"] and got["repr"] == want
        out.append({"call": call, "ok": ok, "got": got["repr"], "want": None if ok else want})
    return {"passed": all(r["ok"] for r in out), "results": out, "error": ""}
