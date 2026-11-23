import re
import tomllib


def _name(requirement):
    return re.split(r"[<>=!~;\[ ]", requirement.strip())[0]


def read_project(text):
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"invalid TOML: {error}") from error
    project = data.get("project")
    if not isinstance(project, dict) or "name" not in project:
        raise ValueError("pyproject.toml needs a [project] section with a name")
    dev = data.get("dependency-groups", {}).get("dev", [])
    return {
        "name": project["name"],
        "version": project.get("version", "0.0.0"),
        "requires_python": project.get("requires-python", ""),
        "dependencies": [_name(r) for r in project.get("dependencies", [])],
        "dev_dependencies": [_name(r) for r in dev],
    }
