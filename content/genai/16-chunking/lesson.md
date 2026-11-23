---
title: Chunking
summary: "Learn why long documents are cut into small chunks before embedding, and write three ways to cut them: fixed size with overlap, by paragraph, and by markdown heading."
plan_ids: []
---

Your API docs are long. You cannot embed a whole manual as one vector, and you would not want to. In this lesson you learn to cut documents into **chunks**: small pieces that you embed and search one by one.

Chunking is the most underrated step in a search system. A bad cut gives bad search, and no clever model fixes that later.

## Why chunk?

1. **Model limits.** An embedding model reads only a limited number of tokens (often 512). Extra text is cut off and lost.
2. **Precision.** One vector for a 20-page document is a blurry average of everything in it. One vector for a single paragraph is a sharp point. Search finds sharp points better.
3. **Cost and speed.** In RAG (Level 4) you put the found chunks into the prompt. Small chunks mean fewer tokens, lower cost and a faster answer.

But chunks that are **too small** lose their context. "It returns 404." means nothing without the sentence before it. So you balance:

| Too small | Too big |
| --- | --- |
| Loses context | Blurry vector |
| Many chunks to store and search | Wastes prompt tokens |
| Answer split over several chunks | Hits the model limit |

A common starting point is **200 to 500 words** per chunk (about 800 to 2000 characters). Then you measure and adjust. Level 4 shows how to measure.

## Strategy 1: fixed size with overlap

The simplest way: take the first `size` characters, then the next `size`, and so on.

```python
text = "abcdefghij"
print([text[0:4], text[4:8], text[8:10]])   # -> ['abcd', 'efgh', 'ij']
```

Problem: the cut can land in the middle of a word or a sentence. An answer that sits on the border is split in two halves, and neither chunk has the whole answer.

The fix is **overlap**: each chunk repeats the last few characters of the one before.

```
text:     a b c d e f g h i j
chunk 1:  a b c d
chunk 2:        d e f g          (starts one step back: overlap = 1)
chunk 3:              g h i j
```

Now text near a border appears in two chunks. The price: a little more to store.

The loop is a **sliding window**. The window has a `size`. After each chunk you move the start forward by `step = size - overlap`.

### Step by step: a sliding window over a list

Same pattern as the first exercise, but on a list of numbers instead of text. Goal: `windows(items, size, step)` returns every window of `size` items, moving `step` items each time, until a window reaches the end.

1. Start at position `0`.
2. While the start is before the end of the list: take `items[start:start + size]` and add it to the result.
3. If this window already reached the end (`start + size >= len(items)`), stop. Otherwise a last window would repeat only old items.
4. Move the start forward by `step`.

```python
def windows(items, size, step):
    result = []
    start = 0
    while start < len(items):
        result.append(items[start:start + size])
        if start + size >= len(items):
            break
        start += step
    return result

print(windows([1, 2, 3, 4, 5, 6], 3, 2))   # -> [[1, 2, 3], [3, 4, 5], [5, 6]]
print(windows([], 3, 2))                   # -> []
```

Check it by hand: windows start at 0, 2, 4. The window at 4 is `[5, 6]` and reaches the end, so we stop.

One more rule from real life: if `step` is `0` or negative, the loop never ends. Guard against it. In the exercise `step = size - overlap`, so `overlap` must be smaller than `size`. Raise a `ValueError` for bad values.

> Strings can be sliced like lists: `text[start:start + size]`. A slice past the end is safe. It just gives what is left.

## Strategy 2: by paragraph

Writers already cut their text into paragraphs, separated by a blank line. Each paragraph is usually one idea. That is a natural place to cut.

```python
text = "First idea.\n\nSecond idea.\n\nThird idea."
paragraphs = text.split("\n\n")
print(paragraphs)   # -> ['First idea.', 'Second idea.', 'Third idea.']
```

One paragraph alone can be tiny. So we **pack** paragraphs: put the next paragraph into the same chunk while it still fits in `max_chars`, otherwise start a new chunk.

```python
def pack(items, limit):
    chunks = []
    current = ""
    for item in items:
        if current == "":
            current = item
        elif len(current) + 1 + len(item) <= limit:
            current = current + " " + item     # +1 for the space
        else:
            chunks.append(current)
            current = item
    if current:
        chunks.append(current)
    return chunks

print(pack(["aa", "bb", "cc", "dd"], 5))   # -> ['aa bb', 'cc dd']
```

Notice the last two lines: after the loop, the chunk you were still building must be added. Forgetting this loses the end of the document. It is a very common bug.

A paragraph longer than the limit stays alone in its own chunk. Splitting it further is a job for strategy 1.

## Strategy 3: by structure (markdown headings)

API docs are written in markdown. Headings (`#`, `##`, `###`) mark topics:

```markdown
# Tasks

## Create a task
Send a POST request to `/tasks`.

## Delete a task
Send DELETE to `/tasks/{id}`.
```

Cutting at headings gives one chunk per topic, and each chunk knows its **heading**. That heading is gold: you can store it next to the chunk and show it in a citation later ("Tasks / Delete a task"). Some systems even add the heading text before the chunk text before embedding, so the vector knows the topic.

How to find a heading line: it starts with 1 to 6 `#` characters followed by a space.

```python
def is_heading(line):
    stripped = line.lstrip("#")
    level = len(line) - len(stripped)
    return 1 <= level <= 6 and stripped.startswith(" ")

print(is_heading("## Delete a task"))   # -> True
print(is_heading("#hashtag"))           # -> False
print(is_heading("plain text"))         # -> False
```

**A trap:** code blocks. In a Python code example, `# this is a comment` starts with `#` and a space, so it looks like a heading! Code blocks are fenced with three backticks. Lines between the fences are never headings.

````markdown
## Example
```python
# not a heading, just a comment
x = 1
```
````

Keep a flag `in_fence`. Flip it each time you see a line that starts with three backticks. Only look for headings when `in_fence` is `False`.

## Metadata: remember where each chunk came from

A chunk is more than text. Each chunk should carry:

- `source`: the file it came from (`tasks.md`).
- `heading`: the section.
- `id`: a stable unique name, like `tasks.md:3`.

Without this you cannot show citations later. Store this **metadata** from day one. It costs nothing now and is painful to add afterwards.

```python
chunk = {"id": "tasks.md:0", "source": "tasks.md", "heading": "Delete a task", "text": "Send DELETE to /tasks/{id}."}
```

## Putting the strategies together

A real chunker joins the strategies. First cut by structure (headings). Then, inside each section, pack paragraphs up to a size limit. Each chunk gets an **id** and remembers its **source** and **heading**.

Let's practise the pattern with a different example: number the words of several sentences, and remember which sentence each came from.

1. Make an empty list `items`.
2. Loop over the sentences. For each one, loop over its words.
3. Add a dictionary with an id that counts over **everything** (use `len(items)`), the word and the sentence number.

```python
def number_words(sentences):
    items = []
    for s, sentence in enumerate(sentences):
        for word in sentence.split():
            items.append({"id": f"w{len(items)}", "word": word, "sentence": s})
    return items

number_words(["hi there", "bye"])
# -> [{'id': 'w0', 'word': 'hi', 'sentence': 0},
#     {'id': 'w1', 'word': 'there', 'sentence': 0},
#     {'id': 'w2', 'word': 'bye', 'sentence': 1}]
```

Notice that `len(items)` gives a counter that does not restart inside the inner loop. The fourth exercise needs the same trick for chunk ids.

## Try it live

1. Take one real markdown file (this project's `reference/genai-groq.md` is a good one). Chunk it three ways: fixed 300 characters with overlap 50, by paragraph, and by heading.
2. Print the number of chunks and the shortest and longest chunk for each way.
3. Pick 3 questions about the file. For each one, find by eye which chunk should answer it in each way. Which way keeps the answer in one piece?

## A little deeper

- **Characters vs tokens.** Models count tokens, not characters. About 4 characters per token for English. Real systems often chunk by tokens with a tokenizer. Characters are fine to start with.
- **Overlap size.** 10 to 20% of the chunk size is common. More overlap means more duplicated storage and sometimes duplicate results.
- **Sentence-based chunking.** Split on sentence ends so no sentence is cut. Needs care with "e.g." and "v1.2".
- **Semantic chunking.** Embed each sentence and cut where the meaning changes. It can improve quality but is slower and more complex. Test whether it beats headings on your data.
- **Parent-child chunks.** Search small chunks (sharp), but give the model the bigger parent section (more context). A popular trick.
- **Tables, code and JSON** need special care. Never cut a code block or a table row in the middle.
- **Contextual prefix.** Adding "Document: Tasks API. Section: Delete a task." before each chunk helps the vector and the reader.
- **Deduplication.** The same text in two files makes duplicate results. Hash chunk texts and drop repeats.
- **There is no best size.** Build an evaluation set (Level 4), try 3 sizes and keep the one with the best retrieval.

## Common mistakes

- Chunks too big or too small, without ever testing.
- No overlap, so answers on a border are split.
- Forgetting to add the last chunk after the loop.
- An infinite loop when `overlap >= size`.
- Treating `#` comments inside code blocks as headings.
- Throwing away metadata (source, heading).
- Changing the chunking and not re-embedding. Chunks and vectors must always match.

## Interview corner

**Why do we chunk documents for RAG?**
Embedding models have an input limit, one vector for a long text is blurry, and the prompt has a limited and costly context. Small, focused chunks give sharper search and cheaper prompts.

**How do you choose a chunk size?**
Start near 200 to 500 words, then measure retrieval quality on a set of real questions and adjust. It depends on the data and the model. There is no universal best.

**What is overlap for?**
So that text near a border is fully inside at least one chunk. Typical overlap is 10 to 20%.

**What chunking would you use for API docs?**
Split by markdown headings (structure-aware), then split long sections by paragraph or size. Keep the source and heading as metadata for citations.

## Summary

- Chunk before embedding: model limits, sharper vectors, cheaper prompts.
- Fixed size + overlap is a sliding window with `step = size - overlap`. Guard against `overlap >= size`.
- Paragraph packing joins small paragraphs up to a limit. Add the last chunk after the loop.
- Markdown headings are the best natural cuts for docs. Ignore `#` lines inside code fences.
- Keep metadata with each chunk: `id`, `source`, `heading`, `text`.
- Project: step 9 adds `copilot/chunking.py` and `copilot/ingest.py`.
- Reference: `reference/genai-retrieval.md`.
