# Same request, different server

**Ollama** (easy local runner) and **vLLM** (fast server for GPUs) both offer an **OpenAI-compatible API**. That is the same `/chat/completions` request that Groq uses. So moving between a hosted model and a local one is mostly a change of **base URL** (and sometimes a key). This is a big reason to wrap your model calls in one small function.

You build the request as plain data (no network). Write (`BASE_URLS` is given in the starter):

1. `base_url(runner)`: the base URL from `BASE_URLS` for `"ollama"`, `"vllm"` or `"groq"`. Any other name raises `ValueError(f"unknown runner: {runner}")`.
2. `chat_request(runner, model, prompt)`: return `{"url": base_url(runner) + "/chat/completions", "json": {"model": model, "messages": [{"role": "user", "content": prompt}]}}`.
3. `request_headers(runner, api_key=None)`: start with `{"Content-Type": "application/json"}`. For `"groq"` add `"Authorization": "Bearer " + api_key` (raise `ValueError("groq needs an api key")` if the key is missing or empty). Local runners need no key.

```python
chat_request("ollama", "llama3.2", "Hi")["url"]
# -> 'http://localhost:11434/v1/chat/completions'
```

(The ports are the usual defaults, from memory. Check the docs of each tool.)

**Think first:** what would you have to change in your app to move one feature from Groq to a local model?

**Hint:** the key must never be in the code. In real use you read it from `GROQ_API_KEY`.
