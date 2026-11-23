BASE_URLS = {
    "ollama": "http://localhost:11434/v1",
    "vllm": "http://localhost:8000/v1",
    "groq": "https://api.groq.com/openai/v1",
}


def base_url(runner):
    ...


def chat_request(runner, model, prompt):
    ...


def request_headers(runner, api_key=None):
    ...
