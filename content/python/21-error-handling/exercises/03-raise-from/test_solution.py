import json

import pytest

from solution import ConfigError, load_port


def test_ok():
    assert load_port('{"port": 8000}') == 8000


def test_invalid_json_chained():
    with pytest.raises(ConfigError, match="invalid JSON") as info:
        load_port("{oops")
    assert isinstance(info.value.__cause__, json.JSONDecodeError), "use `raise ... from e`"


def test_missing_port_chained():
    with pytest.raises(ConfigError, match="missing port") as info:
        load_port('{"host": "x"}')
    assert isinstance(info.value.__cause__, KeyError)


def test_invalid_port():
    for bad in ('{"port": 0}', '{"port": 70000}', '{"port": "80"}', '{"port": true}'):
        with pytest.raises(ConfigError, match="invalid port"):
            load_port(bad)
