# 14. The RAG pipeline, end to end

**RAG** means **Retrieval-Augmented Generation**. Plain words: *look up the facts first, then let the model write the answer using them.*

## Why RAG exists

A model alone has three problems for company or product questions:

- It does **not know** your private data (your docs, your tickets).
- Its knowledge has a **cutoff date**, so it is out of date.
- When it does not know, it may **make something up** (hallucination).

RAG fixes this by handing the model the right text **at question time**. Think of an open-book exam: the student (the model) is clever, and the book (your documents) holds the facts.

## The two halves

@@ flow | Figure 14.1: offline (prepare once) and online (every question).
Ingest|parse, chunk, embed, store|gray -> Index|vector DB + metadata|purple
@@ end

@@ flow | Figure 14.2: what happens for each question.
Question|user text|blue -> Retrieve|top chunks from the index|yellow -> Build prompt|rules + chunks + question|green -> Generate|LLM writes the answer|purple -> Answer + sources|with citations|blue
@@ end

Chapters 10 to 13 built the first half and the retrieve step. This chapter joins everything.

## Step 1: retrieve

Embed the question, search the index, take the top K chunks. Keep the **score** of each hit, because you will use it (see "no answer" below). A typical K is 3 to 8.

## Step 2: build the prompt

The prompt has three parts: **rules**, **sources** (numbered, with their file names), and the **question**.

```python
def build_prompt(question, hits):
    context = "\n\n".join(
        f"[{i}] ({chunk['source']})\n{chunk['text']}"
        for i, (chunk, score) in enumerate(hits, start=1)
    )
    return (
        "Answer using ONLY the numbered sources. Cite like [1]. "
        "If the sources do not answer it, say: I do not know.\n\n"
        f"Sources:\n{context}\n\nQuestion: {question}"
    )
```

What it does: each chunk becomes a block that starts with its number `[1]`, `[2]` and its source file. `enumerate(..., start=1)` gives the numbers. The instruction tells the model to use **only** these sources, to cite by number, and gives it a permitted way out ("I do not know"), as chapter 6 taught.

## Step 3: generate, and read the citations

Because the sources are numbered, the model can write "...within 30 days [1]". Your code reads the numbers, and maps them back to real files. We ran this with the toy embedder (chapter 10), three chunks, and a fake model:

```python
import re

def answer(client, question, min_score=0.2):
    hits = [h for h in retrieve(question) if h[1] >= min_score]
    if not hits:
        return {"answer": "I do not know.", "sources": []}

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": build_prompt(question, hits)}],
        temperature=0,
    )
    text = response.choices[0].message.content
    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text) if 1 <= int(n) <= len(hits)})
    return {"answer": text, "sources": [hits[n - 1][0]["source"] for n in cited]}
```

Results of two test calls:

```
answer(fake, "can I get a refund of my money back")
# -> {'answer': 'Within 30 days you can get your money back [1].', 'sources': ['refund.md']}

answer(fake, "what is the weather")
# -> {'answer': 'I do not know.', 'sources': []}      (and the model was never called)
```

Walk through it:

1. `retrieve` returns `(chunk, score)` pairs. We **drop low scores** with `min_score`. If nothing is good enough, we answer "I do not know" **without calling the model at all**. That saves money, and it avoids an invented answer built on irrelevant text.
2. We call the model at temperature 0 for a faithful answer.
3. The regular expression `\[(\d+)\]` finds citation numbers like `[1]`. We keep only numbers that really exist (1 up to the number of hits), because a model can cite `[7]` when there are 3 sources. The valid ones are turned back into source files.

This is the **whole** RAG idea. A real system adds better chunking, hybrid search, reranking, and evaluation, but the shape stays the same.

## Grounding and citations

**Grounded** means every claim in the answer can be traced to a source. Citations are how users (and you) check. Good practice:

- Number the sources, and ask for `[n]` after each claim.
- Return the **source list** with file name, page or URL next to the answer, so the UI can show links.
- **Verify** citations in code (as above). A deeper check asks a second model: "does source 1 support this sentence?"
- Quote the exact text when stakes are high ("answer, then the supporting quote").

## The "no answer" path

A good RAG system knows when **not** to answer. Three layers:

1. **Retrieval threshold:** nothing scored well, so say so (above).
2. **Prompt rule:** "if the sources do not answer, say I do not know".
3. **Evaluation:** include questions with no answer in your test set (chapter 16), and check that the system refuses them.

An honest "I do not know" is far better than a confident wrong answer.

## Putting history and RAG together

In a chat, the follow-up "and what about shipping?" is not a good search query alone. Rewrite it using the history ("what is the shipping policy?") before retrieval. That is query rewriting (next chapter).

## Cost and size of the prompt

Prompt size = rules + K chunks + history + question. Five chunks of 400 tokens is already 2,000 tokens in **every** request. Chapter 2 shows how this multiplies. Keep K small, rerank to pick the best few, and watch the numbers.

## Where RAG goes wrong

| Symptom | Likely cause |
| --- | --- |
| answer ignores the docs | the prompt does not demand grounding, or temperature is high |
| right doc exists but not found | bad chunking, weak embedder, no hybrid search |
| found, but wrong part used | too many chunks, "lost in the middle" |
| confident wrong answer | no threshold, no "I do not know" rule |
| stale answers | old chunks never deleted or re-indexed |

When RAG is bad, **first check retrieval**. Print the chunks that were retrieved. Most "the model is bad" problems are really "we gave it the wrong text".

::: {.box .checkpoint}
**Checkpoint:** you can draw both halves of the pipeline, write the prompt builder, and explain why the model is not called when no chunk scores well.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Blaming the model before reading the retrieved chunks.
- No instruction to use only the sources.
- No score threshold, so unrelated chunks reach the model.
- Trusting citations without checking that the numbers exist.
- Stuffing 20 chunks into the prompt.
- Forgetting to re-index after documents change.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is RAG and why use it?** It retrieves relevant documents at query time and gives them to the model, so answers use private, current data and hallucinate less.

**Q: Describe a RAG pipeline.** Ingest (parse, chunk, embed, store). Per question: embed the query, retrieve top K (hybrid plus rerank), build a prompt with numbered sources, generate, return the answer with citations.

**Q: How do you reduce hallucination in RAG?** Grounding instructions, a score threshold, an allowed "I do not know", low temperature, citations, and evaluation of faithfulness.

**Q: How do you debug a bad RAG answer?** Look at the retrieved chunks first. If the right chunk is missing, fix retrieval (chunking, embedder, hybrid search). If present but ignored, fix the prompt or reduce noise.

**Q: Why return citations?** Users and developers can verify claims, and it builds trust.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Build the toy pipeline with your own five documents. Print the prompt for one question.
2. Add a `min_score` and test a question outside your documents. Is the model called?
3. Make `answer` ignore citation numbers that are out of range, and test with a fake that says `[9]`.
4. Add the sources' file names under the answer as a list.
5. Write a test with a fake client and check that the prompt contains the retrieved chunk's text.
6. **Think:** why is "I do not know" a feature and not a failure?
:::
