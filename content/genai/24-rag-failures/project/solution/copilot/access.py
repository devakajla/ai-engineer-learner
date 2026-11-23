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
