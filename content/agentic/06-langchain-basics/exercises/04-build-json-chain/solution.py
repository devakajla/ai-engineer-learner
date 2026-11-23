# Given from earlier exercises. Do not change these.
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def build_chain(model):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Translate the text to {language}. Reply with the translation only."),
            ("human", "{text}"),
        ]
    )
    return prompt | model | StrOutputParser()


# Your task:
def build_json_chain(model):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Read the sentence and reply with JSON only, in this shape: "
                '{{"name": "<person name>", "age": <number>}}',
            ),
            ("human", "{sentence}"),
        ]
    )
    return prompt | model | JsonOutputParser()
