# Step 15 — Ingestion that keeps the index fresh

So far `docs_cli index` re-embeds **every** file each time. Embedding costs money and time, and the docs change a little at a time. In this step Copilot learns to **sync** (lesson 39): clean the text, fingerprint each file, and touch only what is new, changed or removed.

### 1. `copilot/sync.py`

```python
"""Keep the index in step with the docs folder: add new, update changed, delete removed, skip the rest."""

import hashlib
import json
from pathlib import Path

from copilot.chunking import chunk_markdown
from copilot.embed import embed_texts
from copilot.ingest import load_docs
from copilot.store import add_chunks


def clean_text(raw):
    """Tidy text from a PDF or a web page: unix line ends, joined hyphenated words, one space between
    words, no lines that are only a page number, at most one blank line in a row."""
    text = raw.replace("\r\n", "\n").replace("-\n", "")
    lines = []
    for line in text.split("\n"):
        line = " ".join(line.split())
        if line.isdigit():
            continue
        lines.append(line)
    result = "\n".join(lines)
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")
    return result.strip()


def content_hash(text):
    """A short fingerprint of the text. Extra spaces and line breaks do not change it."""
    normal = " ".join(text.split())
    return hashlib.sha256(normal.encode("utf-8")).hexdigest()[:16]


def plan_sync(stored, docs):
    """Decide what to do. stored is {doc_id: hash}, docs is {doc_id: text}. Each list is sorted."""
    plan = {"add": [], "update": [], "delete": [], "same": []}
    for doc_id in sorted(docs):
        if doc_id not in stored:
            plan["add"].append(doc_id)
        elif stored[doc_id] != content_hash(docs[doc_id]):
            plan["update"].append(doc_id)
        else:
            plan["same"].append(doc_id)
    for doc_id in sorted(stored):
        if doc_id not in docs:
            plan["delete"].append(doc_id)
    return plan


def load_manifest(path):
    """The saved {source: hash} table. A missing file means an empty table."""
    file = Path(path)
    if not file.exists():
        return {}
    return json.loads(file.read_text(encoding="utf-8"))


def save_manifest(path, manifest):
    Path(path).write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def sync_folder(collection, folder, manifest, max_chars=800, embed=embed_texts):
    """Bring the collection in line with the folder. Only new and changed files are embedded.

    The manifest ({source: hash}) is changed in place. Returns counts: added, updated, deleted, same, chunks.
    """
    docs = {}
    for source, text in load_docs(folder):
        docs[source] = clean_text(text)
    plan = plan_sync(manifest, docs)
    chunks_added = 0
    for source in plan["add"] + plan["update"]:
        collection.delete(where={"source": source})
        chunks_added += add_chunks(collection, chunk_markdown(docs[source], source, max_chars), embed=embed)
        manifest[source] = content_hash(docs[source])
    for source in plan["delete"]:
        collection.delete(where={"source": source})
        del manifest[source]
    return {
        "added": len(plan["add"]),
        "updated": len(plan["update"]),
        "deleted": len(plan["delete"]),
        "same": len(plan["same"]),
        "chunks": chunks_added,
    }
```

Read it in parts:

1. **`clean_text`** fixes the usual mess of text from PDFs and web pages: Windows line ends, words split with a hyphen at the end of a line, repeated spaces, lines that are only a page number, and long runs of blank lines. Garbage in the index means garbage in the answers.
2. **`content_hash`** is a fingerprint (SHA-256, cut to 16 characters). The same text always gives the same hash, and a change gives a different one. Extra spaces and line breaks are ignored on purpose: a file that only changed its formatting must not cost you an embedding call.
3. **`plan_sync`** is a pure function: it only decides. `stored` is what you saved last time, `docs` is what is on disk now. Returns four sorted lists: `add`, `update`, `delete`, `same`. Because it does no work, it is easy to test and easy to print as a "dry run".
4. **The manifest** is a small JSON file with `{source: hash}`. It is the memory between two runs. A missing file means "nothing is indexed yet". `sort_keys=True` keeps the file stable, so a version-control diff shows only real changes.
5. **`sync_folder`** follows the plan. For a new or changed file it first **deletes the old chunks** of that source, then adds the new ones. Skipping the delete would leave stale chunks behind, and Copilot would quote text that is no longer in the docs. For a removed file it only deletes. Unchanged files are not read into the embedder at all.

### 2. Add a `sync` command: `copilot/docs_cli.py`

Add the import, a path for the manifest, `"sync"` to the commands, and a branch in `main`:

```python
from copilot.sync import load_manifest, save_manifest, sync_folder

MANIFEST_PATH = "manifest.json"
...
    commands = ("index", "sync", "search", "vector", "keyword")
...
    elif command == "sync":
        manifest = load_manifest(MANIFEST_PATH)
        report = sync_folder(collection, rest[0], manifest)
        save_manifest(MANIFEST_PATH, manifest)
        print(report)
```

Also add `manifest.json` to `.gitignore`: it belongs to your machine's index, not to the project.

```bash
uv run python -m copilot.docs_cli sync docs      # first run: everything is added
uv run python -m copilot.docs_cli sync docs      # second run: everything is "same", nothing embedded
```

Now edit one doc, delete another, and run `sync` again. Read the report. That is the lesson, live.

### 3. Commit

```bash
git add -A && git commit -m "Add incremental sync of the docs folder"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 14)
│   └── sync.py
├── docs/
├── .env.example
├── .gitignore
├── manifest.json        (created by sync, not committed)
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `clean_text` (line ends, hyphen joins, spaces, page-number lines, blank lines, digits inside a line stay), `content_hash` (formatting does not matter, length 16), `plan_sync` (all four lists, empty input), the manifest round trip, and `sync_folder` with a counting fake `embed`: the first run adds everything, a second run embeds **nothing**, a changed file replaces its old chunks, a removed file leaves the index, and a formatting-only change counts as "same". Steps 1 to 14 must keep working.
