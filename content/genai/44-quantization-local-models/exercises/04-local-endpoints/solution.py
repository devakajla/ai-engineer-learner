BASE_URLS = {
    "ollama": "http://localhost:11434/v1",
    "vllm": "http://localhost:8000/v1",
    "groq": "https://api.groq.com/openai/v1",
}


def base_url(runner):
    if runner not in BASE_URLS:
        raise ValueError(f"unknown runner: {runner}")
    return BASE_URLS[runner]


def chat_request(runner, model, prompt):
    return {
        "url": base_url(runner) + "/chat/completions",
        "json": {"model": model, "messages": [{"role": "user", "content": prompt}]},
    }


def request_headers(runner, api_key=None):
    headers = {"Content-Type": "application/json"}
    if runner == "groq":
        if not api_key:
            raise ValueError("groq needs an api key")
        headers["Authorization"] = "Bearer " + api_key
    return headers
