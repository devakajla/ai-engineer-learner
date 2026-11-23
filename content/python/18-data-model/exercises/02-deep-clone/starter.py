def make_env_config(base, env):
    config = base.copy()
    config["env"] = env
    if env == "prod":
        config["db"]["host"] = "db.internal"
        config["features"].append("metrics")
    return config
