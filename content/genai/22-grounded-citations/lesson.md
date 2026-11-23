---
title: Grounded answers and citations
summary: Make a RAG answer point to its sources - ask for [n] citations, read and check them in code, show sources to the user, and repair answers that cite wrongly.
plan_ids: []
---

In lesson 21 your bot answers from the retrieved chunks. But how does a **user** know the answer is right? And how do **you** know it did not invent something?

The answer is **citations**. A cited answer says where each fact came from:

```
Use the DELETE endpoint to remove a task [1]. You must send a token [2].
```

The user can open source `[1]` and check. This is what builds trust, and it is a must for serious RAG.

## What does "grounded" mean?

An answer is **grounded** when every claim in it is supported by the given context. The opposite is a hallucination: a claim that is not in the context.

Grounding is not one switch. It is a chain of small habits:

1. Tell the model to answer only from the context (lesson 21).
2. Tell it to **cite** a source after each fact.
3. **Check** the citations in code.
4. **Show** the sources to the user.
5. Allow "I don't know".

## Step 1: ask for citations

You already number the chunks (`[1]`, `[2]`). Add one rule to the system prompt:

```
After each fact, cite the context number in square brackets, like [1].
```

Models follow this well, but not perfectly. Some forget. Some invent numbers. So you must check.

## Step 2: read the citations in code

The answer is just text. To find `[1]` and `[2]` in it, you scan the text. There is a tool for patterns in text (regular expressions), but you can do it with simple string methods.

Let's practise the scan with a different example: find the numbers inside round brackets, like `(7)`.

1. Make an empty list `numbers`.
2. Start at position `i = 0`. While `i` is inside the text:
3. If the character is `(`, find the next `)` with `text.find(")", i)`. `find` gives `-1` when there is none: then stop.
4. Take the text between them. If it is all digits (`.isdigit()`), turn it into an `int` and add it (once).
5. Move on.

```python
def numbers_in_round_brackets(text):
    numbers = []
    i = 0
    while i < len(text):
        if text[i] == "(":
            j = text.find(")", i)
            if j == -1:
                break
            inner = text[i + 1:j]
            if inner.isdigit():
                n = int(inner)
                if n not in numbers:
                    numbers.append(n)
                i = j + 1
                continue
        i += 1
    return numbers

numbers_in_round_brackets("a (2) b (x) c (2) d (10)")   # -> [2, 10]
numbers_in_round_brackets("no brackets")               # -> []
```

Look at the last lines of the loop: when we find a number we jump past the bracket (`i = j + 1`) and use `continue`. Otherwise we move one step (`i += 1`). You need the same care in the first exercise, with square brackets.

## Step 3: check the citations

Two things can go wrong:

- **No citation.** The model forgot.
- **A made-up citation.** It wrote `[7]` but you gave it only 3 chunks.

So after reading the numbers, check them against the number of chunks:

```python
def check(numbers, n_hits):
    valid = [n for n in numbers if 1 <= n <= n_hits]
    invalid = [n for n in numbers if n < 1 or n > n_hits]
    return {"valid": valid, "invalid": invalid, "ok": bool(valid) and not invalid}

check([1, 7], 3)   # -> {'valid': [1], 'invalid': [7], 'ok': False}
check([2], 3)      # -> {'valid': [2], 'invalid': [], 'ok': True}
check([], 3)       # -> {'valid': [], 'invalid': [], 'ok': False}
```

`bool(valid)` is `True` when the list has something in it. `1 <= n <= 3` is a **chained comparison**: it means "1 is at most n, and n is at most 3".

## Step 4: show the sources

The citation `[1]` means "chunk 1 of the list I sent". Your code still holds that list, so it can turn the number into a **source**: the file and the heading. Show them under the answer, or as links.

```
Answer: Use DELETE [1]. A token is needed [2].
Sources:
  [1] tasks.md > Delete
  [2] auth.md
```

You must keep the **same list of hits** you put in the prompt. If you reorder it afterwards, `[1]` would point to the wrong chunk.

## Step 5: repair

If the check fails, one more try often fixes it. Do what you did in lesson 10 (the repair loop): add the bad answer, add a user message that says what is wrong, and call again. Limit it to **two** calls in total. If it still fails, return the answer marked as **not ok**, so your app can warn the user.

One special case: **"I don't know."** has no citation, and that is correct. Do not count it as a failure.

## A valid citation does not mean a true claim

This is the trap. The check above only checks that the **number exists**. The model can cite `[1]` for a claim that chunk 1 does not support. Real checks need more:

- **Quote check.** Ask the model to include a short **exact quote**. Then your code checks that the quote is really inside the chunk (`quote in chunk_text`). A quote that is not there is a made-up quote.
- **Judge.** Ask a second model call: "Is this claim supported by this text?" (lesson 41).

Citations make errors **easy to find**. They do not make errors impossible.

## Try it live

Use your RAG from lesson 21 with the cite rule.

1. Ask 5 questions whose answers are in your docs. How often does the model cite correctly on the first try?
2. Make the model fail on purpose: tell it in the system prompt "cite with [A], [B]". See what your check says.
3. Ask a question that is not in the docs. Does it say "I don't know", or does it invent a citation?
4. Take one answer and open the cited chunk. Is the claim really there?

## A little deeper

- **Sentence level.** You can check each sentence of the answer for at least one citation, and flag the uncited ones (lesson 26 drill).
- **Several citations in one bracket.** Models sometimes write `[1, 2]` or `[1][2]`. Your parser should decide what it accepts. Telling the model the exact format helps.
- **Structured output.** Instead of free text, ask for JSON: `{"answer": ..., "citations": [1, 2], "quotes": [...]}` and validate it with Pydantic (lesson 10). It is easier to check than text.
- **Native citation features.** Some providers have built-in citation or "grounded generation" modes. The checks are still your job.
- **Citing the right level.** Cite the chunk, but show the user the **document and section**, and a link if you have one.
- **Don't rank by citations.** A model that cites a lot is not always more correct.

## Common mistakes

- Trusting the citation numbers without checking them against the list.
- Reordering or filtering the hits after the model has seen them.
- Treating "I don't know" as a failed answer.
- Assuming that a valid `[1]` proves the claim is supported.
- Repairing forever. Limit the tries.
- Showing sources to the user that the model did not actually use.

## Interview corner

**What is a grounded answer?**
An answer where every claim is supported by the retrieved context. We help the model get there with an "only the context" rule, citations, an "I don't know" option, and checks in code.

**How do you implement citations in RAG?**
Number the chunks in the prompt, ask the model to cite `[n]` after each fact, parse the numbers, check they are in range, map them back to sources, and show the sources. Retry once if the check fails.

**A citation is valid, but the claim is wrong. How do you catch it?**
Ask for an exact quote and verify it is inside the cited chunk, or use a judge (a second model call or a trained checker) to test if the chunk supports the claim.

**Why is "I don't know" important?**
Without it, the model is pushed to answer, and invents when the context is missing. It is the safe exit that keeps the system honest.

## Summary

- Grounded: every claim is supported by the retrieved context.
- Ask the model to cite `[n]` after each fact. Number the chunks in the prompt.
- Read the numbers with simple string scanning. Check that they are in range and that at least one exists.
- Map citations back to the same hit list to show sources. Never reorder that list.
- Repair once with the error message. After the limit, return "not ok".
- "I don't know." is a valid answer with no citation.
- A valid number does not prove the claim. Use quotes or a judge for more.
- Project: step 13 adds `copilot/citations.py`: checked citations.
- Reference: `reference/genai-retrieval.md`.
