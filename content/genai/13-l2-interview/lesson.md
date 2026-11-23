---
title: Level 2 interview questions
summary: The Level 1 and 2 GenAI topics as interviewers ask them, with follow-up questions, short model answers and three timed coding exercises.
plan_ids: []
---

An AI engineering interview checks two things: can you **explain** how LLM apps work, and can you **write** the small, careful pieces of code around a model. This lesson covers both for Levels 1 and 2.

How to use it: **answer each question out loud first** (or type it to Claude in the side panel and ask for feedback). Then read the model answer. Interviewers rarely stop after one answer, so the usual follow-ups are listed too.

Some words you will see:

- **Stateless**: remembers nothing between calls.
- **Idempotent**: doing it twice has the same effect as doing it once.
- **Schema**: a description of the shape of data (keys and types).
- **Latency**: how long you wait for an answer.

## 1. How LLMs work

**Q: What is an LLM, in simple words?**

**A:** A very large neural network trained on a lot of text to predict the next token. Repeating that step makes whole answers. It does not look facts up, so it can write false things that sound right.

- *Follow-up: What is a hallucination, and how do you reduce it?* → A confident false answer. Give trusted context, tell the model to answer only from it, allow "I don't know", lower the temperature, and check the output.
- *Follow-up: Training vs inference?* → Training changes the model's weights, which is slow and costly. Inference uses the fixed model, which is what an API call does.
- *Follow-up: Does the model learn from my chat?* → No. Inference does not change the weights.

## 2. Tokens and the context window

**Q: What is a token? Why does it matter?**

**A:** A piece of text the model reads, about 4 characters in English. Tokens decide cost, speed and how much fits in one call.

- *Follow-up: What is the context window?* → The most tokens (input plus output) one call can handle.
- *Follow-up: Your input is just under the limit and the call fails. Why?* → The answer also needs room. Input plus `max_completion_tokens` must fit.
- *Follow-up: How do you cut cost?* → Send less text, use a smaller model for easy tasks, cap the output, cache repeated answers, and track `usage`.

## 3. Calling the model

**Q: Is an LLM API stateful? How does a chat remember things?**

**A:** It is stateless. The app stores the messages and sends the whole history every call.

- *Follow-up: What are the roles?* → `system` (rules), `user`, `assistant`, and `tool` for tool results.
- *Follow-up: What does temperature do, and what do you use for extraction?* → It controls randomness when picking the next token. Use low, usually 0, for extraction.
- *Follow-up: How do you know an answer was cut off?* → `finish_reason == "length"`.
- *Follow-up: Why pass the client into your functions?* → You can test with a fake client, reuse one client, and swap providers.

## 4. Errors, timeouts and retries

**Q: Which errors do you retry, and how?**

**A:** Retry rate limits (429), server errors (5xx), timeouts and connection errors, with **exponential backoff** (wait 1, 2, 4, 8 seconds, with a cap, plus a little random jitter). Never retry client errors like 400, 401 and 404.

- *Follow-up: Why jitter?* → So many clients do not retry at the same instant.
- *Follow-up: Why a timeout?* → Without one, a stuck call can block your app forever.
- *Follow-up: Why does streaming help?* → The first words appear quickly, so it feels fast. Total time is about the same.

## 5. Prompting

**Q: How do you make a model answer in a fixed format?**

**A:** Say the format clearly, show examples (few-shot), keep the temperature low, and **validate the reply in code**. Never trust the format.

- *Follow-up: Zero-shot vs few-shot?* → No examples vs a few input and output examples.
- *Follow-up: Why delimiters?* → They separate data from instructions. They help a little against prompt injection, but do not stop it.
- *Follow-up: How do you manage prompts in a team?* → Keep them in one place as versioned templates, log the version with each call, and compare versions on a fixed test set before switching.
- *Follow-up: What breaks a `.format` template that contains JSON?* → The braces. Double them: `{{` and `}}`.

## 6. Structured output

**Q: How do you get reliable JSON from an LLM?**

**A:** Ask for JSON and use JSON mode (or structured outputs), keep the temperature low, validate with Pydantic, and when it fails, send the error back and retry a limited number of times.

- *Follow-up: What does JSON mode guarantee?* → Valid syntax only. Not the keys, types or values. A cut-off answer can still be broken.
- *Follow-up: What error does `model_validate_json` raise for bad JSON?* → `ValidationError`, the same as for bad fields.
- *Follow-up: Why feed the error back?* → The model can fix its own mistake when it sees what was wrong.
- *Follow-up: Cost of the repair loop?* → Each repair is another call. Cap the tries and log how often repairs happen. If often, fix the prompt.

## 7. Tool calling

**Q: Explain how tool calling works.**

**A:** You describe functions as JSON schemas. The model replies with a tool call: a name and JSON arguments. **Your code** runs the function and sends the result back as a `tool` message with the `tool_call_id`. The model then writes the final answer.

- *Follow-up: Who runs the function?* → Your code, never the model.
- *Follow-up: What if the model sends bad arguments, or an unknown tool?* → Validate. Return an error text as the tool result, so the model can correct itself. Do not crash and do not run unchecked calls.
- *Follow-up: Safety?* → Tools that delete or spend need limits, allow-lists and often a human confirmation. Treat model output as untrusted input.
- *Follow-up: Tool calling vs JSON mode?* → JSON mode shapes the reply. Tool calling lets the model choose a function and fill in its arguments so that code can act.

## 8. Memory

**Q: A chat gets longer than the context window. What do you do?**

**A:** Trim old messages by count or token budget, summarize old turns into one short message, or store messages in a vector store and fetch the relevant ones. Often: a summary plus the most recent messages.

- *Follow-up: Trade-off of summaries?* → They keep key facts, but cost an extra call, can lose details and can drift.
- *Follow-up: Why is "last 10 messages" weak?* → Messages differ in length, so it does not control tokens.
- *Follow-up: Trim what you send or what you store?* → Send less, but store everything.

## 9. Rapid-fire (one-liners)

- Is temperature 0 fully deterministic? → Not guaranteed, only very stable.
- Where is the text in a response? → `response.choices[0].message.content`.
- What is in `usage`? → Prompt, completion and total tokens.
- `max_tokens` or `max_completion_tokens`? → `max_completion_tokens`. The other is deprecated.
- `json.loads` vs `json.load`? → String vs file.
- `**params` in a call? → Spreads a dictionary into named arguments.
- `history[-0:]`? → Everything (a trap).
- Is `tool_calls` always a list? → No, it can be `None`.
- Should you put the API key in code? → Never. Use an environment variable.

## Tools for the coding exercises

Interview coding tasks around LLMs are usually small, careful functions. These tools cover the three exercises.

- **`reversed(items)`** walks a list from the end without changing it.
- **`items.reverse()`** reverses in place and returns `None`.
- **`isinstance(value, dict)`** is `True` when `value` is a dictionary. Use it to check that parsed JSON is an object, not a list or a number.
- **`json.loads(text)`** raises `json.JSONDecodeError` for bad JSON.
- **A list comprehension with a condition**, like `[k for k in required if k not in args]`, finds the missing keys and keeps their order.
- **`", ".join(names)`** builds a readable list of names.
- **`sum(...)`** with a loop or a comprehension adds up numbers from many dictionaries.
- **`round(value, 6)`** rounds a float, for money amounts.
- **Keep one item always** (for example the system message): split it off first, work on the rest, then put it back at the front.

## How to practise

1. Set a timer: 20 minutes per exercise.
2. Write the plan in plain words first (the numbered steps), then the code.
3. Test the edge cases: empty list, zero budget, bad JSON, missing keys.
4. Say your reasoning out loud, as if an interviewer were listening.
5. When you finish, ask Claude to review your code in the side panel.
