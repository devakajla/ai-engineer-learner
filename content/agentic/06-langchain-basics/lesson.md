---
title: "LangChain basics: models, prompts, parsers and LCEL"
summary: Learn what LangChain is for, and build chains with the pipe sign - prompt, model, parser - using small pieces that all share the same methods.
plan_ids: []
---

In lessons 1 to 5 you built agents with plain Python and the Groq SDK. That works well. So why do companies use **LangChain**?

Because many teams build the same small parts again and again: fill a prompt, call a model, clean the answer, retry, stream, log. LangChain gives these parts a **shared shape**, so you can snap them together. It also lets you swap one model for another by changing one line.

In an interview you will be asked about LangChain. Many job posts list it. This lesson teaches the core idea, **LCEL** (LangChain Expression Language), and when it helps. In the next lessons you add tools and LangGraph.

> **Setup.** The exercises need only `langchain-core`, which is already installed in the Learner project. To call Groq for real, add the Groq piece in your own folder: `uv add langchain-groq langchain-core`.

## The big idea: a Runnable

Everything in LangChain that you can run is a **Runnable**. A prompt is a Runnable. A model is a Runnable. A parser is a Runnable. Even your own function can be one.

Every Runnable has the same methods:

```
.invoke(x)    run once, give the answer
.batch([x,y]) run for many inputs, give a list of answers
.stream(x)    give the answer in pieces, as it is made
```

Because all pieces have the same methods, you can join them with the `|` sign (a pipe). The output of the left piece becomes the input of the right piece. This is the same idea as the chain in lesson 3: step one, then step two. A chain made with `|` is itself a Runnable, so it also has `invoke`, `batch` and `stream`.

Let us look at the pieces one by one.

## Messages

A chat model takes a list of messages. LangChain has a class for each role:

```python
from langchain_core.messages import HumanMessage, SystemMessage

messages = [SystemMessage("Be short."), HumanMessage("What is the capital of France?")]
```

`SystemMessage`, `HumanMessage`, `AIMessage` (the model's answer) and `ToolMessage` (a tool result, lesson 7) match the `system`, `user`, `assistant` and `tool` roles you know from the Groq SDK. The model gives back an `AIMessage`. The text is in `.content`.

## Prompt templates

A **prompt template** is a message with holes. You fill the holes later. You saw this idea in GenAI lesson 8. Here it is a Runnable:

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("Tell one fact about {topic}.")
print(prompt.invoke({"topic": "tea"}).to_messages()[0].content)
# -> Tell one fact about tea.
print(prompt.input_variables)
# -> ['topic']
```

What just happened: the template found the variable `topic`. `invoke` took a dict, filled the hole and returned the messages. For several messages use `ChatPromptTemplate.from_messages([("system", "..."), ("human", "...")])`.

> **Trap:** a real brace must be doubled. `{{"a": 1}}` gives `{"a": 1}`. A single `{a}` is a variable. You practise this in exercise 4.

## Chat models

A **chat model** takes messages and returns an `AIMessage`. With Groq:

```python
from langchain_groq import ChatGroq

model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)   # reads GROQ_API_KEY
```

Other providers have their own class (`ChatOpenAI`, `ChatAnthropic`, ...), but they all work the same way. That is the swap-one-line benefit.

For lessons and tests we use a **fake model** that returns fixed answers, so nothing touches the network:

```python
from langchain_core.language_models.fake_chat_models import FakeListChatModel

model = FakeListChatModel(responses=["Tea is a hot drink made from leaves."])
reply = model.invoke("Tell one fact about tea.")
print(type(reply).__name__, "|", reply.content)
# -> AIMessage | Tea is a hot drink made from leaves.
```

## Output parsers

The model returns an `AIMessage`, but most code wants a plain string or a dict. A **parser** does this step. `StrOutputParser` takes the message and returns its text. `JsonOutputParser` reads JSON text and returns a dict (it also removes a markdown code fence).

## LCEL: join the pieces with `|`

```python
from langchain_core.output_parsers import StrOutputParser

model = FakeListChatModel(responses=["Tea is a hot drink made from leaves."])
chain = prompt | model | StrOutputParser()
print(chain.invoke({"topic": "tea"}))
# -> Tea is a hot drink made from leaves.
```

Line by line:

1. `prompt` gets a dict and makes messages.
2. `model` gets messages and makes an `AIMessage`.
3. `StrOutputParser` gets the `AIMessage` and makes a string.
4. `chain` is one object. You call it with the input of the **first** piece.

### Step by step: build a chain (exercise 1)

Exercise 1 asks for a chain with a two-message prompt. The steps, with a different task:

1. Write the prompt with `from_messages`: a system message that sets the job, and a human message with the variable.
2. Pick the parts: your prompt, the model you were given, a parser.
3. Join them in one line and return it.

```python
def build_summary_chain(model):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarise the text in one sentence."),
        ("human", "{text}"),
    ])
    return prompt | model | StrOutputParser()
```

You do not call the model inside the function. You only **build** the chain. The caller runs it with `chain.invoke({"text": "..."})`.

## Your own function as a step

Wrap a function with `RunnableLambda` and it joins the chain:

```python
from langchain_core.runnables import RunnableLambda

step = RunnableLambda(lambda x: x + 1) | RunnableLambda(lambda x: x * 10)
print(step.invoke(2))
# -> 30
print(step.batch([1, 2, 3]))
# -> [20, 30, 40]
```

You get `batch` for free. This is the main reason to use a Runnable: one function, and you get `invoke`, `batch` and `stream`.

## Several branches at once

A dict of Runnables runs **all** of them on the same input and returns a dict. The pieces run at the same time (this is the "parallel" pattern from lesson 3):

```python
from langchain_core.runnables import RunnableParallel

both = RunnableParallel({"upper": RunnableLambda(str.upper), "length": RunnableLambda(len)})
print(both.invoke("abc"))
# -> {'upper': 'ABC', 'length': 3}
```

Inside a chain, a plain dict is turned into a `RunnableParallel` for you. You will use this in lesson 7 to build a RAG chain.

## Retry and fallback

Any Runnable has helpers for trouble:

```python
chain.with_retry(stop_after_attempt=3)          # try again, up to 3 times
chain.with_fallbacks([backup_chain])            # if it fails, use this one
```

The fallback is useful when the main model is down: `groq_chain.with_fallbacks([other_provider_chain])`. In exercise 3 you build this.

## Try it live

1. `uv add langchain-groq langchain-core` in a new folder. Set `GROQ_API_KEY`.
2. Build the translation chain from exercise 1 with `ChatGroq` and run it on 3 sentences.
3. Run `chain.batch([...])` with 5 sentences. Compare the time with a `for` loop of `invoke`.
4. Run `for piece in chain.stream({...}): print(piece, end="")` and watch the text arrive in pieces.
5. Turn off your internet and use `with_fallbacks` with a fake model as the backup. What do you see?

## A little deeper

- **Why `|` works.** Python lets a class define `__or__`. LangChain uses this to build a `RunnableSequence` from the two sides. Nothing runs until you call `invoke`.
- **`init_chat_model("groq:qwen/qwen3.8-27b")`** builds a model from a string, so the provider can be a config value.
- **Structured output.** `model.with_structured_output(MySchema)` asks for JSON that fits a Pydantic class and returns an object. It uses the provider's JSON or tool features inside.
- **Callbacks and tracing.** Every Runnable call can be logged by tools such as LangSmith, with no change to your code. You will see this in lesson 16.
- **When not to use LangChain.** A single call with a clear prompt does not need it. A framework adds a layer to learn and to debug. Use it when you gain reuse (swap models, shared retries, tracing) or when the team already uses it.
- **Versions.** LangChain changes fast. Names move between packages (`langchain`, `langchain-core`, `langchain-community`). Check the docs for the version you install.

## Common mistakes

- Calling the model when you only wanted to build the chain.
- Forgetting the parser, then wondering why the result is an `AIMessage` and not a string.
- A single brace in a prompt that holds JSON (`{"a": 1}`). It becomes a missing variable error. Double it.
- Passing a string to `invoke` when the prompt needs a dict (or the reverse).
- Using LangChain for a one-call task.
- Mixing up `invoke` (one input) and `batch` (a list).

## Interview corner

**What is LCEL?**
A way to build chains by joining Runnables with `|`. Each piece has `invoke`, `batch` and `stream`, so the whole chain has them too.

**What is a Runnable?**
Any piece with the shared methods: prompt, model, parser, retriever, or your own function wrapped with `RunnableLambda`.

**Why use LangChain at all, and when not?**
For reuse and speed: shared interfaces, easy model swap, retries, fallbacks, tracing. Not for a single plain call, where the extra layer only adds things to learn.

**How do you make a chain return a dict, not text?**
End it with `JsonOutputParser()`, or use `model.with_structured_output(Schema)`. Validate the result.

**What is a fallback?**
`with_fallbacks([...])`: if the first Runnable raises an error, LangChain tries the next one with the same input.

## Summary

- A **Runnable** has `invoke`, `batch` and `stream`. Prompts, models, parsers and your own functions can all be Runnables.
- `prompt | model | parser` is a **chain**. It is also a Runnable.
- Fill prompt holes with a dict. Double the braces to write a real brace.
- Parsers (`StrOutputParser`, `JsonOutputParser`) turn the `AIMessage` into text or a dict.
- `RunnableLambda` wraps your function. A dict of Runnables runs in parallel.
- `with_retry` and `with_fallbacks` add safety.
- Use LangChain for reuse and swapping. Skip it for a single call.
- Reference: see `reference/agentic-langchain-langgraph.md`.
