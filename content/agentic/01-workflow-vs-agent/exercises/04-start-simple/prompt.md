# Start simple, escalate only when needed

A cheap pattern for real apps: try the **simple** way first. Only if its answer is not good enough, call the expensive **agent**.

Write `start_simple(question, simple_fn, agent_fn, good_enough)`. All three of `simple_fn`, `agent_fn` and `good_enough` are functions that you receive as arguments.

1. Call `simple_fn(question)`.
2. If it returns an answer and `good_enough(answer)` is `True`, return `{"answer": answer, "used": "simple"}`. Do **not** call `agent_fn`.
3. If `good_enough(answer)` is `False`, call `agent_fn(question)` and return `{"answer": that_answer, "used": "agent"}`.
4. If `simple_fn` **raises an exception**, treat it as "not good enough": call the agent. (Use `try` / `except Exception`.)

```python
def simple(q):  return "I am not sure"
def agent(q):   return "Paris"
def good(a):    return "not sure" not in a

start_simple("Capital of France?", simple, agent, good)
# -> {'answer': 'Paris', 'used': 'agent'}
```

**Think first:** what must `good_enough` check, so that the simple path is not trusted when it is wrong? Who writes that check in a real app?

**Hint:** the agent function must be called **at most once**, and never when the simple answer is good.
