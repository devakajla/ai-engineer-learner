from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def build_chain(model):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Translate the text to {language}. Reply with the translation only."),
            ("human", "{text}"),
        ]
    )
    return prompt | model | StrOutputParser()
