# Given from earlier exercises. Do not change these.
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

def ask(client, prompt, system=None, temperature=0):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()


def grade_doc(client, question, doc):
    reply = ask(
        client,
        f"Question: {question}\n\nDocument: {doc}\n\n"
        "Is the document relevant to the question? Answer yes or no.",
    )
    return reply.strip().lower().startswith("yes")


def grade_docs(client, question, docs):
    return [doc for doc in docs if grade_doc(client, question, doc)]


def decide_next(state):
    if state["relevant"]:
        return "answer"
    if state["tries"] >= state["max_tries"]:
        return "give_up"
    return "rewrite"


def rewrite_question(client, question):
    return ask(
        client,
        "Rewrite this question so a search engine finds better results. "
        "Reply with the new question only.\n\n" + question,
    )


class RagState(TypedDict):
    question: str
    docs: list
    relevant: list
    tries: int
    max_tries: int
    answer: str


def build_rag_graph(client, search):
    def retrieve(state):
        return {"docs": search(state["question"]), "tries": state["tries"] + 1}

    def grade(state):
        return {"relevant": grade_docs(client, state["question"], state["docs"])}

    def rewrite(state):
        return {"question": rewrite_question(client, state["question"])}

    def answer(state):
        context = "\n".join(state["relevant"])
        prompt = "Answer using only this context.\n\nContext:\n" + context + "\n\nQuestion: " + state["question"]
        return {"answer": ask(client, prompt)}

    def give_up(state):
        return {"answer": "I could not find this in the documents."}

    graph = StateGraph(RagState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("grade", grade)
    graph.add_node("rewrite", rewrite)
    graph.add_node("answer", answer)
    graph.add_node("give_up", give_up)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", decide_next, {"answer": "answer", "rewrite": "rewrite", "give_up": "give_up"})
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("answer", END)
    graph.add_edge("give_up", END)
    return graph.compile()


# Your task:
def run_rag(app, question, max_tries=2):
    state = {"question": question, "docs": [], "relevant": [], "tries": 0, "max_tries": max_tries, "answer": ""}
    path = []
    answer = ""
    for update in app.stream(state, stream_mode="updates"):
        for node, change in update.items():
            path.append(node)
            if "answer" in change:
                answer = change["answer"]
    return {"answer": answer, "tries": path.count("retrieve"), "path": path}
