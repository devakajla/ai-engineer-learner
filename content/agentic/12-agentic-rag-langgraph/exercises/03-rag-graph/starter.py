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


# Your task:
def build_rag_graph(client, search):
    ...
