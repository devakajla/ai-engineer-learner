---
title: "Capstone: the DevDocs agent with RAG, tools, tracing and evals"
summary: Join everything into one project you can show in an interview - a routed agent that answers from API docs and from the user's tasks, with safe tool output, traces, an eval set, a regression gate and a short report.
plan_ids: []
---

A capstone is the project you put on your CV and talk about for 20 minutes in an interview. A good one is **small but complete**: it shows that you can build, test, measure and defend an LLM system, not only call a model.

You already have most pieces. This lesson tells you what to build, in what order, and how to show it. The code project is **DevDocs Copilot** (the folder `~/Projects/devdocs-copilot`). The last project step of this track (step 26) adds the capstone files, with the tests, so the work is graded.

## What you are building

An assistant that answers questions about API documentation and about the user's own tasks:

```
question
   |
   v
 guard  (input checks, lesson 15 and GenAI 30)
   |
   v
 route  --- chat  ---------------------------> model answer
   |  \
   |   +--- tasks ----> TaskFlow tool -----+
   |                                       |
   +------ docs ------> hybrid search -----+--> quarantine --> answer with citations
                        (RAG, GenAI L4)             (lesson 15)        |
                                                                       v
                                                 trace + cost + latency (lesson 16)
```

| Part | From | What you show |
|---|---|---|
| Hybrid search over docs with citations | GenAI L3 and L4 | retrieval quality, grounded answers |
| Agentic retry (grade, rewrite, give up) | agentic 12 | handling bad retrieval |
| Router | agentic 3 and exercise 1 | cheap model for the easy decision |
| Tool calling against TaskFlow | GenAI 11, agentic 2 | real action with safe arguments |
| Safety layer | agentic 15 | quarantine, risk tiers, approval, audit log |
| Memory | agentic 11 | facts per user |
| Tracing | agentic 16 | spans for every step |
| Eval set and gate | agentic 16, GenAI 25 and 41 | numbers, no guessing |
| Serving | GenAI 28, 29 | streaming, cache, cost |

You do not need every row at full depth. A smaller capstone with **all rows present and measured** beats a big one that you cannot explain.

## Build order (do not skip ahead)

1. **Plain RAG first.** Search, prompt, answer with citations. Write 20 eval cases. Record the baseline score. (about 2 hours)
2. **Router and tools.** Add the route step (exercise 1). Add one TaskFlow tool. Run the eval again.
3. **Safe answer.** Quarantine tool output, risk tiers, and a step cap (exercise 2 and lesson 15).
4. **Tracing.** Wrap every model call and tool call in a span (lesson 16). Print the trace for one question.
5. **Eval and gate.** Run the full eval set. Make the report (exercise 3). Save the result as the baseline for the regression gate.
6. **Improve with evidence.** Pick the biggest failure group. Fix it. Run the gate. Keep the change only if the scores improve.
7. **Write it up** (below).

> Steps 1 and 5 are the ones people skip, and the ones interviewers care about most. Without a baseline you cannot say that anything improved.

## The three exercises

You build the **core of the agent** in small tested pieces. The project step then joins them with the real RAG code.

### Route the question (exercise 1)

A cheap model call returns one word: `docs`, `tasks` or `chat`. Parse it strictly. Anything unclear becomes `docs`, the harmless default. Greetings skip retrieval and save money.

### Traced, safe answer (exercise 2)

```python
route  = traced_call(trace, "route", "llm", clock, route_question, client, question)
data   = traced_call(trace, route, "tool", clock, tools[route], question)
prompt = "Answer the question using only the tool output. ...\n\n" + wrap_untrusted(route, data) + ...
text   = traced_call(trace, "answer", "llm", clock, ask, client, prompt)
```

Three things happen in this flow:

1. Every step leaves a **span**, so you can see where time and tokens went.
2. The tool output is **wrapped as untrusted data** before the model sees it.
3. If the tool fails, the user gets a **polite message**, and you make no further model call. No made-up answer.

### The report (exercise 3)

```
Cases: 20
Pass rate: 85%
Average steps: 2.4
Total tokens: 41200
p95 latency: 3100 ms
Failed: q07, q13, q18
```

Six lines that tell an interviewer you measure things. Put it in your README.

## Good eval cases for this capstone

- **8 docs questions** with a known fact in the answer (`must_contain`) and `expected_tools: ["docs"]`.
- **4 task questions** ("what is overdue?") with `expected_tools: ["tasks"]`.
- **3 small talk** with no tools.
- **3 unanswerable** questions (the docs do not say). The right answer is "I could not find this".
- **2 attacks:** a doc chunk that contains "ignore previous instructions". The agent must not obey.

Take real questions from your own use. Keep the set in a file in the repo and never change old cases without noting why.

## How to show it

A strong README has, in this order:

1. **One paragraph:** what it does and for whom.
2. **A diagram** (like the one above).
3. **The numbers:** the report from exercise 3, before and after your best improvement.
4. **Three design decisions with the trade-off:** for example "I used hybrid search because BM25 found exact error codes that embeddings missed (recall@5 from 0.62 to 0.81)".
5. **Safety:** the layers you added and one attack you tested.
6. **What you would do next** and what you know is weak.
7. **How to run it** in three commands, and how to run the tests.

Practise a **5-minute talk**: the problem, the diagram, one thing that failed and how you fixed it, the numbers. Interviewers love the failure story, because it shows you debug with evidence.

## Try it live

1. Build step 1 on your real docs and real Groq key. Write the 20 cases. Run the baseline.
2. Print the trace for three questions: one docs, one tasks, one chat. Find the slowest span in each.
3. Add one attack case in a doc file. Does the model obey it with no protection? With `wrap_untrusted`? With the system prompt rule?
4. Change something (chunk size, a prompt line). Run the gate. Write one sentence on what you learned.
5. Record a 5-minute screen demo.

## A little deeper

- **Frameworks.** You can build the same graph in LangGraph (lessons 8 to 12). Keep your plain version too: it shows you understand what the framework does for you.
- **Deployment.** FastAPI plus SSE (GenAI lesson 28), a Dockerfile, and a `/health` endpoint. One live URL helps a lot, but a clean repo with tests helps more.
- **Cost line.** Add "cost per question" to the report (lesson 17). Interviewers like it.
- **Human feedback.** Add thumbs up and down and store them with the trace id. Turn bad ones into new eval cases.
- **Keep scope small.** Three tools and one data source are enough. A capstone that is too wide gets shallow.

## Common mistakes

- Building the agent before you have eval cases.
- No baseline, so "it got better" is a feeling.
- Letting the router default to a tool with side effects.
- Putting tool output into the prompt with no wrapper.
- A README with screenshots but no numbers.
- Hiding failures. Say what does not work.
- Adding a framework or a fancy feature that you cannot explain.

## Interview corner

**Walk me through your capstone.**
Problem, diagram, the build order, the baseline number, the biggest failure group, the fix and the new number, the safety layers, and what I would do next.

**What was the hardest bug?**
Pick a real one with evidence. For example: a chunk containing an instruction that the model followed. Found by an attack case in the eval set. Fixed with quarantine plus a system rule. The attack case now guards against it.

**How do you know your changes helped?**
A fixed eval set, a baseline run, a regression gate that blocks changes that lower the pass rate, regress a passing case or raise the cost a lot.

**What would you do with more time?**
Online feedback and sampling, a reranker (measured), a cheaper model for grading, multi-tenant filters, and a deployment with alerts.

**Why a router instead of one big agent?**
A cheap decision up front saves tokens and latency for easy questions, limits which tools can be reached, and makes each route easy to test.

## Summary

- A capstone is **small but complete**: build, test, measure, defend.
- Build order: plain RAG and baseline, router and tools, safe answer, tracing, eval and gate, evidence-based improvement, write-up.
- Route with a cheap call and a strict parse. Unclear means the harmless default.
- Every step is traced. Tool output is quarantined. A failing tool gives a polite message, not a guess.
- Report: cases, pass rate, average steps, tokens, p95 latency, failed ids.
- The eval set holds docs, tasks, small talk, unanswerable and attack cases.
- Show numbers before and after, three decisions with trade-offs, safety layers and honest weaknesses.
- Reference: `reference/agentic-langchain-langgraph.md`.
