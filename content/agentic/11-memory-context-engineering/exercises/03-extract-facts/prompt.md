# Let the model pick the facts to remember

You do not want to save every message. A cheap model call can **extract** the lasting facts ("Dev lives in Pune") and skip the small talk. This is how many assistants write their long-term memory.

The starter gives you `ask(...)` (one model call, returns stripped text) and `import json`. Write `extract_facts(client, message)`:

1. Call `ask(client, prompt)` where `prompt` is exactly:
   `"List the lasting facts about the user in this message as a JSON list of short strings. Reply with the JSON list only. Use [] if there are none.\n\n" + message`
2. Find the JSON list in the reply: from the first `[` to the last `]` (the model may add words or a code fence around it). If there is no `[`, or the `]` comes before the `[`, return `[]`.
3. Parse it with `json.loads`. If that fails, or the result is not a list, return `[]`.
4. Return only the items that are strings with some text in them, each with spaces at both ends removed.

```python
extract_facts(client, "I am Dev from Pune and I like Python")
# -> ['Dev likes Python', 'Dev lives in Pune']
```

**Think first:** the reply may be wrong. What should happen to your memory if the model returns nonsense?

**Hint:** `reply.find("[")` and `reply.rfind("]")` give the two positions. Catch `json.JSONDecodeError`.
