# Prompt, RAG or fine-tune?

Fine-tuning is the **last** tool, not the first. It costs data, time and money, and it is hard to undo. The usual ladder is: try a better **prompt** first, add **RAG** when the model lacks facts, and **fine-tune** only to change *how* the model writes or acts (style, format, a narrow skill) when you have enough good examples.

Write `choose_approach(prompt_works, knowledge_is_private_or_changing, needs_style_or_format, example_count)`. It returns one of the strings `"prompting"`, `"rag"`, `"fine-tune"`, `"few-shot"`. Apply the rules **in this order**:

1. If `prompt_works` is true: `"prompting"`.
2. Else if `knowledge_is_private_or_changing` is true: `"rag"`.
3. Else if `needs_style_or_format` is true: `"fine-tune"` when `example_count >= 500`, otherwise `"few-shot"` (put examples in the prompt).
4. Else: `"prompting"`.

```python
choose_approach(False, True, True, 5000)
# -> 'rag'
choose_approach(False, False, True, 800)
# -> 'fine-tune'
```

**Think first:** why is "the model does not know our price list" a RAG problem and not a fine-tune problem?

**Hint:** write four `if` lines, one per rule, in the given order.
