---
title: AI, ML, GenAI and LLMs
summary: Start from zero. Learn what AI, machine learning and an LLM really are, how an LLM writes text one piece at a time, and why it sometimes makes things up.
plan_ids: []
---

You may have used ChatGPT. You type a question and a good answer appears. It feels like magic.

It is not magic. In this lesson you will see what is really going on, in plain words. You do not need any AI knowledge to start. If you can read a little Python, that is enough.

Why does this matter? Because an AI Engineer builds apps on top of these models. If you do not know what the model really does, its answers will surprise you. If you do know, you can plan around its strong and weak points.

In this track you will build one real project, **DevDocs Copilot**. It answers questions about API documentation and shows where each answer came from. Every lesson adds one piece.

## Words you will meet

Here are the words of this lesson in one place. Each one is explained again when it comes up.

| Word | Plain meaning |
| --- | --- |
| **AI** | Computers doing things that normally need human thinking |
| **ML** | AI where the computer learns from examples instead of fixed rules |
| **GenAI** | ML that creates new things: text, pictures, code |
| **Model** | The thing that was learned. A big pile of numbers |
| **LLM** | A model that works with language and predicts the next piece of text |
| **Training** | The learning phase. Slow and costly |
| **Inference** | Using the finished model. This is what an API call does |
| **Hallucination** | A confident answer that is false |

## Two ways to teach a computer

Say you want a program that finds spam emails.

**Way 1: write the rules yourself.** "If the email says *free money*, it is spam." You write rule after rule. Spammers change their words. Your rules break all the time.

**Way 2: show examples.** You give the computer 100,000 emails, each marked *spam* or *not spam*. The computer finds the patterns itself. Nobody wrote a rule.

Way 2 is **machine learning** (ML). The computer **learns the rules from examples**.

## AI, ML and GenAI: three words, three sizes

Think of three circles, one inside the other.

```
AI  (computers doing "smart" things)
 └── ML  (learning from examples)
      └── GenAI  (creating new things)
```

- **AI** is the big idea. Any program that seems to think.
- **ML** is one way to do AI. It learns from examples.
- **GenAI** (generative AI) is ML that **makes new content**: text, images, music, code.

A spam filter is ML. It *decides* (spam or not). A chatbot that *writes* a new email for you is GenAI. It *creates*.

## Your phone already does this

Open a messaging app and type "Good". Your phone suggests "morning", "night", "luck".

The phone looked at the words you typed so far and guessed the next word. That is the whole idea of an LLM, only much bigger.

An **LLM** (large language model) is like a phone keyboard that read a huge part of the internet. Instead of three suggestions for the next word, it picks one, adds it, and guesses again. It repeats this until a full answer exists.

Let's take the name apart:

- **Language**: it works with text.
- **Model**: a model is something *learned* from data. Here, it is a big pile of numbers. Those numbers are called **parameters**. Think of them as dials. Learning means turning the dials until the guesses get good.
- **Large**: billions of dials.

> The word "model" is used for the learned thing. When people say "I called the model", they mean "I sent text to the program with the learned numbers inside it and got text back".

## How one next word is chosen

(To be exact, a model works with small pieces of words called **tokens**. Lesson 2 explains them. For now, think "word".)

At each step, the model gives **every possible next word a chance**. Chances add up to 100% (1.0).

Here is a tiny toy version in Python. It is a dictionary. After the word `"I"`, the word `"like"` has a 60% chance and `"am"` has 40%:

```python
table = {
    "I": {"like": 0.6, "am": 0.4},
    "like": {"tea": 0.7, "coffee": 0.3},
}

table["I"]           # -> {'like': 0.6, 'am': 0.4}
table["like"]["tea"] # -> 0.7
```

A real LLM does the same thing. It just uses a huge learned model, not a small table you typed by hand.

### Step by step: pick the most likely word

The simplest choice is: take the word with the **highest chance**. Let's write that, using a different example (the weather):

```python
chances = {"sunny": 0.2, "rainy": 0.7, "cloudy": 0.1}
```

1. Start with "nothing found yet": `best = None` and `best_chance = 0`.
2. Go through every `word, chance` pair in the dictionary.
3. If this chance is bigger than `best_chance`, remember this word and this chance.
4. After the loop, `best` holds the winner.

```python
def most_likely(options):
    best = None
    best_chance = 0
    for word, chance in options.items():
        if chance > best_chance:
            best = word
            best_chance = chance
    return best

most_likely(chances)   # -> 'rainy'
most_likely({})        # -> None
```

An empty dictionary returns `None`, because nothing was found. This pattern is "find the biggest while you loop". It is called an **accumulator** pattern. You will use it in the first exercise.

### Step by step: make a whole sentence

One word is not an answer. To write a sentence, **repeat**:

1. Start with a list holding the first word.
2. Look at the **last** word in the list.
3. Find the most likely word after it, and add that word.
4. Go back to step 2. Stop when the sentence is long enough, or when the last word has nothing after it.

```python
words = ["I"]
words.append("like")     # best word after "I"
words.append("tea")      # best word after "like"
print(" ".join(words))   # -> I like tea
```

`" ".join(words)` glues the list into one string with spaces between the items.

That loop is the heart of every chatbot. Everything else in this track is built around it.

## Training and inference

A model has two phases in its life.

**Training** is the learning. The model reads a huge amount of text and turns its dials so its next-word guesses improve. Think of a student studying for years before an exam. Training takes weeks, thousands of special computers, and a lot of money. Only a few big companies do it.

**Inference** is the using. You send text, the model sends text back. The dials do **not** move. This is the exam. This is what happens when you call an API.

> When you chat with a model, it does **not** learn from you. Its training finished long before you arrived.

## What LLMs are good at

- Writing, rewriting and shortening text.
- Explaining things in simple words.
- Turning messy text into tidy data (for example, find the name and date in an email).
- Writing and explaining code.
- Translating between languages.

## What LLMs are bad at

- **Facts it never saw.** It does not know your private files, or news after its training stopped. That stop date is its **knowledge cutoff**.
- **Exact maths and counting.** It predicts text. It does not calculate.
- **Remembering.** Every call starts from nothing. It "remembers" a chat only if you send the old messages again (lesson 4).
- **Saying "I don't know".** It often answers anyway.

## Hallucination

A **hallucination** is when the model writes something that sounds right but is false. It may invent a function that does not exist, or a fake book title.

Why does it happen? The model picks **likely** words. A likely-sounding sentence is not always a **true** sentence. The model has no built-in "is this true?" check.

It sounds just as sure when it is wrong as when it is right. So for anything important, **check the answer against a source you trust**.

Here is a small version of that check in Python. We keep a set of trusted facts and look for claims that are not in it:

```python
trusted = {"Paris is in France", "2 + 2 = 4"}
claims = ["Paris is in France", "Paris is in Spain"]

for claim in claims:
    if claim not in trusted:
        print("unchecked:", claim)   # -> unchecked: Paris is in Spain
```

Later you will fix this properly with **RAG**: you give the model the right documents and tell it to answer only from them.

## Try it live

You do not need code yet. Open `console.groq.com`, sign in and open the **Playground**. Pick a model. Then try three things:

1. Ask: *What is 17 times 23?* Then ask the same question again. Did the wording change?
2. Ask about something that cannot exist, like *Explain the Python function `list.shuffle_fast()`.* Does it invent an answer?
3. Ask: *What happened in the news yesterday?* What does it say?

Write down what you see. This is what the lessons describe.

## A little deeper

- **The model gives chances, not one answer.** At every step it has a chance for every possible next token. Always picking the top one gives steady answers. Sometimes picking a lower one gives variety. The `temperature` setting controls this (lesson 5).
- **What is a neural network?** It is the shape of the model: many layers of numbers that pass signals to each other. Each layer changes the signal a little. You do not need to know more to use LLMs.
- **Transformer and attention.** The design inside almost every modern LLM is the **transformer**. Its key trick is **attention**: each word looks at the other words to decide what matters. In "The animal did not cross the street because it was tired", attention helps the model link "it" to "animal", not "street".
- **Base model vs chat model.** A base model only continues text. A chat model gets extra training to follow instructions. API models are usually chat models. The lesson on training stages (two lessons from now) goes deeper.
- **Open vs closed models.** Open models (like Llama) can be downloaded and run by anyone. Closed models are used only through the owner's API. Groq runs open models very fast on its own chips.

## Common mistakes

- Treating the LLM like a search engine or a database. It does not look facts up. It writes likely text.
- Believing an answer because it sounds sure of itself.
- Thinking the model learns from your chats. It does not. Inference never changes the model.
- Expecting it to know your company's documents. It only uses what you put in the prompt.

## Interview corner

**What is an LLM?**
A large neural network trained on a lot of text to predict the next token. Repeating that prediction produces full answers.

**What is the difference between training and inference?**
Training changes the model's numbers using data. It is slow and costly. Inference uses the fixed model to answer a prompt. It is what an API call does.

**What is a hallucination, and how do you reduce it?**
The model states something false with confidence. To reduce it: give trusted context (RAG), tell it to say "I don't know" when the context has no answer, lower the temperature, and check the output.

**Why can't an LLM answer questions about your private documents?**
It never saw them in training. You must put the relevant text in the prompt. RAG is the standard way to do that.

## Summary

- Machine learning means learning rules from examples. GenAI is ML that creates new content.
- An LLM predicts the next token, over and over, like a very large phone keyboard.
- A model is a pile of learned numbers (parameters, like dials).
- Training changes the dials. Inference (an API call) does not.
- LLMs are strong with language. They are weak with fresh facts, exact maths and memory.
- Hallucinations are confident mistakes. Check against trusted sources and give the model the right context.
- Reference: `reference/genai-groq.md` (the Groq calls you will write in the next lessons).
