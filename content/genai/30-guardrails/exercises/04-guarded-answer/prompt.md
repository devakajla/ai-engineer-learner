# A guarded answer

Put the guardrails around one model call. In the starter: `check_input` and `redact_pii`, and the constant `REFUSAL`.

Write `guarded_answer(client, text, system, max_chars=2000, banned=None)`.

Rules:
1. Run `check_input(text, max_chars, banned)`. If it is not ok, **do not call the model**. Return `{"answer": REFUSAL, "blocked": "input", "reason": <the reason from the check>}`.
2. Otherwise call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=[system message, user message], temperature=0)`. The user message holds `redact_pii(text)` (so personal data never leaves your server).
3. Take the reply text (it may be `None`: treat that as `""`) and apply `redact_pii` to it.
4. If the redacted reply is empty or only spaces, return `{"answer": REFUSAL, "blocked": "output", "reason": "empty answer"}`.
5. Otherwise return `{"answer": reply, "blocked": None, "reason": ""}`.

```python
guarded_answer(client, "Mail asha@example.com a hello", "Be brief.")
# the model sees "Mail [EMAIL] a hello"; its reply "Sure, I wrote to bob@x.org" becomes
# -> {'answer': 'Sure, I wrote to [EMAIL]', 'blocked': None, 'reason': ''}
```

**Think first:** which guardrail runs before the model, and which after? Why do you need both?
