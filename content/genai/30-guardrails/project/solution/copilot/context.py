"""Prepare the chunks before they go into the prompt: no repeats, no one-source flood, best at the edges."""

from copilot.citations import cited_answer
from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL
from copilot.rag import retrieve


def dedupe_hits(hits, max_per_source=None):
    """Drop hits whose text repeats an earlier one (ignoring case and spacing).

    With max_per_source, keep at most that many hits from one source. Order is kept.
    """
    seen = []
    per_source = {}
    kept = []
    for hit in hits:
        normal = " ".join(hit["text"].lower().split())
        if normal in seen:
            continue
        source = hit.get("source", "")
        if max_per_source is not None and per_source.get(source, 0) >= max_per_source:
            continue
        seen.append(normal)
        per_source[source] = per_source.get(source, 0) + 1
        kept.append(hit)
    return kept


def prepare_context(hits, max_hits, max_per_source=2):
    """Dedupe, cut to max_hits, then put the best chunks at the START and END of the list.

    Models use the beginning and the end of a long context best, and lose the middle ("lost in the middle").
    Input is best first. The result is ranks 1, 3, 5 ... then ... 6, 4, 2.
    """
    if max_hits <= 0:
        return []
    hits = dedupe_hits(hits, max_per_source)[:max_hits]
    front = hits[0::2]
    back = hits[1::2]
    back.reverse()
    return front + back


def retrieve_prepared(collection, question, k=3, pool=10, max_per_source=2, embed=embed_texts):
    """A wide pool, cleaned and ordered, ready for the prompt."""
    candidates = retrieve(collection, question, k=pool, embed=embed)
    return prepare_context(candidates, k, max_per_source)


def answer_prepared(client, collection, question, k=3, pool=10, max_per_source=2,
                    embed=embed_texts, model=DEFAULT_MODEL, base_delay=1.0):
    """A cited answer from prepared chunks."""
    hits = retrieve_prepared(collection, question, k=k, pool=pool, max_per_source=max_per_source, embed=embed)
    return cited_answer(client, collection, question, k=k, embed=embed, model=model,
                        base_delay=base_delay, hits=hits)
