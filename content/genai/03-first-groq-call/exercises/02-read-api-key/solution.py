def read_api_key(env):
    key = env.get("GROQ_API_KEY", "").strip()
    if not key:
        raise ValueError("GROQ_API_KEY is not set")
    return key
