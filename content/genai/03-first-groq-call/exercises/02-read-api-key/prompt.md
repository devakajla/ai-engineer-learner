# Read the API key safely

Write `read_api_key(env)`. `env` is a dictionary of environment variables (like `os.environ`).

Return the value of `"GROQ_API_KEY"` without spaces around it.

Rules:
- If the key is missing, raise `ValueError` with the message `"GROQ_API_KEY is not set"`.
- If the key is only spaces or an empty string, raise the same error.
- Never print the key.

```python
read_api_key({"GROQ_API_KEY": " gsk_abc "})   # -> 'gsk_abc'
read_api_key({})                              # raises ValueError: GROQ_API_KEY is not set
read_api_key({"GROQ_API_KEY": "   "})         # raises ValueError: GROQ_API_KEY is not set
```
