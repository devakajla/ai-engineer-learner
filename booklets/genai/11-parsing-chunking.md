# 11. Reading documents and chunking

A RAG system is only as good as the text you feed it. Real knowledge lives in PDFs, web pages, Word files and tables, not in clean strings. This chapter covers two jobs: **parsing** (getting text out) and **chunking** (cutting it into good pieces). Chunking quality decides retrieval quality more than most people expect.

## Why we cut documents into chunks

You could embed a whole document as one vector, but:

- A vector for 50 pages is a **blurry average** of many topics. It matches nothing precisely.
- Embedding models have an **input limit**, so long text is cut anyway.
- You want to put **only the relevant paragraph** in the prompt, not 50 pages (cost and focus, chapter 2).

So we split each document into **chunks**, embed each chunk, and retrieve the best chunks for a question.

@@ flow | Figure 11.1: the ingestion pipeline.
Source files|PDF, HTML, docs, text|gray -> Parse|extract clean text;keep titles and tables|blue -> Chunk|cut into pieces;add metadata|yellow -> Embed|one vector per chunk|green -> Store|vector database|purple
@@ end

## Parsing: getting text out

| Source | Common tool | Watch out for |
| --- | --- | --- |
| text and Markdown | `Path.read_text()` | encodings |
| HTML | BeautifulSoup | menus, ads, scripts mixed into the content |
| PDF | `pypdf`, `pdfplumber`, `PyMuPDF` | columns read in the wrong order, headers and footers repeated on every page |
| scanned PDF or image | OCR (for example Tesseract) | recognition mistakes |
| tables | `pdfplumber`, or convert to Markdown | a table flattened into nonsense text |
| Word and slides | `python-docx`, `python-pptx` | hidden or formatted text |

(The tools above are the usual choices. They were not run in this booklet.)

A PDF example:

```python
from pypdf import PdfReader

reader = PdfReader("handbook.pdf")
pages = [page.extract_text() for page in reader.pages]
```

Principles for parsing:

- **Always read the parsed text with your own eyes.** Broken parsing is the number one hidden RAG bug. A table turned into "Plan Price Basic 5 Pro 15" loses its meaning.
- **Keep structure** where you can: headings, list items, page numbers. Markdown is a good middle format, because headings survive.
- **Remove noise**: repeated headers and footers, page numbers, navigation text.
- **Keep metadata**: file name, title, page number, section, date, URL. You will need it for citations (chapter 14) and for filters (chapter 12).

## Chunking strategies

### 1. Fixed size

Cut every N characters (or tokens). Simple, predictable, but it can cut a sentence in half.

```python
def fixed(text, size, overlap):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + size])
        if i + size >= len(text):
            break
        i += size - overlap
    return chunks

print(fixed("abcdefghij", 4, 1))
# -> ['abcd', 'defg', 'ghij']
```

Follow it: each chunk starts `size - overlap` = 3 characters after the previous start, so `d` and `g` appear in two chunks each.

### Overlap

**Overlap** repeats the end of one chunk at the start of the next. If a key sentence sits on a cut, one of the two chunks still contains it whole. Typical overlap is 10 to 20 percent of the size. Too much overlap wastes storage and creates near-duplicates in results.

### 2. By structure (recursive splitting)

Better: split at the **biggest natural boundary first** (a blank line, then a line break, then a sentence end, then a space), and only go smaller when a piece is still too big. Paragraphs stay whole.

```python
def split_recursive(text, max_chars, seps=("\n\n", "\n", ". ", " ")):
    if len(text) <= max_chars:
        return [text]
    for sep in seps:
        if sep in text:
            parts = text.split(sep)
            chunks, current = [], ""
            for part in parts:
                piece = part if not current else current + sep + part
                if len(piece) <= max_chars:
                    current = piece
                else:
                    if current:
                        chunks.append(current)
                    if len(part) > max_chars:      # still too big: use a smaller separator
                        chunks.extend(split_recursive(part, max_chars, seps[seps.index(sep) + 1:]))
                        current = ""
                    else:
                        current = part
            if current:
                chunks.append(current)
            return chunks
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
```

Run on a small two-section document with a limit of 80 characters:

```python
doc = ("# Refunds\n\nYou can ask for a refund within 30 days. Send us your order number."
       "\n\n# Shipping\n\nOrders ship in 2 days. Tracking is sent by email.")
for chunk in split_recursive(doc, 80):
    print(repr(chunk))
# -> '# Refunds\n\nYou can ask for a refund within 30 days. Send us your order number.'
# -> '# Shipping\n\nOrders ship in 2 days. Tracking is sent by email.'
```

The two sections came out as two clean chunks, each with its heading. The code tries `"\n\n"` first, and packs paragraphs together while they fit. Only an oversized paragraph is split further. Libraries such as LangChain offer the same idea as `RecursiveCharacterTextSplitter`.

### 3. By document structure

For Markdown or HTML, split by **headings**, so each chunk is one section, and put the heading path ("Billing > Refunds") at the top of the chunk. This is often the best quality for manuals and docs.

### 4. Semantic chunking

Embed sentences, and start a new chunk where the meaning changes (the similarity of neighbouring sentences drops). It can give very coherent chunks, but costs extra embedding work, and does not always beat simple structure-based splitting. Try it only when the simpler ways fail.

### 5. Parent and child chunks (the idea)

Search on **small** chunks (precise matching), but give the model the bigger **parent** section around the match (more context). Chapter 15 returns to this.

## How big should a chunk be?

There is no magic number. Common starting points are **200 to 500 tokens** with 10 to 20 percent overlap.

| Too small | Too big |
| --- | --- |
| loses context ("it", "this plan" mean nothing) | blurry vectors, off-topic text wastes the prompt |
| many chunks, more storage | fewer pieces fit in the context |

Choose by **testing**: build a small question set (chapter 16) and compare recall at a few sizes.

## Add context to chunks

A chunk that says "It costs 15 dollars" is useless alone. Prefix every chunk with its source and heading:

```python
def make_chunk(title, section, body, page):
    text = f"{title} > {section}\n{body}"
    return {"text": text, "metadata": {"title": title, "section": section, "page": page}}

chunk = make_chunk("Pricing", "Pro plan", "It costs 15 dollars per month.", 4)
print(chunk["text"])
# -> Pricing > Pro plan
# -> It costs 15 dollars per month.
```

The heading text is embedded with the body, so the vector knows what "it" is. The `metadata` stays **beside** the text, to filter and to cite.

::: {.box .checkpoint}
**Checkpoint:** you can explain what overlap protects against, why recursive splitting beats fixed size, and why metadata is stored with every chunk.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Never looking at the parsed text, and indexing garbage.
- One giant chunk per document.
- Cutting in the middle of sentences or tables.
- Chunks with no heading or source, so "it" has no meaning.
- Dropping metadata, which makes citations impossible.
- Choosing a chunk size once and never testing alternatives.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Why chunk documents for RAG?** Embeddings of long text are blurry, models have input limits, and the prompt should hold only relevant text.

**Q: What is chunk overlap?** Repeating the end of a chunk at the start of the next so that content on a boundary is not lost.

**Q: How do you choose chunk size?** Start with 200 to 500 tokens, and compare retrieval metrics on a test set for several sizes.

**Q: Recursive vs fixed-size chunking?** Recursive splits on natural boundaries (paragraphs, sentences) so meaning stays together. Fixed-size cuts anywhere.

**Q: What are the usual PDF problems?** Wrong reading order of columns, repeated headers and footers, tables flattened to text, and scans that need OCR.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Chunk a text file of your own with `fixed(text, 300, 50)` and print the first two chunks.
2. Run `split_recursive` on a Markdown file. Do headings stay with their text?
3. Write `with_overlap(chunks, n)` that adds the last `n` characters of the previous chunk to the next one.
4. Write a splitter that cuts a Markdown file at every line starting with `#`, and keeps the heading as the first line of each chunk.
5. Parse a PDF of your choice and read the first page of text. Write down three problems you see.
6. **Think:** why would a chunk of size 1 (a single sentence) retrieve precisely but answer badly?
:::
