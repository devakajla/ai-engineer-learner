import json
from pathlib import Path


def load_config(path, defaults):
    config = dict(defaults)
    p = Path(path)
    if p.exists():
        config.update(json.loads(p.read_text(encoding="utf-8")))
    return config
