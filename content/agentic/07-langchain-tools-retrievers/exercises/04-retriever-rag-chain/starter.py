# Given from earlier exercises. Do not change these.
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


# Your task:
def make_retriever(docs, k=2):
    ...


def format_docs(docs):
    ...


def build_rag_chain(retriever, model):
    ...
