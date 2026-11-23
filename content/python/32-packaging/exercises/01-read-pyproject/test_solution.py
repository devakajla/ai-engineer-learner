import pytest

from solution import read_project

FULL = """
[project]
name = "taskflow"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["fastapi>=0.110,<1.0", "httpx", "uvicorn[standard]>=0.30"]

[dependency-groups]
dev = ["pytest>=8", "ruff"]
"""


def test_full():
    assert read_project(FULL) == {
        "name": "taskflow",
        "version": "0.1.0",
        "requires_python": ">=3.12",
        "dependencies": ["fastapi", "httpx", "uvicorn"],
        "dev_dependencies": ["pytest", "ruff"],
    }


def test_defaults():
    out = read_project('[project]\nname = "app"\n')
    assert out == {
        "name": "app",
        "version": "0.0.0",
        "requires_python": "",
        "dependencies": [],
        "dev_dependencies": [],
    }


def test_example_from_prompt():
    text = '[project]\nname = "app"\nversion = "1.2.0"\ndependencies = ["fastapi>=0.110", "httpx"]\n'
    out = read_project(text)
    assert out["dependencies"] == ["fastapi", "httpx"]


def test_missing_project_section():
    with pytest.raises(ValueError):
        read_project('[tool.x]\na = 1\n')


def test_missing_name():
    with pytest.raises(ValueError):
        read_project('[project]\nversion = "1.0"\n')


def test_invalid_toml():
    with pytest.raises(ValueError):
        read_project("this is = = not toml")
