"""Hybrid search: vector search plus BM25 keyword search, joined with reciprocal rank fusion."""

from copilot.bm25 import bm25_scores, rank_by_score
from copilot.embed import embed_texts
from copilot.store import build_where, search


def reciprocal_rank_fusion(rankings, k=60):
    """Join ranked lists of ids. Returns (id, score) pairs, best first. Ties: first seen wins."""
    scores = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1 / (k + rank)
    pairs = list(scores.items())
    return sorted(pairs, key=pair_score, reverse=True)


def pair_score(pair):
    return pair[1]


def keyword_search(collection, query, k=20, source=None, heading=None):
    """The k best BM25 matches among the stored chunks, as dicts without a score."""
    where = build_where(source, heading)
    stored = collection.get() if where is None else collection.get(where=where)
    scores = bm25_scores(query, stored["documents"])
    hits = []
    for i in rank_by_score(scores)[:k]:
        hits.append({
            "id": stored["ids"][i],
            "text": stored["documents"][i],
            "source": stored["metadatas"][i]["source"],
            "heading": stored["metadatas"][i]["heading"],
        })
    return hits


def hybrid_search(collection, query, k=3, pool=20, source=None, heading=None, embed=embed_texts):
    """Vector and keyword search, fused. Each side gives `pool` candidates, the best k are returned.

    Each hit is {"id", "text", "source", "heading", "score"}. The score is the RRF score.
    """
    if k <= 0:
        return []
    vector_hits = search(collection, query, k=pool, source=source, heading=heading, embed=embed)
    keyword_hits = keyword_search(collection, query, k=pool, source=source, heading=heading)
    by_id = {}
    for hit in vector_hits + keyword_hits:
        by_id[hit["id"]] = hit
    fused = reciprocal_rank_fusion([[h["id"] for h in vector_hits], [h["id"] for h in keyword_hits]])
    results = []
    for chunk_id, score in fused[:k]:
        hit = by_id[chunk_id]
        results.append({
            "id": chunk_id,
            "text": hit["text"],
            "source": hit["source"],
            "heading": hit["heading"],
            "score": score,
        })
    return results
