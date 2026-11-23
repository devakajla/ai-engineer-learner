---
title: "Mock interview 1: concepts (GenAI and agents)"
summary: A timed concept interview across LLM basics, prompting, RAG, agents, LangGraph, memory, MCP, safety, evaluation, fine-tuning and serving, with follow-up questions, short model answers and three coding drills.
plan_ids: []
---

This is a practice interview. The goal is to **speak your answers out loud**, in plain words, in about a minute each, and to hear where you get stuck. Reading the answers is the second step, not the first.

## How to use this lesson

1. Set a timer for **45 minutes**. Cover the answers.
2. Pick a section. Read a question. Answer **out loud**, as if to a person. A good answer has: a one-line definition, **why it matters**, an example or a trade-off.
3. Read the model answer. Mark each question: green (said it well), yellow (missed a point), red (could not say).
4. Repeat the yellow and red ones tomorrow. Record yourself once. You will hear filler words and long pauses.
5. Do the three coding drills at the end (about 10 minutes each).

Tips for a real interview:

- Start with the **answer**, then the reason. Do not build up to it.
- Say **"it depends"** only with what it depends on: "It depends on latency and data privacy. If..., then..."
- Give a **number or an example** when you can ("about 4 characters per token").
- When you do not know: say what you do know, how you would find out, and move on.
- Mention **trade-offs** and **how you would measure**.

## 1. LLM basics

**Q: How does an LLM generate text?**
**A:** It predicts the next token from all the tokens so far, picks one (by sampling), adds it, and repeats. A token is a piece of a word. It does not "look up" facts. It produces likely text.
- *Follow-up: Why do models hallucinate?* → They are trained to produce plausible text, not true text. With no good information in context they still produce something fluent. Retrieval, citations and "say you don't know" rules reduce it.

**Q: What is the context window, and what happens when you exceed it?**
**A:** The maximum number of tokens (input plus output) the model can handle in one call. If you exceed it, the call fails or old text is cut. You must trim, summarise or retrieve only what you need.
- *Follow-up: Does a bigger window solve RAG?* → No. Long prompts cost more, are slower, and models use the middle of long text poorly. Retrieval still helps with cost, freshness and access control.

**Q: What do temperature and top-p do?**
**A:** They control randomness when picking the next token. Temperature 0 is almost always the same answer. Higher temperature gives more variety. Top-p keeps only the most likely tokens that add up to p. For extraction and tools use low values. For creative text use higher.

**Q: What is a KV cache and why do you care?**
**A:** The model keeps the key and value vectors of earlier tokens so it does not recompute them for every new token. It speeds up generation but uses memory that grows with context length and with the number of users.

**Q: Base, chat and reasoning models?**
**A:** A base model only continues text. A chat model is further trained to follow instructions (SFT, then preference tuning such as RLHF or DPO). A reasoning model is trained to think step by step before the answer, which helps with hard problems but costs more tokens and time.

## 2. Prompting and structured output

**Q: Give three prompt patterns and when you use them.**
**A:** Clear instructions with a role and format for most tasks. Few-shot examples when the format or style is hard to describe. Chain of thought or a reasoning model for multi-step problems. Self-consistency (several answers, majority vote) when accuracy matters more than cost.

**Q: How do you get reliable JSON from a model?**
**A:** Ask for a schema (JSON mode or a JSON schema if the API supports it), validate with Pydantic, and on failure send the error back and retry a limited number of times. Never trust the output without validation.

**Q: How does tool calling work?**
**A:** You describe tools with a name, description and JSON schema. The model replies with a tool name and arguments instead of text. Your code validates the arguments, runs the tool, and sends the result back as a tool message. The loop continues until the model answers.
- *Follow-up: What can go wrong?* → Wrong tool, bad arguments, endless loops, injected instructions in results. Validate, cap steps, quarantine results.

## 3. Retrieval and RAG

**Q: Explain RAG and why you would use it.**
**A:** Retrieve relevant chunks from your own data, put them in the prompt, and ask the model to answer only from them, with citations. It gives fresh, private and checkable knowledge without retraining.

**Q: How do you choose chunk size?**
**A:** Chunks should be big enough to hold a complete idea and small enough to be specific. Start around 200 to 500 tokens with a small overlap, split on structure (headings, paragraphs), keep metadata, then **measure** retrieval on an eval set and adjust.

**Q: Why hybrid search?**
**A:** Embeddings find meaning but can miss exact words (error codes, names). BM25 finds exact terms but misses synonyms. Combining both (for example with reciprocal rank fusion) is usually better than either alone.

**Q: What does a reranker do?**
**A:** It re-scores the top candidates (for example 20) with a more accurate model that reads the question and the chunk together, then keeps the best few. It improves precision, at a cost in latency.

**Q: How do you evaluate a RAG system?**
**A:** Two parts. Retrieval: recall@k, MRR, nDCG on labelled questions. Generation: faithfulness (is every claim supported by the chunks?), answer relevance and citation checks, often with an LLM judge checked against human labels. Use a fixed golden set and run it on every change.

**Q: What are common RAG failures?**
**A:** Bad chunking, the answer is not in the index, wrong chunks ranked high, stale documents, too many chunks (lost in the middle), and the model ignoring the context. Classify failures first, then fix the biggest group.

**Q: How do you handle access control in RAG?**
**A:** Store the allowed users or groups as metadata, and **filter during retrieval**, so forbidden text never reaches the prompt. Never rely on the model to hide it.

## 4. Agents

**Q: What is an agent, and when should you NOT use one?**
**A:** A loop where the model chooses tool calls until it is done. Do not use one when the steps are known: a fixed workflow is cheaper, faster and easier to test. Use an agent when the path depends on what is found.

**Q: Name some workflow patterns.**
**A:** Prompt chaining, routing, parallelisation, orchestrator-workers, and evaluator-optimizer.

**Q: ReAct versus plan-and-execute?**
**A:** ReAct alternates thought, action and observation, so it adapts at each step. Plan-and-execute writes a plan first and then runs the steps, which is more predictable and can use a cheaper model for each step, but adapts less.

**Q: How do you stop an agent from looping for ever?**
**A:** A step cap, a cost cap, a time limit, detection of repeated identical calls, and a clear "give up" path.

**Q: When do you use multiple agents?**
**A:** When parts need different tools, permissions or contexts, or can run in parallel. Otherwise one agent or a workflow is better, because teams cost more tokens and are harder to debug. Supervisor and handoff are the two common shapes.

## 5. LangChain and LangGraph

**Q: What is LCEL?**
**A:** LangChain Expression Language: you join runnables with `|` (prompt, model, parser). Each runnable has `invoke`, `batch` and `stream`. It gives retries, fallbacks and streaming in a uniform way.

**Q: Why use LangGraph instead of a plain loop?**
**A:** It gives explicit state, conditional edges and loops, a checkpointer for memory and resume, streaming, human-in-the-loop with `interrupt`, and time travel. For a simple agent a plain loop is fine. LangGraph pays off as the flow grows.

**Q: What is a reducer in LangGraph state?**
**A:** A rule for combining several updates to one state key (append to a list, add numbers). It is needed when nodes run in parallel, and for message lists (`add_messages`).

**Q: How does memory work in LangGraph?**
**A:** A checkpointer saves the state after each step under a `thread_id`: that is short-term memory for one conversation. Long-term memory across conversations goes into a store.

**Q: How do you add human approval?**
**A:** Call `interrupt` in a node. The run pauses and the state is saved. Resume with `Command(resume=...)` on the same thread. It needs a checkpointer.

## 6. Memory and context

**Q: How do you keep long conversations from getting too big?**
**A:** Keep recent messages, summarise older ones, retrieve only relevant memories, trim long tool outputs, and set a token budget. Keep the system prompt and the current question always.

**Q: What are the risks of long-term memory?**
**A:** Wrong or poisoned facts that persist, privacy, and noise. Validate before saving, record the source, let users view and delete, and expire old facts.

## 7. MCP

**Q: What is MCP?**
**A:** An open protocol for AI apps (clients) to use tools, resources and prompts from servers. Write a tool once, use it from many clients. Messages are JSON-RPC, over stdio or HTTP.
- *Follow-up: Main risk?* → Tool descriptions and results are text in the prompt, so a bad server can inject instructions. Trust only reviewed servers and apply least privilege.

## 8. Safety

**Q: What is indirect prompt injection and how do you reduce it?**
**A:** Attacker text inside data the agent reads. You cannot fully prevent it, so you limit the damage: treat tool output as untrusted, least privilege tools, human approval for risky actions, break the lethal trifecta (private data, untrusted input, outbound channel), argument validation, step and cost caps, and an audit log.

**Q: What would you log, and what not?**
**A:** Log model, prompt version, tokens, latency, tool calls, decisions and errors. Do not log secrets, and redact personal data.

## 9. Evaluation and observability

**Q: How do you evaluate an agent?**
**A:** On the final answer, the trajectory (right tools in the right order) and efficiency (steps, tokens, latency, cost), over a fixed eval set built from real cases. Run it in CI as a regression gate.

**Q: What is tracing?**
**A:** A record of one request as spans: each model and tool call with timing, tokens and errors. It tells you where time and money go and why a run failed.

## 10. Fine-tuning, quantization and serving

**Q: Fine-tune, RAG or prompt?**
**A:** Prompt first. RAG for knowledge that is private or changing. Fine-tune for style, format or a narrow skill when you have enough clean examples, and prove it beats a prompted baseline.

**Q: What is LoRA?**
**A:** Freeze the model and train small low-rank matrices next to the layers. It trains well under one percent of the numbers and gives a small adapter file. QLoRA does it on a 4-bit base model.

**Q: What does quantization trade?**
**A:** Smaller memory and often faster inference, for a small loss of quality. 8-bit is nearly free, 4-bit is usually fine, below that it hurts. Test on your own eval set.

**Q: How do you serve a streaming answer?**
**A:** Server-sent events: the server sends each token chunk as it arrives. It makes the first words appear early. Handle errors inside the stream, and stop the model call if the client disconnects.

**Q: How do you cut LLM cost?**
**A:** Smaller models for easy steps, shorter prompts and fewer chunks, response and prompt caches, batching, routing, and step caps.

## Rapid fire (answer in 15 seconds each)

- Token versus word? A token is a sub-word piece. English averages about 4 characters.
- What is an embedding? A list of numbers that captures meaning, so similar texts are close.
- Cosine similarity? The angle between two vectors, from -1 to 1.
- What is HNSW? A graph index for fast approximate nearest-neighbour search.
- recall@k? Did the right chunk appear in the top k?
- What is idempotent? Running it twice has the same effect as once. Needed for safe retries.
- p95 latency? The time that 95% of requests beat.
- What is a regression gate? A check that blocks a change that makes the eval worse.
- What is a thread_id? The key of one conversation in a checkpointer.
- What is the lethal trifecta? Private data, untrusted input, and a way to send data out.

## Coding drills

1. **`merge_messages`**: the `add_messages` reducer (append, replace by id).
2. **`run_graph`**: a tiny LangGraph with conditional edges and a loop limit.
3. **`run_with_limits`**: a step cap and a cost cap for an agent.

## Summary

- Say the answer first, then why, then a number or a trade-off.
- Know the one-line definition and the main trade-off of each topic above.
- Practise out loud. Mark green, yellow, red. Repeat the red ones.
- Coding drills show you can build the ideas, not only name them.
- Reference: `reference/agentic-langchain-langgraph.md`.
