import json
import os

DEFAULTS = {"debug": False, "port": 8000, "name": "app"}


def load_settings(path):
    settings = dict(DEFAULTS)
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as error:
            raise ValueError(f"settings file is not valid JSON: {error}") from error
        if not isinstance(data, dict):
            raise ValueError("settings file must contain a JSON object")
        settings.update(data)
    port = os.environ.get("APP_PORT")
    if port is not None:
        try:
            settings["port"] = int(port)
        except ValueError:
            raise ValueError(f"APP_PORT must be a whole number, got {port!r}") from None
    return settings
