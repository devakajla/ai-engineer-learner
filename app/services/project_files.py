"""Collects a snapshot of the learner's project (folder tree + source files) for Claude to review."""

from pathlib import Path

SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", ".idea", ".vscode"}
TEXT_SUFFIXES = {".py", ".toml", ".md", ".txt", ".cfg", ".ini", ".yaml", ".yml", ".example", ".sql"}
TEXT_NAMES = {".gitignore", "Dockerfile", ".dockerignore", ".env.example", "Makefile", "alembic.ini"}
# Never send these contents (they may hold secrets); they are still listed in the tree.
SECRET_NAMES = {".env", ".env.local", ".env.prod"}

MAX_FILE_CHARS = 6_000
MAX_TOTAL_CHARS = 60_000


def _walk(root: Path):
    for p in sorted(root.iterdir(), key=lambda x: (x.is_file(), x.name)):
        if p.is_dir():
            if p.name in SKIP_DIRS or p.name.endswith(".egg-info"):
                continue
            yield p
            yield from _walk(p)
        else:
            yield p


def snapshot(root: Path) -> str:
    """A text tree of the project followed by the contents of its source files."""
    if not root.is_dir():
        return f"(project folder {root} does not exist)"
    paths = list(_walk(root))
    tree = [f"{root.name}/"]
    for p in paths:
        rel = p.relative_to(root)
        tree.append("  " * (len(rel.parts) - 1) + "- " + p.name + ("/" if p.is_dir() else ""))

    parts = ["<tree>\n" + "\n".join(tree[:400]) + "\n</tree>"]
    total = 0
    for p in paths:
        if not p.is_file() or p.name in SECRET_NAMES or p.name == "uv.lock":
            continue
        if p.suffix not in TEXT_SUFFIXES and p.name not in TEXT_NAMES:
            continue
        text = p.read_text(errors="replace")
        if len(text) > MAX_FILE_CHARS:
            text = text[:MAX_FILE_CHARS] + "\n... (truncated)"
        if total + len(text) > MAX_TOTAL_CHARS:
            parts.append("(more files omitted: size limit)")
            break
        total += len(text)
        parts.append(f'<file path="{p.relative_to(root)}">\n{text}\n</file>')
    return "\n\n".join(parts)
