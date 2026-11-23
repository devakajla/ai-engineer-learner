# Batch and fallback

Every LangChain piece (a **Runnable**) has the same methods: `invoke` for one input, `batch` for a list of inputs, and `stream` for pieces of the answer. They also have helpers such as `with_fallbacks`, which says "if this fails, try that one".

The imports and `build_chain` are given. Write two functions:

1. `run_batch(chain, texts, language)`: run the chain once for every text with **one `batch` call**. Each input is a dict `{"language": language, "text": text}`. Return the list of answers, in the same order.
2. `safe_chain(main, backup)`: return a runnable that runs `main`, and if `main` raises an error, runs `backup` with the same input. Use `main.with_fallbacks([backup])`.

```python
run_batch(chain, ["one", "two"], "Spanish")
# -> ['uno', 'dos']
safe_chain(main, backup).invoke("q")   # main fails
# -> whatever backup returns
```

**Think first:** what if the backup also fails? Should the error be hidden?

**Hint:** `chain.batch([...])` takes a list of inputs and returns a list of outputs.
