import json


class ConfigError(Exception):
    pass


def load_port(text: str) -> int:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ConfigError("invalid JSON") from e
    try:
        port = data["port"]
    except KeyError as e:
        raise ConfigError("missing port") from e
    if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
        raise ConfigError("invalid port")
    return port
