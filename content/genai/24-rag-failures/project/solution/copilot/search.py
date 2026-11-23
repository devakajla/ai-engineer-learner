"""First version of search: embed everything, score, take the best k. In memory only."""

from copilot.embed import embed_texts
from copilot.similarity import top_k


def search_texts(query, texts, k=3, embed=embed_texts):
    """Find the k texts closest in meaning to the query.

    Returns a list of {"index", "text", "score"}, best first.
    `embed` takes a list of texts and returns a list of vectors. Tests pass a fake one.
    """
    if k <= 0 or not texts:
        return []
    doc_vectors = embed(texts)
    query_vector = embed([query])[0]
    return [
        {"index": index, "text": texts[index], "score": score}
        for index, score in top_k(query_vector, doc_vectors, k)
    ]
