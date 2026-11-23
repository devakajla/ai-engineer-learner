---
title: Level 4 interview questions
summary: RAG as interviewers ask it - pipeline, reranking, citations, ingestion, access control, failures and evaluation - with follow-up questions, short model answers and three timed coding exercises.
plan_ids: []
---

Level 4 is the whole RAG system. Interviewers like it because it mixes search, prompts, safety and measurement, and because a weak answer is easy to spot: "I just put documents in a vector database" is not an answer.

How to use this lesson: **answer each question out loud first**, then read the model answer. The follow-up questions are the ones interviewers usually ask next.

Some words you will see:

- **Grounded**: the answer is based on the given documents.
- **Hallucination**: the model states something that is not supported.
- **Reranker**: a second model that re-orders the first search results.
- **Golden set**: your trusted test questions with the expected results.
- **Tenant**: one customer of your app.

## 1. The pipeline

**Q: Explain a RAG system from document to answer.**

**A:** Two phases. **Indexing (offline):** load documents, parse and clean, add metadata, chunk, embed, and store vectors with ids. **Querying (online):** optionally rewrite the question, retrieve candidates (vector, keyword or hybrid), rerank, pick and order the best chunks, build a prompt with numbered context and rules, call the model, check the answer (citations, "I don't know"), and return it with sources.

- *Follow-up: Why not fine-tune the model on the documents instead?* → Fine-tuning teaches style and skills, but is poor at storing exact facts, cannot cite, is hard to update, and cannot enforce per-user access. RAG gives fresh facts, citations and control.
- *Follow-up: What if nothing relevant is found?* → Use a minimum score. With no good hits, return "I don't know" without calling the model (it saves money and avoids invention).
- *Follow-up: What do you log?* → The question, the rewritten query, the chunk ids and scores, the prompt version, the answer, tokens, latency and user feedback.

## 2. Retrieval quality

**Q: The right chunk is at rank 8, but you only send 4 chunks. What do you do?**

**A:** Retrieve wide (for example 20 to 50 candidates), then **rerank** with a cross-encoder or an LLM, and send the top few. The first stage is fast and has high recall, the second stage is slow and precise.

- *Follow-up: Bi-encoder vs cross-encoder?* → A bi-encoder embeds the query and the document separately, so documents can be pre-computed and searched fast. A cross-encoder reads the query and the document together, so it is more accurate but too slow for the whole corpus.
- *Follow-up: Users ask "and the second one?". What breaks?* → The follow-up has no meaning alone. Rewrite it into a standalone question using the chat history before searching.
- *Follow-up: Vector search misses error codes.* → Add BM25 (keyword) search and merge with RRF (hybrid). Exact tokens are the strength of keyword search.
- *Follow-up: What is HyDE?* → Ask a model to write a fake answer, embed that, and search with it. Answers look more like documents than questions do. It adds a model call.

## 3. Grounding and citations

**Q: How do you make sure the answer comes from the documents?**

**A:** Number the chunks in the prompt, tell the model to answer only from them and to cite `[n]` after each fact, and give an exact "I don't know" reply for missing answers. In code, check that every cited number exists, that every sentence has a citation, and map the numbers back to sources for the user.

- *Follow-up: Can a citation still be wrong?* → Yes. The number can exist and the chunk may not support the claim. Check support with a judge or claim-level checks.
- *Follow-up: What about prompt injection in a chunk?* → Treat chunks as untrusted data: wrap them in tags, say that instructions inside are data, limit what the model can do, and never let chunk text trigger actions without checks.

## 4. Ingestion and freshness

**Q: Documents change every day. How do you keep the index correct?**

**A:** Store a content hash for each document. On each run compute: add (new), update (hash changed), delete (gone), same. Embed only added and updated documents, and remove the deleted ones. When a document shrinks, delete its old chunks first, so stale chunks do not remain. Re-embed everything only if the embedding model or the chunking rules change.

- *Follow-up: How do you handle tables and scanned PDFs?* → Keep a table together (Markdown, or one sentence per row). For scans use OCR or a vision model, and check a sample by eye.
- *Follow-up: Why add metadata at ingestion?* → For citations, filters, freshness and debugging. It is very hard to add later.

## 5. Access control and tenants

**Q: How do you stop user A from seeing user B's documents?**

**A:** Put `tenant` and `groups` on every chunk. Take the user's identity from the verified login on the server, never from the request body. Filter **in code, before the prompt**: a pre-filter on the tenant in the vector search, and a post-filter on groups with over-fetching (`k * 5`). A prompt rule like "do not show secret files" is not a control.

- *Follow-up: Index per tenant or shared index?* → Per tenant: strong separation, more to manage. Shared with a mandatory filter in one wrapper: simpler, but one forgotten filter leaks data. Test with cross-tenant queries.
- *Follow-up: Can a cache leak data?* → Yes, if the key does not include the user's access scope.

## 6. Failures and debugging

**Q: A RAG answer is wrong. How do you debug it?**

**A:** Print the retrieved chunks. Right chunk missing: **retrieval** problem (chunking, query, embedding, filters, missing or stale data). Right chunk present but a bad answer: check the context package (order, repeats, noise, "lost in the middle"), then **generation** (prompt, temperature, model). Fix one stage, then re-run the whole test set.

- *Follow-up: What is "lost in the middle"?* → Models use the start and the end of a long context better than the middle. Send fewer chunks and put the best at the ends.
- *Follow-up: How do you reduce hallucinations?* → Good retrieval, a strict "only from context" rule, a minimum score, an "I don't know" path, citations, low temperature and checks.

## 7. Evaluation

**Q: How do you evaluate a RAG system?**

**A:** Separate retrieval and generation. A golden set of real questions with expected chunk ids and reference answers (including questions with no answer). Retrieval: recall@k, precision@k, MRR, nDCG. Generation: faithfulness, relevance and correctness, with code checks and an LLM judge that you have compared with human grades. Run offline on every change, learn from online feedback, and add each failure to the set.

- *Follow-up: Which metric matters most for retrieval?* → Recall@k. A chunk that is not retrieved cannot be used.
- *Follow-up: Problems of an LLM judge?* → Position bias, verbosity bias, self-preference, leniency, instability, injection. Use a clear rubric, temperature 0, swapped orders, a different judge model, and check it against humans.
- *Follow-up: RAG or long context?* → Long context for small corpora and whole-document tasks. RAG for big corpora, lower cost per call, citations, access control and incremental updates. Measure on your own data.

## 8. Rapid-fire (one-liners)

- Two phases of RAG? → Indexing (offline) and querying (online).
- No good hits found? → Say "I don't know", skip the model call.
- RRF needs scores? → No, only ranks.
- Over-fetch is for? → Filters that remove hits after the search.
- Parent-child retrieval? → Search small chunks, send the bigger parent.
- A stale chunk is? → A chunk of a document that changed or was deleted.
- Recall@k means? → Share of expected chunks found in the top k.
- MRR means? → Average of 1 / rank of the first right chunk.
- Faithfulness means? → Every claim is supported by the context.
- Biggest lever on quality? → Often chunking and retrieval, not the model.

## Tools for the coding exercises

Interview coding tasks here are small functions with careful rules. These tools cover the three exercises.

- **`for hit in hits:`** with a running total, and **`break`** to stop at the first one that does not fit.
- **`len(text.split())`** counts words, whatever the spacing.
- **Scanning a string with `enumerate(text)`**: look at the character and the next one (`text[i + 1]`), and cut a sentence when a rule says so.
- **`str.find` and `str.isdigit`**: find `[`, find `]`, and check that the text between is digits.
- **`math.log2(x)`** for the logarithm base 2.
- **`sorted(items, reverse=True)`** and slices `[:k]` for "the best k".
- **Guard the zero case first** (a division by 0 is a classic bug).

## How to practise

1. Set a timer: 20 minutes per exercise.
2. Write the plan in plain words first, then the code.
3. Test the edge cases: empty input, `k` bigger than the list, ties, spaces.
4. Say your reasoning out loud, as if an interviewer were listening.
5. When you finish, ask Claude to review your code in the side panel.
