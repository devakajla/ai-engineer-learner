# Given from earlier exercises. Do not change these.
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda


def build_chain(model):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Translate the text to {language}. Reply with the translation only."),
            ("human", "{text}"),
        ]
    )
    return prompt | model | StrOutputParser()


# Your task:
def clean_title(text):
    first_line = text.strip().split("\n")[0]
    return first_line.strip().strip("\"'").strip()


def build_title_chain(model):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Write a short title for the text. Reply with the title only."),
            ("human", "{text}"),
        ]
    )
    return prompt | model | StrOutputParser() | RunnableLambda(clean_title)
