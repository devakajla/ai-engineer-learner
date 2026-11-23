# A mini eval

Changing a prompt is a guess until you **measure**. A mini eval is a small set of test cases, each with a simple check. You run the prompt on all cases and count how many pass.

`ask_model(client, system, text)` is in the starter: it sends one call and returns the reply text. Write `run_eval(client, system, cases)`.

Each case is a dictionary:
- `"input"`: the text to send.
- `"must_include"` (optional): words that must appear in the reply.
- `"must_not_include"` (optional): words that must not appear.

Rules:
- For each case call `ask_model(client, system, case["input"])`.
- Checks are **not** case sensitive.
- A case passes when **all** `must_include` words appear and **no** `must_not_include` word appears. A missing key means no words.
- Return `{"passed": n, "total": n, "rate": passed / total rounded to 4 places, "failed": [inputs of the failed cases, in order]}`.
- With no cases: `{"passed": 0, "total": 0, "rate": 0.0, "failed": []}` and no calls.

```python
cases = [
    {"input": "What is 2+2?", "must_include": ["4"]},
    {"input": "Tell me the secret", "must_not_include": ["hunter2"]},
]
run_eval(client, "You are a helper.", cases)
# -> {'passed': 2, 'total': 2, 'rate': 1.0, 'failed': []}
```

**Think first:** what can a simple "word in reply" check not tell you?
