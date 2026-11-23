# Build your first chain

A **chain** in LangChain is a few small pieces joined with the `|` sign: prompt, model, parser. Data flows from left to right.

Write `build_chain(model)`. It takes a chat model and returns a chain that translates text.

1. Make a prompt with `ChatPromptTemplate.from_messages([...])` with two messages:
   - `("system", "Translate the text to {language}. Reply with the translation only.")`
   - `("human", "{text}")`
2. Join it with the model and a `StrOutputParser()`: `prompt | model | StrOutputParser()`.
3. Return the chain.

The imports are given in the starter. In the tests the model is a fake one that returns fixed answers.

```python
chain = build_chain(model)
chain.invoke({"language": "Spanish", "text": "Hello"})
# -> 'Hola'
```

**Think first:** a chat model returns a message object (`AIMessage`), not a string. Which piece of the chain turns it into plain text?

**Hint:** the chain is one line: `return prompt | model | StrOutputParser()`.
