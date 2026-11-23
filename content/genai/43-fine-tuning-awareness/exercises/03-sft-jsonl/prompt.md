# Training data for fine-tuning (SFT)

**SFT** (supervised fine-tuning) teaches a model from examples of the form "for this input, give this answer". The usual file format is **JSONL**: one JSON object per line. Chat models use a `messages` list, like the API. Bad data teaches bad habits, so you **check every line** before you pay for training.

Write two functions (use the `json` module):

1. `to_jsonl_line(system, user, assistant)`: return `json.dumps({"messages": [...]})` with a `system` message (only if `system` is not empty), then the `user` message, then the `assistant` message. Each message is `{"role": ..., "content": ...}`.
2. `check_example(line)`: return a list of problem strings (an empty list means the line is fine). Test in this order:
   - the line is not valid JSON: return `["not valid JSON"]` right away.
   - there is no non-empty `"messages"` list (or the JSON is not a dict): return `["no messages list"]` right away.
   - then collect, in this order: `"no user message"` if no message has role `user`; `"last message must be from the assistant"` if the last role is not `assistant`; and for every message with empty or blank content, `"empty <role> message"`.

```python
to_jsonl_line("Be short.", "Hi", "Hello!")
# -> '{"messages": [{"role": "system", "content": "Be short."}, {"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello!"}]}'
check_example('{"text": "hi"}')
# -> ['no messages list']
```

**Think first:** why check the **last** role? What does the model learn if the last message is a user message?

**Hint:** use `m.get("role")` and `str(m.get("content", "")).strip()` to stay safe with odd data.
