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
    ...


def build_title_chain(model):
    ...
