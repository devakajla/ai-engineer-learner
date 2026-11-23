# Step 16 — Access control and freshness

Copilot now answers from **every** chunk. In a real company that is a leak: a customer must not see another customer's docs, and an engineer must not see HR files. Old pages are a second problem: Copilot may quote last year's price. In this step you add both checks (lesson 40).

The golden rule: **the filter runs in code, before the prompt is built.** Never write "do not show secret files" in the prompt. A model that never receives the text cannot leak it.

### 1. `copilot/citations.py`: answer from chunks you chose

`cited_answer` searches by itself. Now the caller must be able to hand over already-filtered chunks. Add a `hits=None` argument:

```python
def cited_answer(client, collection, question, k=3, embed=embed_texts, model=DEFAULT_MODEL,
                 base_delay=1.0, max_tries=2, hits=None):
    """..."""
    if hits is None:
        hits = retrieve(collection, question, k=k, embed=embed)
    if not hits:
        ...   # as before
```

Use `is None`, not `if not hits`: an **empty list** means "the filter removed everything", and that must not trigger a new search that ignores the filter. Old calls work as before.

### 2. `copilot/access.py`

```python
"""Who may see what, and how fresh it must be. Rules live in CODE, never in the prompt."""

import json
from datetime import date
from pathlib import Path

from copilot.citations import cited_answer
from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL
from copilot.rag import retrieve


def load_access(path):
    """The rules table: {source: {"tenant", "groups", "updated"}}. A missing file means no rules."""
    file = Path(path)
    if not file.exists():
        return {}
    return json.loads(file.read_text(encoding="utf-8"))


def with_access(hits, table):
    """Copy each hit and add tenant, groups and updated from the table.

    A source with no rule gets tenant None, which nobody may see (deny by default).
    """
    result = []
    for hit in hits:
        rule = table.get(hit["source"], {})
        new_hit = dict(hit)
        new_hit["tenant"] = rule.get("tenant")
        new_hit["groups"] = rule.get("groups", [])
        if "updated" in rule:
            new_hit["updated"] = rule["updated"]
        result.append(new_hit)
    return result


def allowed(chunk, user):
    """Same tenant, and (if the chunk lists groups) the user is in at least one of them."""
    if chunk.get("tenant") is None or chunk["tenant"] != user.get("tenant"):
        return False
    groups = chunk.get("groups", [])
    if not groups:
        return True
    return any(group in user.get("groups", []) for group in groups)


def filter_hits(hits, user):
    return [hit for hit in hits if allowed(hit, user)]


def drop_stale(hits, today, max_age_days):
    """Remove hits older than max_age_days. today is "YYYY-MM-DD". A hit with no date is kept."""
    today_date = date.fromisoformat(today)
    fresh = []
    for hit in hits:
        updated = hit.get("updated")
        if updated is None:
            fresh.append(hit)
            continue
        age = (today_date - date.fromisoformat(updated)).days
        if age <= max_age_days:
            fresh.append(hit)
    return fresh


def search_for_user(collection, table, user, question, k=3, today=None, max_age_days=None,
                    overfetch=5, embed=embed_texts):
    """The best k chunks this user may see. Searches wider first, because filtering removes some."""
    if k <= 0:
        return []
    hits = retrieve(collection, question, k=k * overfetch, embed=embed)
    hits = filter_hits(with_access(hits, table), user)
    if today is not None and max_age_days is not None:
        hits = drop_stale(hits, today, max_age_days)
    return hits[:k]


def answer_for_user(client, collection, table, user, question, k=3, today=None, max_age_days=None,
                    embed=embed_texts, model=DEFAULT_MODEL, base_delay=1.0):
    """A cited answer built ONLY from chunks the user is allowed to see."""
    hits = search_for_user(collection, table, user, question, k=k, today=today,
                           max_age_days=max_age_days, embed=embed)
    return cited_answer(client, collection, question, k=k, embed=embed, model=model,
                        base_delay=base_delay, hits=hits)
```

Read it in parts:

1. **The rules table** maps a source file to its tenant, its groups and its last update date. Here it is a JSON file. In a real system the same fields live in the chunk metadata of the vector database, or come from your identity system.
2. **Deny by default.** `with_access` gives a source with no rule `tenant: None`, and `allowed` refuses `None`. A new file that nobody classified is invisible until someone adds a rule. The opposite default (allow unless told otherwise) leaks on the first mistake. The test even checks that `None` does not match a user whose tenant is also `None`.
3. **`allowed`** needs the same tenant. If the chunk lists groups, the user must share at least one. An empty list of groups means the whole tenant may read it.
4. **`drop_stale`** compares dates with `date.fromisoformat`. A chunk exactly `max_age_days` old is still fresh. A chunk with no date is kept: you cannot judge what you cannot see. Decide your own policy for that.
5. **`search_for_user` over-fetches.** Filtering removes chunks, so asking for exactly `k` may leave you with fewer. Ask for `k * overfetch`, filter, then cut to `k`.
6. **`answer_for_user`** passes the filtered hits to `cited_answer`. The forbidden text is never in the prompt. If nothing is allowed, the model is not called at all.

> A subtle point: access rules decide what the **model** may read. Also check them when you show **sources** or logs. Do not print a forbidden file name either.

### 3. A command to try it: `copilot/access_cli.py`

```python
"""Ask as a given user. Usage:

    python -m copilot.access_cli acme eng "how do I create a task"
    python -m copilot.access_cli acme hr "what are the salary bands"

The rules come from access.json (copy access.example.json and edit it).
"""

import sys
from datetime import date

from copilot.access import answer_for_user, load_access
from copilot.llm import get_client
from copilot.store import open_collection

DB_PATH = ".chroma"
ACCESS_PATH = "access.json"


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return
    user = {"tenant": sys.argv[1], "groups": [g for g in sys.argv[2].split(",") if g]}
    question = " ".join(sys.argv[3:])
    result = answer_for_user(
        get_client(), open_collection(DB_PATH), load_access(ACCESS_PATH), user, question,
        today=date.today().isoformat(), max_age_days=365,
    )
    print(result["answer"])
    for source in result["sources"]:
        print(f"[{source['n']}] {source['source']} > {source['heading']}")


if __name__ == "__main__":
    main()
```

Create `access.json` in the project folder (copy the example, and add `access.json` to `.gitignore`):

```json
{
  "tasks.md": {"tenant": "acme", "groups": [], "updated": "2026-11-01"},
  "payroll.md": {"tenant": "acme", "groups": ["hr"], "updated": "2026-10-01"},
  "other-company.md": {"tenant": "globex", "groups": [], "updated": "2026-11-10"}
}
```

```bash
uv run python -m copilot.docs_cli sync docs
uv run python -m copilot.access_cli acme eng "what are the salary bands"
uv run python -m copilot.access_cli acme hr  "what are the salary bands"
```

The same question must give two different answers. The engineer gets "I don't know." and the HR user gets the answer. (Name your doc files like the table says, or change the table.)

### 4. Commit

```bash
git add -A && git commit -m "Add access control and freshness filters"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 15)
│   ├── access.py
│   └── access_cli.py
├── access.json          (your rules, not committed)
├── docs/
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check that `cited_answer` accepts `hits` (a list is used, `[]` means no model call), `load_access`, `with_access` (rules added, unknown source denied, input not changed), `allowed` (tenant, groups, no rule, `None` vs `None`, a user without groups), `filter_hits` (order kept), `drop_stale` (the 30-day edge, undated hits), `search_for_user` (other tenants, other groups and rule-less chunks never appear, over-fetch still fills `k`, stale chunks are dropped) and `answer_for_user` with a fake client: the text of forbidden chunks must **never** be in the prompt, and with nothing allowed the model is not called. Steps 1 to 15 must keep working.
