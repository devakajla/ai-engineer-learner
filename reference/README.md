# Reference

One place for methods, built-ins and patterns, with short theory and runnable examples. It is for **all tracks**, not only DSA. Look things up here instead of searching the web.

| File | What is inside | Taught in |
| --- | --- | --- |
| [builtins-and-math.md](builtins-and-math.md) | `len sum min max abs round divmod range`, `// % **`, digit tricks | `python/03`, `dsa/02` |
| [strings.md](strings.md) | slicing, `split join strip replace find count`, `ord chr`, checks | `python/04`, `dsa/06` |
| [lists.md](lists.md) | `append pop insert remove sort sorted`, slicing, `enumerate` | `python/08`, `dsa/07` |
| [tuples.md](tuples.md) | unpacking, swap, `zip`, star unpacking | `python/09`, `dsa/08` |
| [sets.md](sets.md) | `add discard`, union, intersection, seen-set | `python/10`, `dsa/09` |
| [dicts.md](dicts.md) | `get items setdefault`, counting, grouping | `python/11`, `dsa/10` |
| [comprehensions-and-sorting.md](comprehensions-and-sorting.md) | list comprehensions, `sorted(key=)`, grids, records | `python/12`, `dsa/11` |
| [functions-and-patterns.md](functions-and-patterns.md) | defaults, early return, and the recurring problem patterns | `python/13`, `dsa/01-05, 12` |
| [heap-and-deque.md](heap-and-deque.md) | `heapq` push/pop/heapify/nlargest, `deque` queue | `dsa/24`, `dsa/27` |
| [genai-groq.md](genai-groq.md) | `Groq` client, messages and roles, settings, streaming, errors and retries, tokens and cost, prompt patterns, templates, JSON, Pydantic checks, tool calling, chat memory | `genai/02-12` |
| [genai-retrieval.md](genai-retrieval.md) | embeddings, numpy and cosine similarity, chunking, Chroma, BM25, reciprocal rank fusion, retrieval metrics | `genai/14-20` |

## Entry format

Each entry has: **signature**, **theory** (what it does, new object or in place, cost where it matters), a runnable **example** with `# ->` output, and a **gotcha**.

## Rule for new lessons

Any lesson (any track) that introduces a method or built-in must add or update its entry here, and link back to this folder in its "Summary".
