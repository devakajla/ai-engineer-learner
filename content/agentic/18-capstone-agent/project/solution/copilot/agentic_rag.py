"""Agentic RAG as a LangGraph graph: retrieve, grade, then answer, rewrite the question, or give up."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL, complete_with_retry
from copilot.rag import NO_ANSWER, build_rag_messages, retrieve


class RagState(TypedDict):
    original: str
    question: str
    hits: list
    relevant: list
    tries: int
    max_tries: int
    answer: str


def grade_hit(client, question, hit, model=DEFAULT_MODEL):
    """Ask the model: does this chunk help to answer the question? True for a clear yes."""
    prompt = (
        "Is this document relevant to the question? Reply yes or no.\n\n"
        f"Question: {question}\n\nDocument: {hit['text']}"
    )
    reply = complete_with_retry(
        client, [{"role": "user", "content": prompt}], model=model, temperature=0, max_completion_tokens=5
    )
    return reply.strip().lower().startswith("yes")


def grade_hits(client, question, hits, model=DEFAULT_MODEL):
    return [hit for hit in hits if grade_hit(client, question, hit, model)]


def decide_next(state):
    """Pure routing: answer when something relevant was found, give up when out of tries, else rewrite."""
    if state["relevant"]:
        return "answer"
    if state["tries"] >= state["max_tries"]:
        return "give_up"
    return "rewrite"


def rewrite_for_search(client, question, model=DEFAULT_MODEL):
    prompt = (
        "Rewrite this question so a search engine finds better results. "
        "Use the words a documentation page would use. Reply with the new question only.\n\n" + question
    )
    text = complete_with_retry(
        client, [{"role": "user", "content": prompt}], model=model, temperature=0, max_completion_tokens=60
    )
    return text.strip() or question


def build_agentic_graph(client, collection, k=3, embed=embed_texts, model=DEFAULT_MODEL):
    """Compile the graph. The nodes use client and collection from this function."""

    def retrieve_node(state):
        hits = retrieve(collection, state["question"], k=k, embed=embed)
        return {"hits": hits, "tries": state["tries"] + 1}

    def grade_node(state):
        return {"relevant": grade_hits(client, state["question"], state["hits"], model)}

    def rewrite_node(state):
        return {"question": rewrite_for_search(client, state["question"], model)}

    def answer_node(state):
        messages = build_rag_messages(state["original"], state["relevant"])
        text = complete_with_retry(client, messages, model=model, temperature=0, max_completion_tokens=300)
        return {"answer": text}

    def give_up_node(state):
        return {"answer": NO_ANSWER}

    graph = StateGraph(RagState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("answer", answer_node)
    graph.add_node("give_up", give_up_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", decide_next, {"answer": "answer", "rewrite": "rewrite", "give_up": "give_up"})
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("answer", END)
    graph.add_edge("give_up", END)
    return graph.compile()


def agentic_answer(graph, question, max_tries=2):
    """Run the graph. Returns {"answer", "sources", "tries", "path"}.

    path lists the nodes in the order they ran. sources are the ids of the chunks that were used.
    """
    state = {"original": question, "question": question, "hits": [], "relevant": [],
             "tries": 0, "max_tries": max_tries, "answer": ""}
    path = []
    answer = ""
    relevant = []
    for update in graph.stream(state, stream_mode="updates"):
        for node, change in update.items():
            path.append(node)
            if "answer" in change:
                answer = change["answer"]
            if "relevant" in change:
                relevant = change["relevant"]
    sources = [hit["id"] for hit in relevant] if path and path[-1] == "answer" else []
    return {"answer": answer, "sources": sources, "tries": path.count("retrieve"), "path": path}
