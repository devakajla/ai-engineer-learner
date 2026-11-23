# Given from earlier exercises. Do not change these.
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


# Your task:
def make_retriever(docs, k=2):
    def search(query):
        words = set(query.lower().split())
        scored = []
        for doc in docs:
            score = len(words & set(doc.page_content.lower().split()))
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda pair: -pair[0])
        return [doc for _, doc in scored[:k]]

    return RunnableLambda(search)


def format_docs(docs):
    return "\n".join(f"[{i}] {doc.page_content}" for i, doc in enumerate(docs, 1))


def build_rag_chain(retriever, model):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer using only the context. If it is not there, say you do not know."),
            ("human", "Context:\n{context}\n\nQuestion: {question}"),
        ]
    )
    return (
        {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
