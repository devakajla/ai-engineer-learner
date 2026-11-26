"""The Python tools an exercise needs, read from its reference solution with `ast`.

Shown in the Practice tab as "Tools you will need". It names the tools and links each one to the Python lesson
that teaches it. It never shows any code of the solution.

Only the functions the learner must write are read: functions that the starter already gives with a real body
("given" code from earlier exercises) are skipped, and calls to them become "Use the given function X".
"""

from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path

from app.content import Exercise, get_tracks

# tool key -> (plain name, lesson id that teaches it)
TOOLS: dict[str, tuple[str, str]] = {
    "if": ("if / elif / else to choose a path", "python/06-conditionals"),
    "compare": ("Comparisons and `and` / `or` / `not`", "python/05-booleans-operators"),
    "in": ("`in` to check if something is inside a list, dict or string", "python/05-booleans-operators"),
    "for": ("A `for` loop over a list", "python/07-loops"),
    "while": ("A `while` loop", "python/07-loops"),
    "range": ("`range()` to count", "python/07-loops"),
    "enumerate": ("`enumerate()` to get the position and the item", "python/07-loops"),
    "list": ("Make a list with `[...]`", "python/08-lists"),
    "append": ("Add to a list with `.append()`", "python/08-lists"),
    "index": ("Get one item with `[n]` or `[key]`", "python/08-lists"),
    "slice": ("Take a part with slicing `[a:b]`", "python/08-lists"),
    "len": ("`len()` to count items", "python/08-lists"),
    "sorted": ("`sorted()` / `.sort()`", "python/08-lists"),
    "tuple": ("Tuples and unpacking `a, b = ...`", "python/09-tuples"),
    "set": ("Sets for 'seen' and unique items", "python/10-sets"),
    "dict": ("Make a dictionary with `{key: value}`", "python/11-dicts"),
    "dict_get": ("`.get(key, default)` on a dictionary", "python/11-dicts"),
    "dict_loop": ("`.items()` / `.keys()` / `.values()` on a dictionary", "python/11-dicts"),
    "comprehension": ("A comprehension `[x for x in ...]`", "python/12-comprehensions"),
    "string_methods": ("String methods (`.strip()`, `.split()`, `.join()`, ...)", "python/04-strings"),
    "fstring": ("f-strings `f\"...{x}...\"`", "python/04-strings"),
    "numbers": ("Number helpers (`min`, `max`, `sum`, `round`, `abs`, `//`, `%`)", "python/03-numbers-casting"),
    "cast": ("Change a type with `int()`, `str()`, `float()`", "python/03-numbers-casting"),
    "isinstance": ("`isinstance()` to check a type", "python/02-variables-types"),
    "default_args": ("Default argument values `def f(x, y=1)`", "python/13-functions"),
    "helper_def": ("Write a small helper function", "python/13-functions"),
    "try": ("`try` / `except` to catch an error", "python/16-exceptions-basics"),
    "raise": ("`raise ValueError(...)` to stop with an error", "python/16-exceptions-basics"),
    "import": ("`import` a module", "python/14-modules"),
    "with_open": ("`with open(...)` to read or write a file", "python/15-files"),
    "lambda": ("`lambda` for a short `key=` function", "python/25-functional-tools"),
    "attr_chain": ("Read a value inside an object with a dot: `obj.part`", "genai/03-first-groq-call"),
    "method_call": ("Call a method on an object: `obj.method(...)`", "genai/03-first-groq-call"),
    "class": ("A small class", "python/19-classes"),
}

STRING_METHODS = {
    "strip", "lstrip", "rstrip", "split", "join", "lower", "upper", "replace", "startswith", "endswith",
    "find", "splitlines", "title", "isdigit", "isalpha", "count", "format",
}
DICT_LOOP = {"items", "keys", "values"}
NUMBER_FUNCS = {"min", "max", "sum", "round", "abs"}
CASTS = {"int", "str", "float", "bool", "list", "dict", "set", "tuple"}


def _is_stub(fn: ast.FunctionDef) -> bool:
    """True when the body is only a docstring and `...` / `pass`."""
    for stmt in fn.body:
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):  # `...` or a docstring
            continue
        return False
    return True


def _given_functions(starter: str) -> set[str]:
    try:
        tree = ast.parse(starter)
    except SyntaxError:
        return set()
    return {n.name for n in tree.body if isinstance(n, ast.FunctionDef) and not _is_stub(n)}


class _Finder(ast.NodeVisitor):
    def __init__(self, given: set[str]):
        self.given = given
        self.found: list[str] = []  # tool keys, in the order they first appear
        self.uses_given: list[str] = []
        self._depth = 0  # how deep inside a function we are
        self._call_funcs: set[int] = set()  # ids of `obj.method` nodes that are called

    def add(self, key: str) -> None:
        if key not in self.found:
            self.found.append(key)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._depth:
            self.add("helper_def")
        if node.args.defaults or node.args.kw_defaults:
            self.add("default_args")
        self._depth += 1
        self.generic_visit(node)
        self._depth -= 1

    def visit_If(self, node):
        self.add("if"); self.generic_visit(node)

    def visit_IfExp(self, node):
        self.add("if"); self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.add("compare"); self.generic_visit(node)

    def visit_Compare(self, node):
        if any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops):
            self.add("in")
        else:
            self.add("compare")
        self.generic_visit(node)

    def visit_For(self, node):
        self.add("for")
        if isinstance(node.target, ast.Tuple):
            self.add("tuple")
        self.generic_visit(node)

    def visit_While(self, node):
        self.add("while"); self.generic_visit(node)

    def visit_List(self, node):
        self.add("list"); self.generic_visit(node)

    def visit_Tuple(self, node):
        if isinstance(node.ctx, ast.Store):
            self.add("tuple")
        self.generic_visit(node)

    def visit_Set(self, node):
        self.add("set"); self.generic_visit(node)

    def visit_Dict(self, node):
        self.add("dict"); self.generic_visit(node)

    def visit_ListComp(self, node):
        self.add("comprehension"); self.generic_visit(node)

    visit_SetComp = visit_DictComp = visit_GeneratorExp = visit_ListComp

    def visit_Subscript(self, node):
        self.add("slice" if isinstance(node.slice, ast.Slice) else "index")
        self.generic_visit(node)

    def visit_JoinedStr(self, node):
        self.add("fstring"); self.generic_visit(node)

    def visit_Try(self, node):
        self.add("try"); self.generic_visit(node)

    def visit_Raise(self, node):
        self.add("raise"); self.generic_visit(node)

    def visit_Import(self, node):
        self.add("import"); self.generic_visit(node)

    visit_ImportFrom = visit_Import

    def visit_With(self, node):
        self.add("with_open"); self.generic_visit(node)

    def visit_Lambda(self, node):
        self.add("lambda"); self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.add("class"); self.generic_visit(node)

    def visit_BinOp(self, node):
        if isinstance(node.op, (ast.FloorDiv, ast.Mod)):
            self.add("numbers")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Load) and id(node) not in self._call_funcs:
            self.add("attr_chain")
        self.generic_visit(node)

    def visit_Call(self, node):
        f = node.func
        if isinstance(f, ast.Name):
            name = f.id
            if name in self.given:
                if name not in self.uses_given:
                    self.uses_given.append(name)
            elif name in ("range", "enumerate", "len", "sorted", "isinstance"):
                self.add(name)
            elif name in NUMBER_FUNCS:
                self.add("numbers")
            elif name in CASTS and name in ("set",):
                self.add("set")
            elif name in CASTS:
                self.add("cast")
        elif isinstance(f, ast.Attribute):
            self._call_funcs.add(id(f))
            m = f.attr
            if m == "append" or m == "extend":
                self.add("append")
            elif m == "get":
                self.add("dict_get")
            elif m in DICT_LOOP:
                self.add("dict_loop")
            elif m == "sort":
                self.add("sorted")
            elif m in STRING_METHODS:
                self.add("string_methods")
            else:
                self.add("method_call")
        self.generic_visit(node)


def _known_lessons() -> set[str]:
    return {r.id for t in get_tracks().values() for r in t.lessons if r.available}


@lru_cache(maxsize=2048)
def _tools(solution_path: str, mtime: float, starter: str) -> tuple[tuple[str, str | None], ...]:
    try:
        tree = ast.parse(Path(solution_path).read_text())
    except (OSError, SyntaxError):
        return ()
    given = _given_functions(starter)
    finder = _Finder(given)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in given:
            continue  # given code: the learner does not write it
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)):
            finder.visit(node)
    known = _known_lessons()
    out = [(f"Use the given function `{name}()`", None) for name in finder.uses_given]
    for key in finder.found:
        name, lesson_id = TOOLS[key]
        out.append((name, lesson_id if lesson_id in known else None))
    return tuple(out)


def tools_needed(exercise: Exercise) -> list[dict]:
    """[{name, lesson_id}] for one exercise; lesson_id is None when no written lesson teaches it."""
    path = exercise.dir / "solution.py"
    if not path.exists():
        return []
    return [
        {"name": name, "lesson_id": lid}
        for name, lid in _tools(str(path), path.stat().st_mtime, exercise.starter)
    ]
