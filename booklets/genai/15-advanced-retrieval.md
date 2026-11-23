# 15. Advanced retrieval

Basic RAG (chapter 14) works for simple questions. Real questions are messy. This chapter lists the standard upgrades. Add them **one at a time**, and keep one only if your evaluation (chapter 16) shows a gain. Complexity has a cost.

## Problem 1: the question is a bad search query

Users write short, vague or follow-up questions: "and the price?", "it does not work". The document says something different.

### Query rewriting

Ask a small model call to **rewrite** the question into a standalone search query, using the chat history.

```python
def rewrite(client, history_text, question):
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        max_completion_tokens=60,
        messages=[
            {"role": "system", "content": "Rewrite the last question as one standalone search query. Use the chat for context. Reply with the query only."},
            {"role": "user", "content": f"Chat:\n{history_text}\n\nLast question: {question}"},
        ],
    )
    return response.choices[0].message.content.strip()
# chat: "tell me about the Pro plan" ... question: "and the price?"
# -> Pro plan price
```

(The example result is illustrative: a model would produce something like it.) One extra short call fixes the follow-up problem.

### Multi-query

Make the model write 3 different versions of the question, retrieve for **each**, and merge the lists with RRF (chapter 13). Different wordings hit different chunks, so recall goes up. Cost: more retrieval and one more call.

### HyDE (hypothetical document embeddings)

Questions and answers look different, so a question vector may sit far from the answer's vector. HyDE asks the model to **write a fake answer first**, and embeds **that** to search. The fake answer may be wrong, but it **looks like** the real documents, so it lands nearby. Use it when queries are short and documents are long.

## Problem 2: chunks lose their context

### Contextual retrieval

Before embedding, ask a model to write a **one-line summary of where the chunk sits** in its document ("This chunk is from the 2024 refund policy, in the section about digital goods") and put it in front of the chunk. The vector then knows the context that the bare chunk lacks. It costs one call per chunk at ingest time, once.

### Parent and child chunks

Search over **small chunks** (precise), but return the **parent** (the full section or page) to the model for context. Store a `parent_id` in the metadata and look the parent up after retrieval.

@@ flow | Figure 15.1: small to find, big to read.
Small chunks|embedded and searched|blue -> Best small chunk|found by similarity|yellow -> Parent section|sent to the model|green
@@ end

## Problem 3: the answer is spread over many places

### Multi-hop questions

"Which team owns the service that the billing API calls?" needs two lookups: the billing API, then its dependency. The first retrieval is not enough. The standard answer is an **agent loop** (retrieve, think, retrieve again), covered in the Agentic AI booklet.

### GraphRAG (the idea)

Extract **entities and relations** from documents into a graph (for example "Service A calls Service B"), and also build **summaries of communities** in the graph. Questions that need the **big picture** ("what are the main themes across all tickets?") or **relationship paths** can then be answered better than with chunk search. It is powerful but costly to build, so use it only for questions that plain chunks cannot answer.

## Problem 4: the data is a table, not text

### Text-to-SQL

For structured data ("how many orders did we get last week?"), searching text is the wrong tool. Give the model the **table schema**, let it write a SQL query, **run it safely**, and let it explain the result.

@@ flow | Figure 15.2: text to SQL.
Question|"orders last week?"|blue -> Model + schema|writes a SQL query|yellow -> Safety check|read-only, allow-listed tables|red -> Database|runs the query|purple -> Answer|explained rows|green
@@ end

Safety is the main danger. Use a **read-only** database user, allow only `SELECT`, add a row limit and a timeout, and check the query before running it. Never run model-written SQL with write rights.

A tiny, safe-by-design guard:

```python
def is_safe_select(sql):
    text = sql.strip().lower().rstrip(";")
    forbidden = ("insert", "update", "delete", "drop", "alter", "create", "attach", "pragma")
    return text.startswith("select") and ";" not in text and not any(w in text for w in forbidden)

print(is_safe_select("SELECT count(*) FROM orders"))
# -> True
print(is_safe_select("SELECT 1; DROP TABLE orders"))
# -> False
```

This guard alone is **not enough** (it is a first line only). The real protection is the read-only database user.

## Other upgrades in one table

| Technique | Helps with | Cost |
| --- | --- | --- |
| metadata filters | restricting by product, date, tenant | cheap; needs good metadata |
| reranking | order inside the top candidates | extra latency |
| query rewriting | follow-ups, vague queries | one small call |
| multi-query | wording mismatch | several retrievals |
| HyDE | short query vs long documents | one call |
| contextual chunks | chunks that lack context | ingest cost |
| parent-child | needing more context | more storage logic |
| GraphRAG | big-picture and relationship questions | high |

## Which to try first

1. Fix parsing and chunking (chapter 11). It is the highest gain.
2. Add hybrid search and a reranker (chapter 13).
3. Rewrite follow-up questions.
4. Add metadata filters.
5. Only then, the rest, and **measure each**.

::: {.box .checkpoint}
**Checkpoint:** for each of "vague follow-up", "chunk lacks context" and "table data", you can name the technique.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Adding five techniques at once, so you cannot tell what helped.
- Building GraphRAG before simple fixes were tried.
- Letting a model run write-capable SQL.
- Rewriting queries without the chat history.
- Returning the whole parent for every hit, which blows up the prompt.
- No measurement, so techniques are chosen by fashion.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you handle follow-up questions in RAG?** Rewrite the question into a standalone query using the chat history before retrieval.

**Q: What is HyDE?** Generate a hypothetical answer with the model, then embed it to search, because it resembles real documents more than the question does.

**Q: What is parent-child chunking?** Retrieve with small chunks for precision, then return the larger parent section for context.

**Q: What is contextual retrieval?** Add a short, model-written description of a chunk's place in its document before embedding it.

**Q: When would you use GraphRAG?** For relationship-heavy or whole-corpus questions where chunk similarity is not enough.

**Q: How do you do text-to-SQL safely?** Give the schema, use a read-only user, allow only SELECT, add limits and timeouts, and validate before running.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write `rewrite` and test it with a fake client. Check the prompt contains the chat history.
2. Write `multi_query(client, question)` that returns three rewrites, one per line, as a list.
3. Merge the results for three queries using `rrf` from chapter 13.
4. Extend `is_safe_select` to reject comments (`--`). Why might comments be dangerous?
5. Sketch a schema for parent and child chunks (which fields in metadata?).
6. **Think:** which technique would you add for the question "summarise the main complaints across all 5,000 tickets"?
:::
