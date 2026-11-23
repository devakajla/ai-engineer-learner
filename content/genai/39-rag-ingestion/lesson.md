---
title: "RAG ingestion: parsing, cleaning and incremental updates"
summary: Get real documents (PDF, HTML, tables) into your index cleanly, and keep the index up to date by re-embedding only what changed.
plan_ids: []
---

In Level 3 your documents were tidy markdown files. Real companies have PDFs, web pages, spreadsheets, wiki exports and scanned papers. **Ingestion** is the work of turning all of that into clean chunks in your index. It is the least glamorous part of RAG, and often the one that decides if the whole system is good.

The rule is old and always true: **garbage in, garbage out**. If the text in your index is broken, no clever prompt or reranker can fix the answers.

## The ingestion pipeline

```
source -> load -> parse -> clean -> add metadata -> chunk -> embed -> upsert
```

Each stage has its own job:

| Stage | Job | Example problem |
| --- | --- | --- |
| **Load** | Get the raw file or page | Login needed, rate limits, files too big |
| **Parse** | Turn the format into text and structure | PDF has two columns, so the text reads across them |
| **Clean** | Remove noise | Page numbers, menus, cookie banners, double spaces |
| **Metadata** | Keep facts about the document | source, title, page, url, updated date |
| **Chunk** | Cut into pieces (lesson 16) | Cutting a table in half |
| **Embed** | Make vectors (lesson 14) | Wrong model, no prefix |
| **Upsert** | Store by a stable id (lesson 17) | Duplicates after a re-run |

## Parsing different formats

- **Markdown and plain text.** Easy. Split on headings.
- **HTML.** The page has navigation, footers, scripts and ads around the real text. Keep only the main content. (Libraries such as `trafilatura` or `beautifulsoup4` do this. Check their docs. Here you just need the idea.)
- **PDF with a text layer.** A library (for example `pypdf`) can read the text. Problems: text of two columns gets mixed, headers and footers repeat on each page, words are broken with hyphens at line ends.
- **Scanned PDF or image.** There is no text, only pictures. You need **OCR** (optical character recognition) to read it. Modern vision models (lesson 38) can also do it. OCR makes mistakes, so check a sample.
- **Tables.** A table cut into plain text loses its meaning (which number belongs to which column?). Better: keep a table as one chunk, in Markdown form, or write each row as a sentence: `"Plan: Pro. Price: 20 USD."`
- **Code and config.** Split by function or file, not by character count.
- **Office files, email, chat exports.** Convert to text, keep the author, date and thread as metadata.

> Tools in this area change quickly (`unstructured`, `docling`, `pypdf` and others). Look at their current docs and test them on **your** files. A parser that is great on clean papers can be poor on your scanned forms.

## Cleaning text

Even good parsers leave noise. A small cleaning function removes the common kinds:

- Windows line ends (`\r\n`).
- Words broken at a line end: `exam-` / `ple` becomes `example`.
- Many spaces and tabs.
- Lines with only a page number.
- Too many blank lines.

A warning: each rule can also **damage** good text. Joining `"-\n"` turns `well-` / `known` into `wellknown`. Keep your rules few, simple, and test them on real samples.

Let's practise the shape of a cleaner with a different example: clean the lines of a chat log.

1. Go through the lines.
2. Fix each line: remove extra spaces (`" ".join(line.split())`).
3. Skip lines that are only a time like `12:30`, and empty lines.
4. Join what is left.

```python
def clean_log(raw):
    kept = []
    for line in raw.split("\n"):
        line = " ".join(line.split())
        if not line or line.replace(":", "").isdigit():
            continue
        kept.append(line)
    return "\n".join(kept)

clean_log("12:30\nHi   there\n\nok  bye\n12:31")   # -> 'Hi there\nok bye'
```

`line.replace(":", "").isdigit()` removes the colon and checks if only digits are left. It is the same skill as the first exercise: a loop that fixes a line and sometimes drops it.

## Metadata: the hidden half of ingestion

Every chunk should know **where it came from**: `doc_id`, `source`, `title`, `page` or `heading`, `url`, `updated_at`, and later `tenant` and `groups` for access (lesson 40). Metadata gives you:

- citations (lesson 22),
- filters (lesson 17),
- freshness checks (lesson 40),
- debugging ("which file produced this bad chunk?").

Add it **during ingestion**. Adding it later is very hard.

## Stable ids and upsert

Give every chunk a stable id, like `f"{doc_id}#{n}"` (you did this in lesson 16). Then **upsert** (insert or update) replaces the same chunk on a re-run, instead of making a duplicate.

But a stable id alone is not enough. If a document **shrinks** from 10 chunks to 8, the old chunks 8 and 9 stay in the index. They are **stale chunks**, and they will appear in answers. When you update a document, delete its old chunks first (for example, delete by `doc_id` metadata), and then add the new ones.

## Incremental updates

Documents change. New ones arrive. Old ones are removed. Re-embedding everything each night wastes time and money. The better way:

1. For each document, keep a **fingerprint** (a hash of its text) in the index.
2. On each run, compare the current fingerprints with the stored ones.
3. Sort the documents into four groups:
   - **add**: new documents,
   - **update**: the hash changed,
   - **delete**: gone from the source,
   - **same**: nothing to do.
4. Embed only the added and updated ones. Remove the deleted ones.

A **hash** is a short code that comes from a text. Python has it in the `hashlib` module:

```python
import hashlib

print(hashlib.sha256("hello".encode("utf-8")).hexdigest()[:8])   # -> 2cf24dba
```

`.encode("utf-8")` turns the text into bytes (the hash function works on bytes). `.hexdigest()` gives the code as letters and digits. We keep the first characters only.

Normalize before you hash, so a tiny change in spaces does not look like a new document: `" ".join(text.split())`.

Let's practise the **four-group comparison** with a different example: compare an old and a new price list.

1. Go through the new items, sorted. If not in the old list: `add`. If the price differs: `change`. Else `same`.
2. Go through the old items, sorted. If not in the new list: `remove`.

```python
def compare_prices(old, new):
    plan = {"add": [], "change": [], "remove": [], "same": []}
    for item in sorted(new):
        if item not in old:
            plan["add"].append(item)
        elif old[item] != new[item]:
            plan["change"].append(item)
        else:
            plan["same"].append(item)
    for item in sorted(old):
        if item not in new:
            plan["remove"].append(item)
    return plan

compare_prices({"pen": 5, "ink": 9, "pad": 3}, {"pen": 5, "ink": 10, "cap": 2})
# -> {'add': ['cap'], 'change': ['ink'], 'remove': ['pad'], 'same': ['pen']}
```

The third exercise uses the same plan with hashes. The fourth exercise **applies** the plan to an index.

## When you must re-embed everything

- You **change the embedding model** (lesson 14). Old and new vectors do not mix.
- You **change the chunking rules**. The chunks are different now.
- You change the **cleaning** in a way that affects many documents.

Keep the model name and the chunking version in your index metadata, so you can see that a re-index is needed.

## Try it live

1. Take 3 different real files you have (a PDF, a web page saved as HTML, a markdown file). Extract the text of each with a library you pick. Print the first 500 characters. What is wrong with each?
2. Write `clean_text` and run it. Does it fix the problems? Does it break anything?
3. Index the three files. Change one file a little, and run the sync again. Did only that file get embedded?
4. Delete one file and sync. Check that its chunks are gone: search for a sentence only that file had.

## A little deeper

- **Layout-aware parsing.** Newer tools read pages as layout blocks (title, paragraph, table, figure) and keep reading order. This is better for scientific papers and invoices.
- **Duplicate documents.** The same text can come from two sources (a PDF and its web page). Hash the text and skip exact copies. Near-duplicates need fuzzier methods.
- **Idempotent jobs.** An ingestion job must be safe to run again after a crash. Stable ids, hashes and upserts give you that.
- **Backfill vs stream.** A first big load (backfill) differs from small daily updates. Rate-limit and batch the embedding calls.
- **Embedding batch size.** Send many texts in one embed call. It is much faster than one by one.
- **Quality checks.** After ingestion, print the number of chunks, the shortest and longest chunk, and a random sample. A glance finds most problems.
- **Privacy.** Do not index documents people are not allowed to search. Remove personal data when the rules say so, before embedding (lesson 40).
- **Time cost.** OCR and large PDFs are slow. Run them in a background job, not in a web request.

## Common mistakes

- Trusting the parser and never looking at its output.
- Cleaning rules that damage real text.
- Cutting a table into pieces, so numbers lose their headers.
- Leaving old chunks in the index when a document shrinks or is deleted.
- Re-embedding everything every night.
- Changing the embedding model and keeping the old vectors.
- No metadata, so citations and filters are impossible later.

## Interview corner

**How do you ingest PDFs into a RAG system?**
Extract the text (with OCR if scanned), handle layout problems like columns, headers and tables, clean the noise, add metadata (source, page), chunk, embed and upsert with stable ids. Then check a sample by eye.

**How do you handle tables?**
Keep a table together as one chunk, in a form that keeps the headers (Markdown), or turn each row into a sentence with its column names. Do not cut tables by character count.

**How do you keep the index fresh when documents change?**
Store a content hash per document. On each run, compute the plan: add, update, delete, same. Embed only the added and updated documents, delete the removed ones, and remove old chunks of an updated document.

**When do you have to re-embed everything?**
When the embedding model changes, or when the chunking or cleaning rules change in a way that affects the chunks.

## Summary

- Ingestion: load, parse, clean, metadata, chunk, embed, upsert. Garbage in, garbage out.
- PDFs, HTML, scans and tables each need care. Look at the parsed text of real files.
- Clean with a few simple rules, and test that they do not damage good text.
- Metadata (source, page, date, tenant) must be added during ingestion.
- Stable ids plus upsert prevent duplicates. Delete stale chunks when a document shrinks.
- Incremental update: hash each document, compute add/update/delete/same, embed only what changed.
- A new embedding model or new chunking needs a full re-index.
- Project: step 15 adds `copilot/sync.py`: clean text and sync the index.
- Reference: `reference/genai-retrieval.md`.
