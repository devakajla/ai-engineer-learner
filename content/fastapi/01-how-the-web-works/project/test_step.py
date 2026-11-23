"""Step 1 checks. Runs with the current directory = the learner's project folder."""

import tomllib
from pathlib import Path

ROOT = Path.cwd()


def test_pyproject_has_fastapi():
    path = ROOT / "pyproject.toml"
    assert path.exists(), "pyproject.toml not found — run `uv init taskflow --app` in ~/Projects"
    deps = tomllib.loads(path.read_text()).get("project", {}).get("dependencies", [])
    assert any(d.lower().startswith("fastapi") for d in deps), "add FastAPI: `uv add \"fastapi[standard]\"`"


def test_app_package_exists():
    assert (ROOT / "app" / "__init__.py").exists(), "create the package: mkdir app && touch app/__init__.py"


def test_demo_main_removed():
    assert not (ROOT / "main.py").exists(), "delete the demo main.py at the project root (app code lives in app/)"


def test_gitignore():
    path = ROOT / ".gitignore"
    assert path.exists(), ".gitignore is missing"
    text = path.read_text()
    assert ".venv" in text, ".gitignore must ignore .venv"
    assert "__pycache__" in text, ".gitignore must ignore __pycache__"
    assert ".env" in text.replace(".venv", ""), ".gitignore must ignore .env (secrets)"


def test_readme_mentions_taskflow():
    path = ROOT / "README.md"
    assert path.exists(), "README.md is missing"
    assert "taskflow" in path.read_text().lower(), "README should describe TaskFlow"
