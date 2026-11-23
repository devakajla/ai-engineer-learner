# 2. Tokens, context windows and cost

Models do not read letters or words. They read **tokens**. Tokens decide your **cost**, your **speed** and how much text fits. Every AI engineer must be able to count them in their head and in code.

## What is a token?

A **token** is a small chunk of text, usually a piece of a word. The text is cut into chunks, and each chunk is replaced by a number (its **token id**). The model only ever sees the numbers.

The common method is **BPE** (byte-pair encoding). The idea: start with single characters, and keep merging the pairs that appear together most often in a huge text, until you have a vocabulary of about 30,000 to 200,000 chunks. Common words become one token. Rare words are split into pieces.

You can see it with the `tiktoken` library (`uv add tiktoken`), which holds OpenAI's tokenizers:

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
ids = enc.encode("Hello, world! Tokenization is fun.")
print(len(ids), ids[:3])
# -> 9 [9906, 11, 1917]
print([enc.decode([i]) for i in ids])
# -> ['Hello', ',', ' world', '!', ' Token', 'ization', ' is', ' fun', '.']
```

What to notice:

- 9 tokens for 34 characters. Roughly **4 characters per token** in English, or about **three quarters of a word per token**.
- A space belongs to the **start of the next word** (`' world'`).
- The long word was split: `' Token'` + `'ization'`.
- Numbers, code and punctuation use many tokens.

@@ grid 4 | Figure 2.1: text becomes tokens, and tokens become ids.
Hello|9906|blue
,|11|gray
 world|1917|blue
!|0|gray
@@ end

### Other languages cost more

The tokenizer was built mostly from English, so other scripts split into many small pieces:

```python
hindi = "नमस्ते दुनिया"
print(len(hindi), len(enc.encode(hindi)))
# -> 13 13
```

Thirteen characters became thirteen tokens, about one token per character, versus one per four characters in English. The same message in Hindi can cost **three or more times** as much and fill the context faster. Different models use different tokenizers, so counts differ a little. `tiktoken` is an **estimate** for non-OpenAI models. The exact count comes back in the API response (`usage`, chapter 3).

## The context window

The **context window** is the most text, in tokens, that the model can handle in one request. It holds **everything**: your system prompt, the chat history, any documents you paste, **and** the answer being written.

@@ flow | Figure 2.2: one window holds input and output together.
System prompt|rules for the model|gray -> History + documents|the conversation and facts|blue -> Question|the latest message|yellow -> Answer|written into the space that is left|green
@@ end

Think of a desk of fixed size. Papers (input) and the page you are writing on (output) must **both fit**. If the input already fills the desk, there is no room to write.

Window sizes vary by model, from about 8,000 to over a million tokens. They also keep changing, so look up the current number on the provider's model page (for Groq: `console.groq.com/docs/models`).

What happens if you go over:

- Most APIs return an **error** (a "context length exceeded" message).
- A chat app may silently **drop the oldest messages**, so the model forgets early facts.

A big window does not mean "use it all". More input costs more and is slower. Models can also pay less attention to facts in the **middle** of a very long text (the "lost in the middle" effect). That is one more reason to retrieve only the relevant pieces (RAG) instead of pasting everything.

## Cost math

APIs charge **per token**, with separate prices for **input** (prompt) tokens and **output** (completion) tokens. Output tokens usually cost more, because each one needs a full pass through the model. Prices are quoted **per million tokens**.

The formula:

```
cost = input_tokens / 1,000,000 * input_price
     + output_tokens / 1,000,000 * output_price
```

A worked example with made-up prices of 0.05 dollars per million input tokens and 0.08 per million output:

```python
input_tokens, output_tokens = 1200, 300
cost = input_tokens / 1e6 * 0.05 + output_tokens / 1e6 * 0.08
print(cost)
# -> 8.4e-05
```

That is 0.000084 dollars for one request, which sounds tiny. Now scale it: 1,000 users, 30 requests a day each is 30,000 requests a day.

```python
print(30_000 * 8.4e-05)
# -> 2.52
```

About 2.52 dollars a day with these small prices, but with a model that costs 100 times more per token it would be 252 dollars a day. **Always do this estimate before you build.**

Other levers that change cost, which later chapters use:

| Lever | Effect |
| --- | --- |
| shorter prompts | fewer input tokens |
| `max_completion_tokens` | caps output cost |
| a smaller model for easy tasks | much lower price per token |
| caching repeated prompts | pay once |
| retrieving 3 chunks instead of pasting 100 pages | far fewer input tokens |

## Counting before you send

When you build a system, count tokens before the call so you can trim or refuse:

```python
def count_tokens(text: str) -> int:
    return len(enc.encode(text))

history = ["Hi", "Hello! How can I help?", "Explain tokens"]
print(sum(count_tokens(m) for m in history))
# -> 11
```

(The real total sent is a bit more, because each message adds a few tokens of formatting.) A typical use is to **trim** history from the oldest end until it fits a budget (chapter 9).

::: {.box .checkpoint}
**Checkpoint:** you can estimate the tokens of a page of English text (about 500 to 700), explain why output is billed higher, and say what happens when a conversation grows past the window.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Counting words and assuming they equal tokens.
- Forgetting that **output** also uses the window and costs money.
- Putting a whole document in every request.
- No `max_completion_tokens`, so one request can run long and expensive.
- Assuming the token count of one model applies to another.
- Not checking the current price and window of the model, which change often.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is a token and how are they made?** A chunk of text, often a word piece, produced by a tokenizer such as BPE, which merges frequent character pairs into a fixed vocabulary.

**Q: Why are non-English texts more expensive?** The tokenizer's vocabulary is mostly English, so other scripts split into more, smaller tokens.

**Q: What is a context window?** The maximum number of tokens for prompt plus completion in one request.

**Q: Why is output priced higher than input?** Output tokens are produced one by one, each needing a full model pass, while input can be processed in parallel.

**Q: How do you cut LLM costs?** Shorter prompts, retrieval instead of pasting, output limits, caching, and a cheaper model for simple tasks.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Count the tokens of a paragraph of English and of the same paragraph in Hindi (or another language). Compare the ratio.
2. Write `fits(messages, limit)` that returns `True` if the total tokens are under the limit.
3. A request has 2,000 input and 500 output tokens. With prices of 0.10 and 0.30 dollars per million, find the cost, and the cost of 50,000 such requests.
4. Find the token ids of `"cat"`, `" cat"` and `"Cat"`. Why do they differ?
5. **Think:** why is it a bad design to paste a 200-page PDF into every request, even if the window allows it?
:::
