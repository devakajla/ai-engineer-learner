def build_prompt(document, question):
    return (
        "Answer only from the text between the tags. "
        "If the answer is not there, reply exactly: I don't know.\n\n"
        "<document>\n"
        f"{document.strip()}\n"
        "</document>\n\n"
        f"Question: {question.strip()}"
    )
