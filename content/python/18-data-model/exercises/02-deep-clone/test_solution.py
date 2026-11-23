from solution import make_env_config


def base():
    return {"db": {"host": "localhost", "port": 5432}, "features": ["auth"]}


def test_prod():
    b = base()
    prod = make_env_config(b, "prod")
    assert prod == {"db": {"host": "db.internal", "port": 5432}, "features": ["auth", "metrics"], "env": "prod"}
    assert b == base(), "base must not be modified (shallow copy shares nested dict/list)"


def test_dev():
    b = base()
    dev = make_env_config(b, "dev")
    assert dev["env"] == "dev" and dev["db"]["host"] == "localhost"
    assert "env" not in b


def test_outputs_independent():
    b = base()
    one = make_env_config(b, "dev")
    two = make_env_config(b, "dev")
    one["features"].append("x")
    assert two["features"] == ["auth"]
