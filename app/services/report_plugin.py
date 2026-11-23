"""Tiny pytest plugin: writes the failures as JSON so the UI can explain them.

Loaded into the test subprocess with `-p report_plugin` (the runner puts this folder
on PYTHONPATH). Standard library only, because project checkpoints run it inside
the learner's own environment. Path of the JSON file comes from LEARNER_REPORT.
"""

import json
import os
import re

_MAX_FAILURES = 5
_failures: list[dict] = []

_HINTS = {
    "ZeroDivisionError": "You divided by zero. Check the value of the divisor before dividing.",
    "NameError": "You used a name that does not exist yet. Check for a typo, or create the variable before using it.",
    "UnboundLocalError": "You used a variable before giving it a value inside the function.",
    "TypeError": "A value has the wrong type for this operation (for example str + int), or a function got the wrong number of arguments.",
    "IndexError": "You asked for a position that is not in the list. Check the length and your loop range.",
    "KeyError": "This key is not in the dict. Check the spelling, or use .get(key).",
    "AttributeError": "This object has no such method or attribute. Check the name and the type of the object.",
    "ValueError": "The value has the right type but a wrong content (for example int('abc')).",
    "RecursionError": "The function calls itself forever. Check the base case.",
    "SyntaxError": "Python cannot read this line. Look for a missing colon, bracket or quote.",
    "IndentationError": "The spaces at the start of a line are wrong. Use 4 spaces for each level.",
    "ImportError": "The function the tests need is missing. Check the name and signature in the prompt.",
    "ModuleNotFoundError": "A module could not be found. Check the import line.",
}


def _my_line(excinfo):
    """Last traceback frame inside the learner's solution.py: (line number, source text)."""
    value = excinfo.value
    if isinstance(value, SyntaxError) and value.lineno:
        return value.lineno, (value.text or "").strip()
    for entry in reversed(list(excinfo.traceback)):
        if entry.path.name == "solution.py":
            try:
                text = str(entry.statement).strip()
            except Exception:
                text = ""
            return entry.lineno + 1, text
    return None, ""


def _assertion_parts(value):
    """Split pytest's rewritten assert text into (message, got, expected)."""
    text = str(value)
    message, _, rest = text.partition("\nassert ")
    if not rest:  # no custom message: the text itself starts with "assert ..."
        message, rest = "", text[len("assert ") :] if text.startswith("assert ") else text
    got = expected = None
    m = re.match(r"(.+?) == (.+?)(?:\n|$)", rest)
    if m:
        got, expected = m.group(1), m.group(2)
    return message.strip(), got, expected


def _collect_error(text):
    """Collection errors (bad syntax, missing import) only arrive as text: pick out the useful parts."""
    errs = re.findall(r"^E\s+(\w+(?:Error|Exception|Exit)): (.*)$", text, re.M)
    exc, message = errs[-1] if errs else ("CollectError", "")
    line = source = None
    m = re.search(r'solution\.py", line (\d+)\n(?:E\s+(.*)\n)?', text) or re.search(r"solution\.py:(\d+): in", text)
    if m:
        line = int(m.group(1))
        if m.lastindex and m.lastindex >= 2 and m.group(2):
            source = m.group(2).strip()
    return exc, message, line, source or ""


def pytest_exception_interact(node, call, report):
    excinfo = call.excinfo
    if excinfo is None or len(_failures) >= _MAX_FAILURES:
        return
    exc = excinfo.type.__name__
    line, source = _my_line(excinfo)
    if exc == "CollectError":
        exc, message, line, source = _collect_error(str(excinfo.value))
        got = expected = None
        kind = "syntax" if exc in ("SyntaxError", "IndentationError", "TabError") else (
            "import" if exc in ("ImportError", "ModuleNotFoundError") else "exception"
        )
    elif exc == "AssertionError":
        message, got, expected = _assertion_parts(excinfo.value)
        kind = "assertion"
    else:
        message, got, expected = str(excinfo.value), None, None
        kind = "syntax" if exc in ("SyntaxError", "IndentationError", "TabError") else (
            "import" if exc in ("ImportError", "ModuleNotFoundError") else "exception"
        )
    _failures.append(
        {
            "test": node.name,
            "kind": kind,
            "exc_type": exc,
            "message": message,
            "got": got,
            "expected": expected,
            "line": line,
            "source": source,
            "hint": _HINTS.get(exc, ""),
        }
    )


def pytest_sessionfinish(session):
    path = os.environ.get("LEARNER_REPORT")
    if path:
        with open(path, "w") as f:
            json.dump(_failures, f)
