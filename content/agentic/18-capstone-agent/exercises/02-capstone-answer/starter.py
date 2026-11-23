# Given from earlier exercises. Do not change these.
def ask(client, prompt, system=None, temperature=0):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()


ROUTES = ["docs", "tasks", "chat"]


def route_question(client, question):
    reply = ask(
        client,
        "Pick one route for this question. docs = questions about the API documentation. "
        "tasks = questions about the user's own tasks. chat = greetings and small talk. "
        "Reply with one word: docs, tasks or chat.\n\nQuestion: " + question,
    )
    word = reply.strip().strip(".!\"' `").lower()
    return word if word in ROUTES else "docs"


def add_span(trace, name, kind, start, end, **attrs):
    span = {"name": name, "kind": kind, "ms": round((end - start) * 1000), **attrs}
    trace.append(span)
    return span


def traced_call(trace, name, kind, clock, fn, *args, **kwargs):
    start = clock()
    try:
        result = fn(*args, **kwargs)
    except Exception as error:
        add_span(trace, name, kind, start, clock(), error=str(error))
        raise
    add_span(trace, name, kind, start, clock())
    return result


def wrap_untrusted(name, text):
    return f'<tool_output name="{name}" trust="untrusted">\n{text}\n</tool_output>'


# Your task:
def answer(client, question, tools, trace, clock):
    ...
