# Capstone part 1: route the question

The capstone is one agent that ties everything together: the **DevDocs assistant**. A user asks a question. It can be about the **documentation** (use search, RAG), about the user's **own tasks** (use a TaskFlow tool), or just **small talk** (no tool). The first step is a cheap model call that picks the **route**. This is the routing pattern of lesson 3.

The starter gives you `ask(client, prompt, system=None, temperature=0)`. Write `route_question(client, question)`:

1. Call `ask` with exactly this prompt:
   `"Pick one route for this question. docs = questions about the API documentation. tasks = questions about the user's own tasks. chat = greetings and small talk. Reply with one word: docs, tasks or chat.\n\nQuestion: " + question`
2. Clean the reply: `reply.strip().strip(".!\"' `").lower()`.
3. If the result is one of `"docs"`, `"tasks"`, `"chat"` (the list `ROUTES` is given), return it. Anything else returns `"docs"`, the safe default (searching the docs is harmless).

```python
route_question(client, "How do I create a task?")
# -> 'docs'
```

**Think first:** why is `"docs"` a better default than `"tasks"` when the reply is unclear?

**Hint:** an exact match, never "contains". `"I think it is about tasks"` is not a clean answer.
