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
