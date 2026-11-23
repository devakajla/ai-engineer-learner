import pytest

from solution import base_url, chat_request, request_headers


def test_base_urls():
    assert base_url("ollama") == "http://localhost:11434/v1"
    assert base_url("vllm") == "http://localhost:8000/v1"
    assert base_url("groq") == "https://api.groq.com/openai/v1"


def test_unknown_runner_raises():
    with pytest.raises(ValueError, match="unknown runner: banana"):
        base_url("banana")


def test_chat_request_has_the_same_shape_for_every_runner():
    for runner, model in [("ollama", "llama3.2"), ("vllm", "my-model"), ("groq", "qwen/qwen3.8-27b")]:
        req = chat_request(runner, model, "Hi")
        assert req["url"] == base_url(runner) + "/chat/completions"
        assert req["json"] == {"model": model, "messages": [{"role": "user", "content": "Hi"}]}


def test_local_runners_need_no_key():
    assert request_headers("ollama") == {"Content-Type": "application/json"}
    assert request_headers("vllm", "ignored") == {"Content-Type": "application/json"}


def test_groq_needs_a_bearer_key():
    assert request_headers("groq", "abc") == {"Content-Type": "application/json", "Authorization": "Bearer abc"}
    for bad in (None, ""):
        with pytest.raises(ValueError, match="groq needs an api key"):
            request_headers("groq", bad)
