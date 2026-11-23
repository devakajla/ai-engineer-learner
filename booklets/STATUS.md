# Booklets: status and handoff

Last updated: 2026-11-22. Read this first when you continue the booklet work. The full plan and chapter lists are in `OUTLINE.md`.

## Goal

Seven PDF booklets for Dev's daily reading, separate from the website: Backend, Python, FastAPI, GenAI, Agentic AI (LangChain + LangGraph), DevOps, System Design. Dev is working toward a job as an AI Engineer. DSA stays on the website, up to medium level. No booklet for DSA.

## Status per booklet

| Booklet | Status | Folder | PDF |
| --- | --- | --- | --- |
| Python | Done, Dev reviewed and is satisfied (112 pages) | `python/` | `_build/python.pdf` |
| GenAI | Done, written 2026-11-22, not yet reviewed by Dev (128 pages, 34 diagrams) | `genai/` | `_build/genai.pdf` |
| FastAPI | Old code-heavy version exists (158 pages). Needs a redesign in the new style | `fastapi/` | `_build/fastapi.pdf` |
| Backend | Not started (check the 50/50 rule and add a start guide) | none | none |
| Agentic AI | Not started | none | none |
| DevOps | Not started | none | none |
| System Design | Not started | none | none |

Work one booklet at a time. Dev reviews each one before the next starts.

## Style rules (apply to ALL booklets)

- **About 50% explanation and 50% code.** Dev said the first FastAPI booklet had far too much code. The goal is understanding, not code without theory.
- Order for every concept: plain everyday meaning, why it exists, a picture or mental model, a SMALL example (3 to 8 lines) with the output as `# ->`, a line-by-line "what just happened" in words, then the trap.
- Every long code block must be explained right after it. Long code only in guided builds.
- Simple English. Explain a jargon word the first time it appears. No shortening of topics.
- Start of every booklet: a Quick Reference (with a "what is in this booklet" table and a suggested daily rhythm).
- Every chapter ends with: Checkpoint, Common mistakes, Interview corner, Exercises. Exercise answers go in `99-answers.md`. The last chapter is an interview question bank.
- Run every code example and paste the real output. State clearly what was not run (for example Groq calls, Docker).

## How to build

```
cd /Users/dev/Projects/Learner/booklets
./build.sh <folder> "<Title>" "<Subtitle>"
```

Output: `_build/<folder>.pdf`. Chapters are read in filename order (`00-quick-reference.md`, `01-...md`, ..., `99-answers.md`). The pipeline is: `diagrams.py` (diagram DSL to inline SVG), then pandoc, then headless Chrome to PDF. After a build, check that `_build/<name>.html` has no leftover `@@` and no literal `\|`.

## Diagram DSL (`diagrams.py`)

- Blocks: `@@ flow|vflow|stack|grid N | caption` then lines, then `@@ end`.
- Box format: `Title|line1;line2|color`. Colors: blue, green, yellow, red, purple, gray. Do not put `;` in the Title.
- Arrows: `->` and `-label->`. Avoid `-.->` and avoid `>` inside box text.
- In a `vflow`, link every row with arrows, or extra rows get dropped.
- Use at most 3 or 4 columns in a grid (6 columns gives tiny text).
- Pandoc divs: `::: {.box .checkpoint}`, `.mistake`, `.interview`, `.exercise`, `.why`, `.step`, `.fastapi`.
- In pipe tables, never put a `|` inside a code span (it renders as `\|`). Use prose or a code block instead.

## Next steps (in order)

1. Dev reviews `_build/genai.pdf`. Fix whatever Dev points out.
2. **FastAPI redesign.** Rewrite chapters 00 to 19 and `99-answers.md` in the 50/50 style. Add the start guide. Keep the TaskFlow guided build. Cut repeated full-file code to diffs and explain each block. Re-verify against the reference project (16 tests passed there). Chapters with the most code: ch06, ch08, ch11, ch15, ch13, ch16.
3. Backend booklet (14 chapters in `OUTLINE.md`). Each chapter ends with a "How FastAPI does this" box.
4. Agentic AI booklet (LangChain + LangGraph, 17 chapters).
5. DevOps booklet, then System Design booklet.
6. Optional: update the status section of the project `CLAUDE.md`.

## Postponed (not now)

- Website landing page with a streak and a done-gate (quiz above 75 percent, code tests, an AI round using Haiku).
- The hard mentor.
- New site quizzes and exercises for the new topics.

## GenAI booklet: facts to reuse

- Groq SDK 1.7.0 is installed in the Learner venv. Use `Groq(api_key=..., max_retries=0, timeout=10)`. Use `max_completion_tokens`, not `max_tokens`. Default model `llama-3.1-8b-instant`. Tell readers to check `console.groq.com/docs/models`.
- No Groq API key was ever used. The booklet's Groq calls, real `fastembed` embeddings, pgvector, Qdrant, Hugging Face, Ollama, vLLM, PDF parsing and image or audio message formats were NOT run. Offline pieces (tokens, softmax, cosine, chunking, BM25, RRF, metrics, Chroma with a toy embedder, retry, repair loop and tool loop with fake clients, mini RAG, semantic cache, PII mask, tracing) were run.
- Run Python with `cd /Users/dev/Projects/Learner && uv run python ...`, or `uv run --with tiktoken python ...` for tiktoken. numpy and chromadb are in the venv.
- Chroma: use unique collection names (the in-process client shares state). `add` with an existing id keeps the old item. `upsert` replaces it. Cosine distance is smaller-is-better.
- Scratch scripts from the work are in the session scratchpad (`g1.py` to `g8.py`) and may be cleared. They are not needed to continue.

## FastAPI booklet: facts to reuse

- TaskFlow guided build. Layers: route, service, repository, database. Imports go downward only.
- The verified reference project was in a session scratchpad (`.../scratchpad/ref/`) and may be gone. If it is gone, rebuild it from `content/fastapi/15-testing/project/solution` and re-run its tests.
- Docker, the ARQ worker and Groq were not run (Docker is not installed on this machine). Say so in the booklet.
- In `fastapi/00-quick-reference.md`, a table cell was changed to `` `limit: int = 20` `` because of the pipe rendering problem.

## Related memory

`~/.claude/projects/-Users-dev-Projects-Learner/memory/booklet-style-understanding-first.md` holds Dev's style feedback (understanding first, about 50/50).
