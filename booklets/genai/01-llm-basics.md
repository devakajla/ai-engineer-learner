# 1. AI, ML, GenAI and how an LLM works

Before you call any API, you need a correct picture of what a language model **is**. Almost every bug and every interview question in this field comes from a wrong picture. This chapter has almost no code, on purpose. We build the idea first.

## The family tree

These words are used loosely, so let us fix them.

@@ stack | Figure 1.1: each layer is a smaller part of the one below.
Generative AI|systems that make new text, images, audio, code|purple
Deep learning|machine learning with many-layered neural networks|blue
Machine learning|programs that learn patterns from data, not from hand-written rules|green
Artificial intelligence|any technique that makes machines act smart|gray
@@ end

- **AI** is the widest word. A chess program from the 1990s with hand-written rules is AI.
- **Machine learning (ML)** means you do not write the rules. You show many examples, and the program finds the pattern itself.
- **Deep learning** is ML using **neural networks**: layers of simple maths units. It is why modern AI got so good.
- **Generative AI (GenAI)** is deep learning that **creates** content. A spam filter *decides* (is this spam?). A GenAI model *writes* (here is a reply).

A **Large Language Model (LLM)** is the GenAI kind that works with text. "Large" means billions of numbers inside it (called **parameters** or **weights**), learned from a huge amount of text.

## The one idea: predict the next piece of text

An LLM does exactly one thing: given some text, it predicts what text is **likely to come next**. That is all. Writing an essay, answering a question, writing code: all of it is "predict the next piece, add it, repeat".

You can feel the idea with a tiny toy. It reads a short text and records which word followed which:

```python
text = "the cat sat on the mat the cat ate the fish the dog sat on the rug".split()
following = {}
for a, b in zip(text, text[1:]):
    following.setdefault(a, []).append(b)

print(following["the"])
# -> ['cat', 'mat', 'cat', 'fish', 'dog', 'rug']
```

After "the", the words seen next were cat (twice), mat, fish, dog, rug. So the toy "model" says: next word is `cat` with probability 2 out of 6, and each of the others 1 out of 6. To write, pick a next word by those odds and repeat.

What this toy shows, and the real thing shares:

- The model gives **probabilities**, not facts. It never "looks up" an answer.
- Text is generated **one piece at a time**, and each piece becomes part of the input for the next.
- Choosing by odds means the same input can give **different outputs**.

A real LLM replaces "the previous one word" with "the whole text so far", and replaces a count table with a giant neural network. But the loop is the same.

@@ flow | Figure 1.2: the generation loop.
Text so far|your prompt + anything already written|blue -> Model|computes odds for the next piece|yellow -> Pick one|by those odds|green -> Add to text|and go around again|blue
@@ end

## Inside: transformers and attention (the intuition)

Modern LLMs use an architecture called the **transformer**. You do not need the maths. You need the intuition.

Take the sentence: *"The trophy did not fit in the suitcase because **it** was too big."* What does "it" mean? The trophy. To know that, the model must **look back** at other words and decide which ones matter for this word. That mechanism is **attention**: for every word, the model scores how much it should pay attention to every other word.

Why this was a breakthrough:

- It sees the **whole text at once**, not word by word, so it can link far-away words.
- It can be trained in **parallel** on thousands of chips, so models could grow huge.

Two consequences you will meet again:

- The model can only look at a limited amount of text at once. That limit is the **context window** (chapter 2).
- Longer input means more attention work, so more cost and time.

## How a model is made

@@ flow | Figure 1.3: three stages.
Pre-training|read a huge pile of text;learn to predict the next piece|blue -> Instruction tuning|train on examples of;question and good answer|yellow -> Alignment (RLHF)|humans rank answers;the model learns to prefer good ones|green
@@ end

1. **Pre-training.** The model reads trillions of words from books, websites and code. It learns language, facts and patterns. The result is a **base model**: great at continuing text, but not a helpful assistant. Ask it a question and it may continue with *more questions*.
2. **Instruction tuning.** Train further on many examples of "instruction, then a good reply". Now it follows instructions.
3. **Alignment, such as RLHF** (reinforcement learning from human feedback). People compare answers, and the model learns to prefer helpful, honest, safe ones.

Remember: **knowledge is frozen at the end of training**, the *training cutoff*. The model does not know yesterday's news, and it knows nothing about **your** private documents. Fixing that is the reason RAG exists (chapters 10 to 14).

## What LLMs are good and bad at

| Good at | Weak at |
| --- | --- |
| writing, summarising, rewriting | exact arithmetic on big numbers |
| explaining, translating | knowing recent events |
| turning text into structure (JSON) | your private data, unless you provide it |
| writing and fixing code | being **sure** it is right |

### Hallucination

Because the model predicts *likely* text, not *true* text, it can produce a confident, fluent, **wrong** answer. This is called a **hallucination**. It is not lying, because the model has no idea of true and false. It continues the pattern. Much of this booklet is about reducing it: give the model the facts (RAG), ask for citations, check outputs, and measure with evaluations.

## Words you must know

| Word | Meaning |
| --- | --- |
| **prompt** | the input text you send |
| **completion** | the text the model sends back |
| **token** | a small piece of text, the unit the model works in (chapter 2) |
| **context window** | the maximum text (input and output) the model can handle at once |
| **parameters** | the learned numbers inside the model; more usually means more capable and more costly |
| **inference** | using a trained model, as opposed to training it |
| **temperature** | a setting that controls how random the choice of next piece is (chapter 4) |
| **open-weights model** | the weights can be downloaded (Llama, Mistral); **closed** ones are only reachable by API |

## How AI engineers work

An AI engineer almost never trains a model. The job is to **build systems around** a model: call it by API, give it the right text and tools, check its answers, and make the whole thing fast, cheap and safe. The chapters ahead follow exactly that path.

::: {.box .checkpoint}
**Checkpoint:** you can explain in two sentences why an LLM can state a wrong fact confidently, and why it does not know your company's documents.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Thinking an LLM looks facts up in a database. It generates likely text.
- Trusting a fluent answer because it sounds sure.
- Expecting the model to know recent events or private data.
- Thinking the model remembers earlier chats on its own. It does not (chapter 3).
- Mixing up AI, ML and GenAI in an interview.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is an LLM?** A neural network, usually a transformer, trained on huge text to predict the next token. Given text, it gives probabilities for the next piece and generates by repeating that step.

**Q: What is attention?** A mechanism that lets each token weigh how relevant every other token is, so the model can use context from anywhere in the text.

**Q: Why do LLMs hallucinate?** They produce statistically likely text, not verified facts, and have no built-in way to say "I do not know".

**Q: Base model vs instruction-tuned model?** A base model continues text. An instruction-tuned model was further trained to follow instructions and chat.

**Q: What is a training cutoff and why does it matter?** The date of the last training data. The model knows nothing after it, so recent or private facts must be supplied in the prompt.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Run the toy code. Print what follows `"sat"` and `"on"`. What does the toy predict after `"sat"`?
2. Extend the toy to look at the last **two** words instead of one. Does it make fewer wrong guesses on a longer text?
3. Write the loop that generates 8 words from the toy with `random.choice`. Run it with two different seeds.
4. In one sentence each, explain AI, ML, deep learning and GenAI.
5. **Think:** a user asks the model about a law passed last week. What should your system do instead of trusting the model?
:::
