# Ask the judge

In the starter: `JUDGE_SYSTEM`, `build_judge_messages` and `parse_verdict` (exercises 1 and 2).

Write `judge(client, question, context, answer, max_tries=2)`.

Rules:
1. Build the messages with `build_judge_messages`.
2. Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, temperature=0)`. Temperature 0, so a judge gives the same grade each time as far as possible.
3. Read the reply text (`response.choices[0].message.content`) and parse it with `parse_verdict`.
4. If the verdict is not `None`, return it.
5. Otherwise try again, at most `max_tries` calls in total (send the same messages).
6. If every try failed, return `{"score": None, "reason": "unparseable"}`.

```python
judge(client, "Q?", "ctx", "A.")   # the client replies '{"score": 5, "reason": "ok"}'
# -> {'score': 5, 'reason': 'ok'}   (1 call)
```
