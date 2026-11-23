# The agent loop with LangChain messages

You built the agent loop with the Groq SDK in GenAI lesson 27. Here is the same loop with LangChain messages. A chat model has `bind_tools(tools)`: it returns a model that knows your tools and may answer with `tool_calls`.

Given: `convert_temp` and `run_tool_calls` (from exercise 2). Write `run_langchain_agent(model, question, tools, max_steps=5)`:

1. `bound = model.bind_tools(tools)` (once).
2. Start with `messages = [HumanMessage(question)]`.
3. Repeat at most `max_steps` times:
   - `ai = bound.invoke(messages)`, then add `ai` to `messages`.
   - If `ai.tool_calls` is empty, return `ai.content`.
   - Otherwise run the calls with `run_tool_calls(ai, tools)` and add the results to `messages`.
4. If the loop ends without an answer, return `"Stopped: too many steps."`.

```python
run_langchain_agent(model, "What is 100 C in F?", [convert_temp])
# -> 'It is 212 F.'
```

**Think first:** why must the `AIMessage` with the tool calls stay in `messages` before the tool results?

**Hint:** a `for _ in range(max_steps):` loop with a `return` inside.
