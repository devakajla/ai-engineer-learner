# 22. Interview question bank

Short, honest answers you can say aloud in 30 to 60 seconds. For each one: say the **idea** first, then **one example**, then **the trade-off**. Chapter numbers show where to revise.

> How to use this: cover the answer, say yours aloud, then compare. Mark the ones you missed and come back in two days.

## A. Foundations (chapters 1 to 2)

**1. What is an LLM?** A neural network trained on a huge amount of text to predict the next token. Repeating that prediction produces text.

**2. What is a token?** A piece of text (a word, part of a word, or a symbol) that the model reads and writes. Tokens are the unit for limits and prices.

**3. What is a context window?** The maximum tokens the model can handle in one request, counting input and output together.

**4. Why do LLMs hallucinate?** They produce likely text, not verified text. With missing knowledge they still produce fluent output.

**5. What is the transformer, in one paragraph?** The architecture behind LLMs. Its key part is attention, which lets each token look at the other tokens and weigh how relevant they are, in parallel.

**6. Pre-training vs instruction tuning vs RLHF?** Pre-training learns language and facts from raw text. Instruction tuning teaches following tasks with example pairs. RLHF aligns answers with human preferences.

**7. How is the cost of a call calculated?** Input tokens times input price plus output tokens times output price. Output usually costs more per token.

**8. Why are some languages more expensive?** The tokenizer splits less common languages into more tokens for the same meaning.

## B. Using the API (chapters 3 to 5)

**9. Are LLM APIs stateful?** No. The client resends the history on every call.

**10. Message roles?** system, user, assistant, tool.

**11. What does temperature do?** It sharpens or flattens the next-token probabilities. Low means steady, high means varied.

**12. Temperature vs top-p?** Temperature reshapes all odds. Top-p keeps the smallest set of tokens whose probabilities add up to p.

**13. Which settings for extraction or RAG?** Low temperature (0 to 0.2), a token limit, and a structured format.

**14. What does `finish_reason: length` tell you?** The answer was cut by the token limit.

**15. Why stream?** The first token appears quickly, so the app feels fast, and users can stop early.

**16. Which errors do you retry?** Rate limit (429), server errors (5xx), timeouts and connection errors. Not 400, 401, 403 or 404.

**17. What is exponential backoff with jitter?** Waiting longer after each failure, plus a random amount, so clients do not retry together.

**18. What is a provider fallback?** Trying a second model or provider when the first fails.

**19. How do you test code that calls an LLM?** Inject the client and use a fake that returns fixed responses and records the arguments.

## C. Prompts, structure and tools (chapters 6 to 9)

**20. Zero-shot, few-shot?** No examples versus a few input-output examples in the prompt.

**21. What is chain of thought?** Asking for step-by-step reasoning before the answer, to improve multi-step tasks.

**22. Where do rules go, system or user message?** Standing rules, role and format in the system message. Task data in the user message.

**23. How do you evaluate a prompt change?** Run it on a fixed test set and compare scores with the previous version.

**24. What is prompt caching?** Reusing the processed fixed prefix of a prompt, so repeated requests are cheaper and faster. Put fixed text first.

**25. How do you get reliable JSON?** Describe the schema, use JSON mode or schema-constrained output, validate with Pydantic, and retry with the error message a few times.

**26. JSON mode vs schema-constrained output?** JSON mode guarantees valid syntax. Schema output also guarantees fields and types.

**27. How does tool calling work?** The model returns a tool name and JSON arguments. Your code runs the tool, returns a `tool` message, and the model continues.

**28. Who runs the tool?** Your code, never the model.

**29. How do you stop an agent loop?** Maximum steps, timeouts, and a cost cap.

**30. How do you make tools safe?** Validate arguments, check permissions in code, prefer read-only, and require approval for side effects.

**31. How do you handle long chats?** Sliding window, summaries of older turns, and long-term facts stored outside.

## D. Retrieval (chapters 10 to 13)

**32. What is an embedding?** A vector representing text so that similar meaning gives nearby vectors.

**33. Cosine vs dot vs L2?** Cosine compares direction. Dot product also depends on length (same as cosine when normalised). L2 is straight-line distance.

**34. Why must documents and queries use the same embedding model?** Different models give different spaces, so vectors are not comparable.

**35. Why chunk documents?** Whole-document vectors are blurry, input limits exist, and the prompt should hold only relevant text.

**36. How do you pick chunk size and overlap?** Start at 200 to 500 tokens and 10 to 20 percent overlap, then test recall on a question set.

**37. Why store metadata with chunks?** For citations, filters, tenant isolation and updates.

**38. What is HNSW?** A layered graph index for approximate nearest-neighbour search. High recall, low latency, high memory.

**39. Exact vs approximate search?** Exact compares with all vectors. ANN uses an index, trading a little recall for large speed gains.

**40. pgvector or a dedicated vector DB?** pgvector for simplicity and moderate scale, with data already in Postgres. A dedicated database for larger scale and richer filtering.

**41. How do you update the index when documents change?** Delete the old chunks by document id, insert new ones. If the embedding model changes, re-embed everything into a new collection.

**42. What is BM25?** A keyword scoring function using term frequency with saturation, inverse document frequency and length normalisation.

**43. Why hybrid search?** Keywords catch exact terms, embeddings catch meaning. Together they cover both.

**44. What is RRF?** Merging ranked lists by summing `1 / (k + rank)`, which avoids comparing score scales.

**45. Bi-encoder vs cross-encoder?** A bi-encoder embeds separately and is fast (retrieval). A cross-encoder reads query and passage together and is more accurate (reranking).

## E. RAG and advanced retrieval (chapters 14 to 15)

**46. What is RAG?** Retrieving relevant documents at question time and giving them to the model to ground its answer.

**47. Walk through a RAG pipeline.** Ingest, then per question: embed, retrieve, optionally rerank, build the prompt with numbered sources, generate, return the answer with citations.

**48. How do you cut hallucinations in RAG?** Grounding rule, score threshold, "I do not know" path, low temperature, citations, and faithfulness evals.

**49. A RAG answer is wrong. How do you debug?** Check the retrieved chunks first. If the right chunk is missing, fix retrieval. If present but ignored, fix the prompt or reduce noise.

**50. How do you handle follow-up questions?** Rewrite into a standalone query using chat history.

**51. HyDE?** Embed a model-written hypothetical answer rather than the question.

**52. Parent-child chunking?** Search small chunks, return the larger parent.

**53. Contextual retrieval?** Prefix each chunk with a model-written note of its place in the document before embedding.

**54. When GraphRAG?** Relationship or whole-corpus questions that chunk similarity cannot answer.

**55. Text-to-SQL safely?** Schema in the prompt, read-only user, SELECT only, limits and timeouts, validation.

## F. Evaluation and safety (chapters 16 to 17)

**56. How do you evaluate RAG?** A golden dataset. Retrieval metrics (recall@k, precision@k, MRR) and generation metrics (faithfulness, relevance, correctness), including questions that should be refused.

**57. What is faithfulness?** Every claim in the answer is supported by the retrieved context.

**58. Weaknesses of LLM-as-judge?** Position bias, verbosity bias, self-preference and errors. Use rubrics, swap order, calibrate with human labels.

**59. How do you catch regressions?** Run evals in CI, fail below baseline.

**60. What is prompt injection, and the defences?** Untrusted text containing instructions. Defend with least privilege, no secrets in prompts, labelled data, output filtering, human approval and code-level permission checks.

**61. Direct vs indirect injection?** Direct is typed by the user. Indirect comes through fetched content such as documents, web pages or tool results.

**62. How do you protect personal data?** Mask before sending and logging, tenant filters in retrieval, short retention, and provider data terms.

**63. What are guardrails?** Input and output checks, limits and approvals in code around the model.

## G. Models, cost and operations (chapters 18 to 21)

**64. Prompting, RAG or fine-tuning?** Prompt first. RAG for knowledge. Fine-tuning for behaviour, style and cheap small models.

**65. Why not fine-tune to add knowledge?** It is costly, goes stale, is unreliable for facts and has no citations.

**66. Long context vs RAG?** Long context for a few documents. RAG for large, changing data with citations and lower cost.

**67. What is LoRA?** Training small low-rank adapter matrices on a frozen base model.

**68. What is quantization?** Storing weights in fewer bits to reduce memory and speed up inference with small quality loss.

**69. Self-hosting vs API?** Self-hosting gives data control and fixed cost at huge volume, but needs GPUs and operations. APIs are simpler and cheaper at low volume.

**70. How do you cut cost?** Routing, shorter prompts, output limits, caching, batching and skipping needless calls.

**71. How do you cut latency?** Streaming, smaller models, shorter prompts, parallel steps, caches.

**72. Semantic cache risks?** A loose threshold returns the wrong answer. Stale entries. Sharing across users.

**73. How do you handle high concurrency?** Semaphores and queues, per-user limits, backoff, backpressure.

**74. Multi-tenant isolation?** Mandatory tenant filter in every query or separate collections or databases, plus tests.

**75. What do you trace?** The question, retrieved chunks and scores, the prompt, model and settings, tokens, cost, latency per step, errors and feedback.

## H. Design questions (practise these aloud)

Use the steps: **clarify, estimate, draw the pipeline, name the risks, say how you measure.**

**76. Design a support chatbot over 10,000 documents for 1,000 concurrent users.** Ingest pipeline with a queue and workers. Hybrid search and a reranker. A grounded prompt with citations and a "no answer" path. Streaming responses. Semaphores, rate limits and a cache. Tenant filters. Tracing, evals in CI, cost alerts.

**77. Your RAG gives wrong answers for 15 percent of questions. What do you do?** Build or extend a golden set. Measure retrieval recall first. Read failed cases by category. Fix parsing and chunking, then add hybrid search and reranking, then prompt rules. Re-run the evals after each change.

**78. The LLM bill doubled. What do you check?** Cost per request by feature and model, prompt size growth (chunks, history), retry storms, a looping agent, and cache hit rate. Then apply routing, trimming and caching.

**79. How would you let an LLM answer questions about a company database?** Text-to-SQL with a schema, a read-only user, allow-listed tables, SELECT only, limits, validation, and result explanation. Log queries and evaluate on known questions.

**80. How do you keep users' documents private in a shared RAG?** Tenant id in metadata, a filter in every query enforced in server code, tests for leakage, and masked logs.

## Quick drills (write code, no help)

1. Write `cosine(a, b)` with numpy.
2. Write `call_with_retry` with backoff and jitter.
3. Write `fixed(text, size, overlap)`.
4. Write `rrf(rankings, k=60)`.
5. Write the repair loop for structured output.
6. Write the tool loop with `max_steps`.
7. Write `build_prompt(question, hits)` with numbered sources.
8. Write `recall_at_k` and `mrr`.

Answers: all of these are in this booklet (chapters 10, 5, 11, 13, 7, 8, 14, 16). Try first, then check.
