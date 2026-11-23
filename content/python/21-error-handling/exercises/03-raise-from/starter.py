import json


class ConfigError(Exception):
    pass


def load_port(text):
    try:
        return json.loads(text)["port"]
    except Exception:
        raise ConfigError("bad config")
