# 21. Observability: seeing inside your LLM app

When a normal program fails, you get an error and a stack trace. When an LLM app fails, nothing crashes. The answer is just **bad**, and you have no idea why. **Observability** means recording enough about every request that you can answer "what happened?" afterwards.

## What to record for every request

An LLM request is a **chain of steps**. Record each step with its inputs, outputs and timing.

@@ flow | Figure 21.1: one request, many steps, one trace.
Rewrite query|prompt, output, ms|blue -> Retrieve|chunk ids, scores, ms|yellow -> Rerank|new order, ms|purple -> Generate|prompt, answer, tokens, ms|green -> Checks|citations valid?|gray
@@ end

A whole request is a **trace**. Each step in it is a **span**. A trace has an id, and every span carries it, so you can collect all pieces of one request.

What to store per request:

| Field | Why |
| --- | --- |
| trace id, user or tenant id, time | find and group |
| the question and the rewritten query | see what was searched |
| retrieved chunk ids and scores | debug retrieval first |
| the final prompt (masked if needed) | exactly what the model saw |
| model name, settings, prompt version | reproduce and compare |
| input and output tokens, cost | money |
| latency per step, TTFT | speed |
| finish reason, errors, retries | reliability |
| user feedback | quality |

Mind privacy (chapter 17): mask personal data, set a retention time, and restrict who can read traces.

## A small tracing tool

A decorator that records each step's name and time. This one was run:

```python
import functools, time

LOG = []

def traced(name):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return function(*args, **kwargs)
            finally:
                LOG.append({"step": name, "ms": round((time.perf_counter() - start) * 1000)})
        return wrapper
    return decorator

@traced("retrieve")
def retrieve(question):
    return [1, 2]

retrieve("hello")
print(LOG)
# -> [{'step': 'retrieve', 'ms': 0}]
```

(The Python booklet, chapter 11, explained decorators.) The `try ... finally` records the time **even if the function raises**. Real systems send these records to a tracing tool instead of a list, and also use structured JSON logs, with one line per event and the trace id inside.

## Tools

- **Langfuse**, **LangSmith**, **Arize Phoenix**, **Helicone**: LLM-specific tracing with prompts, costs, scores and datasets. Several are open source.
- **OpenTelemetry**: the general standard for traces, metrics and logs. Many LLM tools can export to it.
- **Prometheus and Grafana**: metrics and dashboards for rates, errors and latency.

(None of these were set up for this booklet.)

## Dashboards and alerts

Track over time:

- requests per minute, error rate, retry rate, rate-limit (429) count
- latency: median and the slow tail (p95, p99)
- tokens and **cost** per day, per user, per feature
- "I do not know" rate, thumbs-down rate
- retrieval scores (a drop can mean a broken index)

**Alert** on: error rate high, cost per hour above a limit, p95 latency high, sudden jump in "I do not know".

## Feedback loops

Observability is what lets you **improve**:

@@ flow | Figure 21.2: the improvement loop.
Production traces|real questions and answers|blue -> Find bad cases|thumbs down, low scores, refusals|red -> Add to golden set|with the right answer|yellow -> Fix and run evals|prompt, chunking, retrieval|green
@@ end

Every real failure becomes a permanent test (chapter 16). This is how an LLM app gets better over time instead of randomly changing.

## Prompt versions

Give every prompt template a **version id**, and store it in the trace. When quality changes, you can tell which prompt version was running. Keep prompts in files under git (chapter 6).

::: {.box .checkpoint}
**Checkpoint:** given a bad answer, you can say which fields in a trace you would read first, and in what order.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Logging only the final answer, not the retrieved chunks.
- Logging private data in clear text, forever.
- No trace id, so the pieces of one request cannot be joined.
- Looking only at averages and missing the slow tail.
- No cost tracking, until the bill arrives.
- Collecting feedback and never using it.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What do you log for an LLM request?** The trace id, the question, retrieved chunks and scores, the final prompt, the model and settings, token counts and cost, latency per step, errors, and user feedback.

**Q: Trace vs span?** A trace is one whole request. A span is one timed step inside it.

**Q: How do you debug a wrong RAG answer in production?** Open the trace, check the retrieved chunks and scores, then the prompt, then the output. Add the case to the golden set.

**Q: Which metrics do you alert on?** Error and 429 rate, p95 latency, cost per hour, and sudden changes in refusal rate or retrieval scores.

**Q: Name LLM observability tools.** Langfuse, LangSmith, Arize Phoenix, Helicone, and OpenTelemetry for general telemetry.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Add `@traced` to three steps of your toy RAG and print the log.
2. Add a trace id (a UUID) to every log entry of one request.
3. Log the token counts from a fake client's `usage`, and add up the cost.
4. Write a function that finds the 95th percentile of a list of latencies.
5. Decide which five alerts you would set for a support bot.
6. **Think:** why is the slow tail (p99) often more important than the average?
:::
