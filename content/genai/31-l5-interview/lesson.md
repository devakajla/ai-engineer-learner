---
title: Level 5 interview questions
summary: Agents, tools, serving, streaming, caching, cost, observability and guardrails as interviewers ask them, with follow-up questions, short model answers and three timed coding exercises.
plan_ids: []
---

Level 5 is where an LLM demo becomes a real product: it acts (agents), it is served to many users, it must be cheap enough, visible, and safe. Interviewers love it because there is no single right answer. They want to hear **trade-offs** and **what you would measure**.

How to use this lesson: **answer each question out loud first**, then read the model answer. The follow-up questions are the ones interviewers usually ask next.

Some words you will see:

- **Agent**: a loop where the model chooses tool calls until it is done.
- **Workflow**: a fixed path of steps written in code, maybe with model calls inside.
- **Trace**: the full record of the steps of one request.
- **p95 latency**: the time that 95% of requests beat.
- **TTL**: time to live. How long a cache entry is kept.

## 1. Agents

**Q: What is an agent, and how is it different from a plain LLM call or a workflow?**

**A:** A plain call is one question, one answer. A workflow is a path that your code decides (always search, then answer). An agent is a loop where the **model** decides the next step by choosing tool calls, your code runs them, and the results go back, until the model answers. Agents handle open-ended tasks, but they are slower, costlier and less predictable.

- *Follow-up: When would you NOT use an agent?* → When the steps are known in advance. A fixed workflow is cheaper, faster, easier to test and more reliable.
- *Follow-up: How do you stop an agent from running forever?* → A hard `max_steps`, a loop guard on repeated identical calls, a token or cost budget, a time limit, and a clear `stopped` reason in the result.
- *Follow-up: Why does an agent cost more than the number of steps suggests?* → Each step resends the whole history, and the history grows. The input tokens add up faster than linearly.
- *Follow-up: What happens when a tool fails?* → Return the error text as the tool result so the model can adapt. Guard against the same failing call repeating.
- *Follow-up: Each step is 95% reliable. What about 10 steps?* → About 60% (0.95 to the power 10). Keep agents short, tools clear, and add checks.

## 2. Tools

**Q: How do you design good tools for an agent?**

**A:** Few tools, each with a clear name and description (the model reads it to decide), simple typed parameters, small and useful results (not a huge dump), and clear error messages. Validate every argument like input from a stranger.

- *Follow-up: The model keeps picking the wrong tool. What do you check?* → The descriptions (overlap, vagueness), the number of tools, the examples, and the model's tool-calling quality. Often merging or renaming tools fixes it.
- *Follow-up: Native tool calling or the ReAct text format?* → Native calling returns structured calls (a name and JSON arguments), is more reliable and needs no text parsing. ReAct-style text (`Thought`, `Action`, `Action Input`) works with any model but needs parsing and error handling.
- *Follow-up: Parallel tool calls?* → The model may ask for several independent calls in one step. Run them all, and answer each with its own `tool_call_id`.

## 3. Serving and streaming

**Q: How do you serve an LLM feature to many users?**

**A:** Put it behind an API. Check auth, validate input and apply rate limits **before** calling the model. Set timeouts. Stream tokens to the client so the first words appear fast. Keep the provider key on the server. Log every call. Scale by running several workers behind a load balancer, and queue long jobs.

- *Follow-up: Why stream?* → The total time stays the same, but the time to first token drops, so the app feels fast.
- *Follow-up: SSE or WebSocket?* → SSE for one-way token streams: plain HTTP, easy through proxies, automatic reconnect. WebSocket for two-way traffic such as voice.
- *Follow-up: The model fails halfway through a stream. What do you do?* → The `200` status is already sent. Send an `error` event inside the stream, do not send `done`, and let the client offer a retry.
- *Follow-up: The stream arrives all at once. Why?* → Something buffers it: nginx, a CDN, or compression. Turn buffering off for that route.
- *Follow-up: The user closes the tab.* → Stop the model call, or you pay for an answer nobody reads.

## 4. Cost, caching and rate limits

**Q: Your LLM bill doubled. What do you do?**

**A:** First find out **where** the cost comes from, with logs: cost per feature, per user, per model, and tokens in and out. Then pull the levers: shorter prompts and less context, `max_completion_tokens`, a cheaper model for easy tasks (routing), caching, batching, agent step and budget limits, and per-user budgets with alerts. Check for a bug (a loop, retries) before you redesign.

- *Follow-up: What can you cache?* → Deterministic requests (temperature 0) with a key made from the model, messages and settings. Not random outputs, not private data shared across users, and fast-changing facts only with a TTL.
- *Follow-up: What is prompt caching?* → The provider remembers the start of a long prompt, so a repeated prefix is cheaper and faster. Keep the stable part first.
- *Follow-up: What is a semantic cache and what is its risk?* → It matches questions with similar meaning using embeddings. It saves more, but can return a wrong answer for a question that only looks similar. Use a strict threshold and low-risk content.
- *Follow-up: How do you rate limit?* → Per user, with a sliding window or token bucket in a shared store, on requests **and** tokens or cost. Return `429` with `Retry-After`, and do not call the model for a blocked request. Handle the provider's own `429` separately with backoff.

## 5. Observability

**Q: What do you log and monitor for an LLM app?**

**A:** For each call: request id, user or tenant, model, prompt version, tokens in and out, cost, latency (first token and total), status, retries, `finish_reason`. For RAG: retrieved chunk ids and scores. For agents: every step and tool call. Compute error rate, cost, p50 and p95 latency, cache hit rate, and quality scores on sampled traffic. Keep traces. Mask personal data and set retention.

- *Follow-up: Why p95 and not the average?* → The average hides the slow tail. p95 shows what 1 user in 20 feels.
- *Follow-up: How do you notice quality getting worse?* → Run the evaluation set on every change, score a sample of real traffic with checks and a judge, and watch the user feedback.
- *Follow-up: Which tools?* → Tracing and evaluation tools such as Langfuse or LangSmith, or OpenTelemetry-based systems. They change quickly. The ideas stay.

## 6. Safety and guardrails

**Q: How do you protect an agent from prompt injection?**

**A:** There is no complete fix, so you limit the damage. Treat all outside text (user input, documents, web pages, tool results) as untrusted data and tag it. Keep secrets out of the prompt. Give tools least privilege with an allow-list, validated arguments and ownership checks. Require human approval for risky or irreversible actions. Avoid the mix of private data, untrusted content and a way to send data out. Check outputs. Cap steps, tokens and money. Red-team with a saved set of attacks.

- *Follow-up: What is indirect prompt injection?* → Malicious instructions hidden in content the app reads later (a page, an email, a PDF, a tool result).
- *Follow-up: Is a system prompt rule enough?* → No. It is a request, not a lock. Use controls in code.
- *Follow-up: How do you handle PII?* → Collect the minimum, mask it before the provider call and before logging, control who can read logs, and set retention.
- *Follow-up: How do you test guardrails?* → A saved set of attack prompts, run after every change, and measure both attacks that pass and good requests that get blocked.

## 7. A design question to practise

**Q: Design a support assistant for a company. It answers from the company's docs, can look up a customer's order, and can issue a refund.**

**A (outline):**
1. **Split by risk.** Answering from docs is RAG (read-only). Order lookup is a read-only tool. A refund is a risky action.
2. **Retrieval** with tenant and group filters in code (lesson 40), citations (lesson 22) and "I don't know" when there is no support.
3. **Agent loop** with 2 to 3 tools, `max_steps`, a loop guard and a token budget.
4. **Refund tool:** allow-listed, arguments validated, ownership checked with the real customer id from the login, and **human approval** (or a small limit with approval above it).
5. **Serving:** auth, rate limit, input checks, streaming with SSE, timeouts, and a kill switch.
6. **Cost:** cache FAQ answers (temperature 0), a cheaper model for classification and routing, and a budget per user.
7. **Observability:** a trace per conversation, the cost per resolved ticket, p95 latency, refusals, handoffs to humans, and thumbs up or down.
8. **Evaluation:** a golden set of real tickets, an attack set, and a weekly review of sampled conversations.

## 8. Rapid-fire (one-liners)

- Agent stop reasons? → done, max steps, loop, budget, error, human.
- Where is the agent's memory? → In the message history you resend each step.
- Why is the history growing a cost problem? → Every step pays for all earlier steps again.
- Tool errors go to the model as? → Text in the tool result.
- Allow-list is checked on? → The tool name (and then the arguments).
- SSE content type? → `text/event-stream`.
- What ends an SSE event? → A blank line.
- Status after a stream has started? → Already `200`, so errors travel as events.
- Cache key must include? → Model, messages, temperature (and tools).
- Cache when temperature is above 0? → Usually no.
- Provider 429 vs your own limit? → Backoff on the first, enforce the second on users.
- p95 means? → 95% of requests were this fast or faster.
- Never put in a prompt? → Secrets, keys, other users' data.
- Lethal trifecta? → Private data, untrusted content, a way to send data out.

## Tools for the coding exercises

Interview coding tasks here are small functions with careful rules. These tools cover the three exercises.

- **`text.split("\n")`** and **`enumerate(lines)`** to scan lines with their positions.
- **`line.strip().startswith("Action:")`** and slicing with `len("Action:")` to cut a prefix.
- **`json.loads(text)`** inside `try / except json.JSONDecodeError`, and `isinstance(value, dict)`.
- **`reversed(items)`** and **`list.reverse()`** to walk or flip a list.
- **`break`** to stop at the first item that does not fit.
- **A running total** (`history += added`) inside a loop to build a growing sequence.
- **`sum(list)`** and `round(x, 6)`.
- **Guard the empty case first** (no messages, no steps).

## How to practise

1. Set a timer: 20 minutes per exercise.
2. Write the plan in plain words first, then the code.
3. Test the edge cases: empty input, a bad JSON text, a single huge message, no steps.
4. Say your reasoning out loud, as if an interviewer were listening.
5. When you finish, ask Claude to review your code in the side panel.
