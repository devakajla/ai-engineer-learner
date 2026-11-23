# Learner

A personal learning app for Dev, who has read only a little Python and is working toward AI Engineer. Content starts at absolute-beginner level and gets harder slowly, level by level. Tracks: **Python**, **FastAPI**, **DSA** (drill-first; see the DSA section below) and **GenAI** (Groq, embeddings, RAG; see the GenAI section below).

- Backend: FastAPI JSON API in `app/` (SQLite via SQLAlchemy async). Claude is reached through `claude-agent-sdk`, which uses the local `claude` CLI login — no API key.
- Frontend: Next.js (App Router, TypeScript, plain CSS) in `frontend/`. Pages: `app/[track]/[slug]/page.tsx`; components in `frontend/components/`; API client in `frontend/lib/api.ts`.

Run both: `./dev.sh` → http://localhost:3000 (API on :8000)
Validate content: `uv run python scripts/validate_content.py`
Tests: `uv run pytest`

The source curriculum is `~/Downloads/ai-engineer-learning-plan.md` (topic IDs PY-xx, FA-xx).

## Content authoring rules (read before writing any lesson)

### Where things go
```
content/<track>/track.yaml        # THE order. Every lesson is listed here, written or not.
content/<track>/<NN-slug>/lesson.md
content/<track>/<NN-slug>/quiz.yaml
content/<track>/<NN-slug>/exercises/<NN-slug>/{prompt.md, starter.py, solution.py, test_solution.py}
content/<track>/<NN-slug>/project/{step.md, test_step.py, solution/}   # FastAPI track only
```
- Lesson ids are `<track>/<NN-slug>` and are stored in the DB. **Never rename a lesson folder that already exists.**
- `track.yaml` entries: `{slug, title}`; interview modules add `kind: interview`; the Interview track uses `{ref: <track>/<slug>, title, kind: interview}`.
- A listed lesson without a folder shows as "coming soon". Write the folder to publish it.

### Sequence rule (most important)
A lesson may only use concepts taught in **earlier lessons of the same track** (or of the tracks listed as prerequisites). If an example needs something not taught yet, either simplify it or add a one-line "you'll learn X in lesson N" note. Exercises follow the same rule.

### lesson.md
- YAML front matter: `title`, `summary` (one sentence), `plan_ids` (list, may be empty).
- Simple English (not Hinglish): short everyday words, short sentences and paragraphs. Explain *why*, then *how*. Every concept gets a small runnable example with its output shown as a comment (`# -> 42`).
- Structure: intro (why this matters) → `##` sections per concept → "A little deeper" (optional, harder side-details) → "Common mistakes" → "Interview corner" (2–4 questions with short answers, from Level 2 on) → "Summary" (bullets).
- `> ` blockquotes for tips/warnings. No raw HTML.
- Level 1 lessons are for beginners: assume the learner has read only a little Python. Never write "you already know" or "you already write Python at work". Level 2 builds slowly on Level 1, and Level 3 is the advanced level.

### Beginner-friendly rewrite (in progress, Python track first)
Existing lessons were written for an experienced programmer. We are rewriting them one at a time, starting at Level 1, and Dev reviews each lesson before the next one starts.
- **Scope: only `lesson.md` changes.** Do NOT touch exercises (`prompt.md`, `starter.py`, `solution.py`, `test_solution.py`) or `quiz.yaml`. Do not add, remove or rename lessons or folders. `reference/` stays as it is unless Dev asks.
- **Keep every concept.** Before rewriting, list every concept that the lesson's exercises and quiz questions need (including twists such as `bool` being an `int`). The new lesson must still teach each one. Never move a concept to a later lesson.
- **Simplify the way it is taught, not what is taught:**
  - Start each concept with its plain, everyday meaning, then the smallest example with its output as `# ->`.
  - Explain a jargon word the first time it appears (mutable, shallow copy, bytecode, singleton, ...) or use a simpler word.
  - One idea per paragraph. Easy ideas first, then harder ones.
  - Move harder side-details into the "A little deeper" section.
- **Prepare the learner for the exercises.** Include a step-by-step worked example in the lesson that shows the same pattern as the lesson's first exercise. Never show or copy an exercise's solution.
- The sequence rule still applies. Keep front matter (`title`, `summary`, `plan_ids`) valid.

### quiz.yaml
List of `{q, type: single|multi, options: [...], answer: [indices], explain}`. 5–8 questions per lesson. Mix concept checks with "what is the output" questions (code in fenced blocks inside `q`). `single` has exactly one answer index; `multi` has one or more. `explain` says why the right answer is right.

### exercises
- 2–4 per lesson, easy → harder. `prompt.md` starts with `# Title`, states the function signature, rules and 2 examples.
- `starter.py` has the signature and `...`/`pass` body; it must FAIL the tests.
- `solution.py` is the reference; it must PASS. Never shown to the learner.
- `test_solution.py` does `from solution import ...`, covers examples + edge cases, plain `assert`s with clear messages. No network, no sleeping, fast.
- Extra data files in the exercise folder are copied next to the code at run time.
- FastAPI exercises: learner writes `app` in `solution.py`; tests use `fastapi.testclient.TestClient`.

### FastAPI track: theory + backend concept + the TaskFlow project
- Every FastAPI lesson teaches the FastAPI feature AND the backend concept behind it (a "Backend concept" section), plus "Common mistakes" and "Interview corner".
- Every lesson ends with a **project step** that grows one real app, **TaskFlow** (task-manager API), in the learner's own folder (default `~/Projects/taskflow`, set in the UI).
- `step.md` starts with `# Step N — Title`, shows the target folder structure, explains the *why* of each best practice, ends with a "Checkpoint" paragraph.
- `test_step.py` runs with **cwd = the learner's project** (imports `from app.main import app`, reads files via `Path.cwd()`), inside the project's own env (`uv run --project <dir> --with pytest --with httpx`). Give every assert a helpful message.
- `solution/` is the full reference project **at the end of that step** (copy the previous step's solution, then change it). The validator runs `test_step.py` against it and also checks that an empty folder fails.
- Exception: the gap-filler lessons `25-pydantic-validation`, `26-forms-files-cookies`, `27-app-lifecycle-docs`, `28-db-patterns` and `29-llm-backend-patterns` have **no project step**. They sit in `track.yaml` between older lessons, and their folder numbers (25+) do not follow the track order. This keeps TaskFlow step numbers and the solution chain intact. Never renumber the TaskFlow steps.
- From step 6 on, the API lives under `/api/v1` with the layout `app/{core,api/routes,schemas,services,repositories}`. Later steps must keep earlier behaviour working.

After writing content, ALWAYS run `uv run python scripts/validate_content.py` and fix every error.

### DSA track: drills, question sheet, reference
- DSA is **drill-first**: a short "toolbox" `lesson.md` plus **5-7 graded exercises** (easy → hard) per lesson. This overrides the 2–4 exercise rule. Interview corner is not required in the warm-up levels (L1 Logic & Functions, L2 Built-in Data Structures).
- Prerequisite: Python Level 1. A DSA lesson may use Python L1 concepts and earlier DSA lessons only. No lambda/closures/classes until taught.
- Every `prompt.md` has: signature, rules, 2 examples, `**Think first:**` (a question, not the answer) and `**Hint:**` (the tool to use). Pattern functions return `list[str]` so they are testable.
- Lesson 01 teaches the 5-step routine (understand, example by hand, plan, code, test edges). Name the pattern used (accumulator, counter-dict, seen-set, ...) so it becomes reusable.
- **Question sheet:** `content/dsa/QUESTIONS.md`. Add a row for every new DSA exercise (ID, title, diff E/M/H, pattern). When Dev says a question is solved, tick `[x]`, fill the date and update the `Progress: n/N` line. Done = Dev solved it (tests pass).
- **Reference docs:** `reference/` (all tracks, not DSA-only). Any lesson that introduces a method or built-in must add/update its entry there (signature, plain-English theory, `# ->` example, gotcha). Link to it from the lesson's Summary.

### GenAI track: Groq, embeddings, RAG, DevDocs Copilot
- Prerequisite: Python Level 1. A GenAI lesson may use Python L1 ideas (functions, dicts, loops, try/except) and earlier GenAI lessons only. No classes, lambda or closures in lesson code until taught. (Test files may use anything.) Exception: lesson 10 teaches Pydantic `class X(BaseModel)` with a "copy this shape, classes come in Python lesson 19" note. Project solutions avoid closures: tool functions take the spec as first argument.
- LLM provider: **Groq** (`groq` SDK, key in `GROQ_API_KEY`, never in the repo). Default model `qwen/qwen3.8-27b` (set by Dev 2026-11-23; not verified against the live Groq model list). Use `max_completion_tokens` (`max_tokens` is deprecated). Model names change: tell the learner to check `console.groq.com/docs/models`. Sources disagree on whether Groq has an embeddings endpoint, so Level 3 uses a local embedder (`fastembed`, `BAAI/bge-small-en-v1.5`, 384 dims). Project code never imports `fastembed` at module level (lazy import in `copilot/embed.py`), and `fastembed` is NOT in the Learner `pyproject.toml`: tests pass a fake `embed` function. `numpy` and `chromadb` are in `pyproject.toml`; Chroma runs with `anonymized_telemetry=False`. Chroma calls in tests use unique collection names (the in-process client shares state).
- Vector DB path: cosine similarity by hand with numpy, then Chroma, then only an intro to pgvector/Qdrant.
- **Exercises are offline.** Functions take a `client` argument. `test_solution.py` passes a fake client (`types.SimpleNamespace` objects, records calls). No network, no sleeping (pass a delay of 0 or skip waits).
- Every GenAI lesson has "A little deeper" and an "Interview corner" (also in Level 1). Interview lessons: L2, L3, L4, L5.
- Project: **DevDocs Copilot** (default folder `~/Projects/devdocs-copilot`, package `copilot/`). Answers questions about API docs with citations, hybrid search, tool calling against TaskFlow, an eval harness and cost/latency logging. Project steps live on the lessons that need them (step 1 = lesson 03, step 2 = 04, step 3 = 06, step 4 = 08, step 5 = 10, step 6 = 11, step 7 = 12, step 8 = 15, step 9 = 16, step 10 = 17, step 11 = 18, step 12 = 21, 13 = 22, 14 = 23, 15 = 39, 16 = 40, 17 = 24, 18 = 25, 19 = 41). Each step's `solution/` is a copy of the previous one plus the new files. `test_step.py` uses fake clients and `groq` exceptions built by hand, never the network. The validator runs solutions in the Learner venv, so any import a solution needs must be in `pyproject.toml`.
- Project name and default folder per track: `TRACK_PROJECTS` in `app/config.py`.

### Booklets (PDF, separate from the website)
Seven PDF booklets for Dev's daily reading, in `booklets/`. They are NOT linked from the site and do not touch `content/`. **Read `booklets/STATUS.md` first** (status, next steps, facts to reuse) and `booklets/OUTLINE.md` (chapter lists for all seven).
- Booklets: Backend, Python, FastAPI, GenAI, Agentic AI (LangChain + LangGraph), DevOps, System Design. DSA has no booklet (stays on the site, up to medium).
- Work one booklet at a time. Dev reviews each before the next starts.
- **Style (all booklets): about 50% explanation and 50% code.** Per concept: plain everyday meaning, why it exists, a picture or mental model, a SMALL example (3 to 8 lines) with `# ->` output, a line-by-line "what just happened", then the trap. Every long code block is explained right after it. Simple English, many diagrams, no shortened topics.
- Each booklet starts with `00-quick-reference.md` (with a "what is in this booklet" table and a daily rhythm). Each chapter ends with Checkpoint, Common mistakes, Interview corner and Exercises. Answers in `99-answers.md`. The last chapter is an interview question bank.
- Run every code example and paste real output. Say clearly what was not run.
- Build: `cd booklets && ./build.sh <folder> "<Title>" "<Subtitle>"` gives `booklets/_build/<folder>.pdf` (diagrams.py, then pandoc, then headless Chrome). Diagram DSL: `@@ flow|vflow|stack|grid N | caption` ... `@@ end`, boxes `Title|line1;line2|color`. Never put a `|` inside a code span in a pipe table.

---

## Project status (update this section after each chunk of work)

Last updated: 2026-11-22. Validator at last run (2026-11-18): 105 lessons, 694 quiz questions, 573 exercises, 25 project steps, all passing.

### Booklets status (2026-11-22)
- **Python:** done, Dev reviewed and is satisfied (112 pages).
- **GenAI:** done (128 pages, 34 diagrams), waiting for Dev's review. Groq calls, real embeddings, pgvector, Qdrant, Hugging Face, Ollama and vLLM were not run.
- **FastAPI:** old code-heavy version exists (158 pages). Needs a redesign in the 50/50 style. This is the next task.
- **Backend, Agentic AI, DevOps, System Design:** not started.
- Booklets are paused (Dev's call, 2026-11-22) and kept separate from the plan and the site.

### Site changes (2026-11-22, approved plan)
Booklets are separate (PDF only, paused) and are NOT part of the plan or the site. The plan is site lessons only.
Built: home page `frontend/app/page.tsx` ("Do this now" card with a Start button that opens the right lesson tab via `?tab=`, Haiku Guide panel, rest of today), `/plan` (`frontend/app/plan/page.tsx`: 121-day heatmap, per-topic bars, week by week), `content/roadmap.yaml` (generated by `scripts/build_roadmap.py`: edit WEEKS there and rerun, also rerun after writing new lessons so the plan gets their quiz and exercise ids), `app/routers/roadmap.py`, table `roadmap_done`, tests in `tests/test_app.py`. Preview any day: `/?on=2026-12-02`.
- Plan (121 days, about 223 h): Python 01-29, then FastAPI, with GenAI running beside it; Python L3 comes later (30-31 just before FastAPI async in week 8, 32-35 in weeks 13-14); DSA is one exercise stream, 4 to 5 a day Mon-Fri; then Backend (4), Agentic AI (10), DevOps (4), System Design (6) and a capstone; Sunday review; last week revision.
- Gate: a lesson task is done only when its quiz is 75%+ and every exercise of the task passes (and the project step check, if any). Review tasks and lessons not written yet are ticked by hand. Plan never shifts; past undone tasks are overdue. Streak = consecutive days with all tasks done.
- Guide (Haiku, the strict mentor): panel on the home page. `GET /api/roadmap/guide` streams a short briefing (Now / How / Watch, firm when tasks are overdue, cached per plan state) and `POST /api/roadmap/ask` answers a question about the plan. Both use the "review" model setting (Haiku).
- Day 1 is Sunday 22 Nov and already has lessons (Python 01-02); there is no orientation day.
- Not built yet: a Haiku quiz round inside the done-gate (the Guide is the Haiku part for now). The plan lists lessons that do not exist yet (FastAPI 17-24, 29; GenAI 21-31; Backend, Agentic AI, DevOps, System Design modules): write them before their weeks (see `ready_by` in the yaml), then rerun the script.

### GenAI + Agentic 9-week plan (2026-11-23, approved)
Plan file: `~/.claude/plans/listen-we-need-to-expressive-wozniak-of-053ab55c-2bce-4894-a3f3-f80e35080294.md` (week by week, 23 Nov 2026 to 23 Jan 2027). Site lessons only, real Groq key (live "Try it live" sections), start from zero GenAI knowledge, exercises chain level by level (later starter.py includes earlier solutions as "given" code). For GenAI this overrides the "do not touch exercises/quiz" rule; keep folder names.
- **W1 done (2026-11-23), validator green:** rewrote lessons 01, 02 (+KV cache, 4th exercise `call_report`), 03; edited 04, 05 (+top_k); NEW `32-training-stages` (listed after 02) and `33-model-choice` (listed after 05); chained exercises (01/02-generate uses given next_word, 04/03 uses add_turn, 05/03 uses build_messages). Lesson 06 (streaming, errors) is W2 day 1.
- Default model changed to `qwen/qwen3.8-27b` everywhere in `content/genai` and `reference/` (2026-11-23). Not verified against Groq's live list (no key in this shell); Qwen may emit thinking text, check when Dev runs it.
- **W2 done (2026-11-23), validator green:** 06 (+intro, try-it-live), 07 (+system prompt design, self-consistency, new ex 04 `majority-vote`, classify uses given `pick_label`), 08 (+form-letter intro, new ex 04 `render-prompt` built from render + get_prompt), 09 (+JSON schema mode, new ex 04 `schema-format`, ask_json uses given parse_json), 11 (+parallel tool calls section). 10 not changed, 12 is W3 D1, 13 is the W2 Saturday drill (unchanged).
- **Level 1 fixed (2026-11-23), validator green (109 lessons, 728 quiz questions, 589 exercises):** all of L1 is now zero-knowledge style: 01, 02, 03, 04, 05, 06 fully rewritten; 32 and 33 new; NEW `34-reasoning-thinking` (listed after 06: thinking text, reasoning_format, split_thinking, reply_parts, thinking_share) and NEW `35-l1-llm-client` (L1 project: `chat`, `call_cost`, `safe_ask`, built from given L1 pieces). L1 order in track.yaml: 01, 02, 32, 03, 04, 05, 33, 06, 34, 35. Exercise chain: generate<-next_word, chat_turn<-add_turn, ask_with<-build_messages, ask_with_retry<-backoff_delays (new `sleep` arg), 35 uses all. `reasoning_format` details are from memory, check Groq docs.
- **W2 completed (2026-11-23), validator green (110 lessons, 735 quiz, 592 exercises):** NEW `36-l2-assistant` (L2 project, listed after 11): `prepare_messages`, `ask_structured` (repair loop for any Pydantic class), `assistant` (plain / structured / tools), chained with given code. Added Try-it-live to 08, 09, 10, 11; lesson 10 repair loop now shown with a different shape. 07-11 are still edited, not full zero rewrites.
- **W3 built (2026-11-23), validator green (112 lessons, 749 quiz, 604 exercises):** NEW `37-injection-and-eval` (listed after 12: injection, `find_injection`, `wrap_untrusted`, `run_eval`, `compare_prompts`) and NEW `38-multimodal-awareness` (listed after 17, W3 Saturday: `image_message`, `data_url`, `describe_image`). New 4th chained exercise in 12 (`manage-memory`), 14 (`nearest-text`), 15 (`search-threshold`), 16 (`chunk-document`), 17 (`index-and-search`), each with given code from earlier exercises, plus worked-pattern and Try-it-live sections in those lessons. 14-17 text still from the old version (already beginner-friendly), not full rewrites. Vision/Whisper details from memory, not verified. Track order note: 13 (L2 drill) now sits after 12 and 37; W2 Saturday vs W3 order needs fixing in roadmap.yaml.
- **W4 + W5 built (2026-11-23), validator green (122 lessons, 834 quiz, 643 exercises):** L4 is now written and listed as 21, 22, 23, 39, 40, 24, 25, 41, 42, 26. NEW lessons: `21-rag-pipeline` (hits, format_context, build_rag_messages, answer), `22-grounded-citations` (extract/check citations, cited_answer with repair), `23-rerank-rewrite` (rerank, rewrite_question, multi_query, retrieve_multi with RRF), `39-rag-ingestion` (clean_text, content_hash, plan_sync, apply_sync), `40-rag-access-freshness` (allowed, filter_hits, drop_stale, search_for_user), `24-rag-failures` (classify_failure, failure_report, dedupe_hits, prepare_context), `25-evaluation` (recall/precision/MRR, evaluate_retrieval), `41-llm-judge-golden` (judge messages, parse_verdict, judge, run_golden), `42-rag-awareness` (contextualize, expand_to_parents, choose_source), `26-l4-interview` (drills `fit_hits`, `uncited_sentences`, `ndcg_at_k`). 18-hybrid-search got a 4th exercise `hybrid-search`. `reference/genai-retrieval.md` extended. L4 project steps are done (see next entry). Not done: W5 Saturday order vs roadmap.yaml (not updated), live Groq/Chroma checks.
- **L5 + L4 project steps built (2026-11-23), validator green (127 lessons, 873 quiz, 662 exercises, 33 project steps):** L5 lessons written: `27-agent-loop` (message_to_dict, agent_step, run_agent, run_agent_safe with loop guard), `28-fastapi-serving-sse` (format_sse, chunk_text, sse_events, sse_safe; the FastAPI example was run with TestClient), `29-cache-cost-observability` (cache_key, cached_call, allow_request sliding window, summarize_calls with p95), `30-guardrails` (check_input, redact_pii, allow_tool_call, guarded_answer; defence in depth, lethal trifecta), `31-l5-interview` (drills `parse_react`, `trim_messages`, `input_per_step`/`agent_input_cost`). `reference/genai-groq.md` got four L5 sections. DevDocs Copilot steps 12-19 added: 12 `rag.py` + `rag_cli.py` (also optional `temperature`/`max_completion_tokens` in `complete_with_retry`), 13 `citations.py`, 14 `rewrite.py` (rerank, rewrite, multi-query, `answer_with_history`; the CLI becomes a chat), 15 `sync.py` (clean_text, content_hash, plan_sync, manifest, `sync_folder`, `docs_cli sync`), 16 `access.py` + `access_cli.py` (deny by default; `cited_answer(hits=...)`), 17 `context.py` + `failures.py`, 18 `evals.py` + `eval_cli.py` (golden set, three retrievers compared), 19 `judge.py` (LLM judge, `evaluate_answers` labels every failure). All use fake clients and a fake embedder. No new dependency. Chunk ids hold a position (`tasks.md:2`), so golden sets break when docs are re-chunked (said in step 18). Not done: Copilot steps for the agent loop and serving (lessons 27-29 have no project step), Try-it-live never run with a real key.
- **W6 built (2026-11-23), validator green (132 lessons, 908 quiz, 681 exercises):** NEW track `content/agentic/` (in `TRACK_ORDER`, label "Agentic AI" in `app/routers/roadmap.py`, no project yet). Level A1 "Agents without a framework": `01-workflow-vs-agent` (chain_success, choose_approach, pick_by_numbers, start_simple), `02-tool-design` (check_tool_spec, validate_args, truncate_result, safe_tool_call), `03-workflow-patterns` (run_chain, route, orchestrate, improve_loop; `ask` helper given, scripted fake client), `04-react-plan-reflect` (parse_plan, build_step_messages, execute_plan, react_agent with given parse_react from genai 31), `05-failure-modes-frameworks` (detect_failure, check_budget, check_tool_path; framework table from memory, tells learner to check docs). Study order for W6: agentic 01, genai 27 (agent loop), agentic 02-05; Saturday = agentic 05. Prerequisite: Python L1, GenAI L1-L2, genai 27. `reference/genai-groq.md` got an "Agentic patterns" section. `roadmap.yaml` not updated (roadmap-fix session).
- Next: W7-W9 agentic (LangChain, LangGraph, memory, multi-agent, MCP, agent eval/tracing, capstone, mock interviews; extend the `agentic` track with levels A2+), fine-tuning and quantization awareness, full zero-knowledge rewrites of 07-11 and 14-17. `content/roadmap.yaml` is NOT yet updated for this plan.

### Site updates and 4-month roadmap (original plan; landing page, roadmap and streak are built, see above)
Goal: Dev becomes a job-ready AI Engineer in 4 months, from 2026-11-22 to about 2027-03-22. Time: 2 to 2.5 hours on weekdays, lighter on weekends (about 300 hours in total). This is the understanding phase, so build only after the booklets are done and Dev says go. Topics and weight: heavy on Python, FastAPI, GenAI, Agentic AI and DSA. Interview level only for DevOps, System Design and Backend.

**What changes on the site (`frontend/` and `app/`):**
1. **Landing page** (new `frontend/app/page.tsx`). It shows the full daily schedule: what to read (booklet chapter) and what to practise (site lesson or exercise), for all topics.
2. **Fixed roadmap file** `content/roadmap.yaml`, one entry per day (topic, task, link to a booklet chapter or a site lesson or exercise).
3. **Backend endpoint** under `app/` for today's tasks, progress, streak and the overdue list. Use SQLite, the same pattern as the existing progress tracking.
4. **Hard mentor.** The schedule is fixed. Skipping days does NOT quietly shift the plan. Missed work stays visible as overdue. The mentor is an LLM (Haiku) called through the existing `claude-agent-sdk` path (no API key, local `claude` login), with a strict-mentor system prompt.
5. **Done-gate for a task:** quiz score above 75 percent, plus the code tests pass, plus a short AI round with Haiku.
6. **Streak** counter on the landing page.
7. **Content for new topics on the site** (quizzes and exercises): Backend, Agentic AI, DevOps, System Design. DSA stays on the site, up to medium.
8. **Not linked from the site:** the booklets (PDF only, for reading).

**Open points to decide with Dev before building:**
- Exact behaviour of the mentor when tasks are overdue (a stern message on open, a daily check-in chat, or hiding new tasks until old ones are done).
- Time budget per topic (300 hours is not enough for everything at full depth, so some topics get shallow).
- Which site lessons and exercises fill each day of the schedule, and where booklet reading replaces them.

**Order:** finish the booklets (FastAPI redesign, Backend, Agentic AI, DevOps, System Design), then write `roadmap.yaml`, then build the landing page, endpoint, streak, done-gate and mentor.

### Done
- **Python L1–L3 (lessons 01–35):** rewritten or newly written in the beginner-friendly style, validated.
- **FastAPI L1 (01–07) and L2 (08–16):** `lesson.md` rewritten only (exercises, quizzes and project steps untouched), validated.
- **FastAPI gap lessons** (added after an audit against a 1.5-year-experience interview). Each has `lesson.md`, `quiz.yaml` and 3 exercises, and no project step:
  - `25-pydantic-validation` (listed after 05): field/model validators, `computed_field`, `Literal` and discriminated unions.
  - `26-forms-files-cookies` (listed after 25): `Form`, `Cookie`, `Header`, `UploadFile` checks, response classes, `response_model_exclude_none`.
  - `28-db-patterns` (listed after 11): transactions, many-to-many, optimistic locking, soft delete, `IntegrityError` to 409.
  - `27-app-lifecycle-docs` (listed after 13): lifespan, `app.state`, `mount`, GZip, TrustedHost, OpenAPI metadata.
- `content/fastapi/track.yaml` order updated for the new lessons. `07-l1-interview` and `16-l2-interview` got new Q&A sections (lesson.md only).

- **GenAI Level 1 (lessons 01-06)** written: `01-ai-llm-basics`, `02-tokens-context`, `03-first-groq-call`, `04-messages-roles`, `05-parameters`, `06-streaming-errors-retry`. Each has lesson, quiz, 3 offline exercises. DevDocs Copilot steps 1-3 (lessons 03, 04, 06). `reference/genai-groq.md` added. All 31 GenAI lessons are listed in `content/genai/track.yaml` (L4-L5 are "coming soon").
- **GenAI Level 2 (lessons 07-13)** written: prompt patterns, prompt templates (project step 4), JSON output, Pydantic validation and retry (step 5), tool calling (step 6), chat memory (step 7), L2 interview (3 coding drills). `reference/genai-groq.md` extended.

- **GenAI Level 3 (lessons 14-20)** written: embeddings idea, cosine with numpy (project step 8: `embed.py`, `similarity.py`, `search.py`), chunking (step 9: `chunking.py`, `ingest.py`), Chroma (step 10: `store.py`, `docs_cli.py`), BM25 and hybrid search with RRF (step 11: `bm25.py`, `hybrid.py`), vector DB landscape (no step), L3 interview (3 coding drills). `reference/genai-retrieval.md` added.

### Left to do
- **GenAI L4-L5 (lessons 21-31):** write level by level, Dev reviews each level first. Plan is in the track.yaml order. L4 is RAG (pipeline, citations, rerank and rewrite, failure modes, evaluation).
- **FastAPI L3, lessons 17–24:** listed in `track.yaml`, folders do not exist yet. Write each with lesson, quiz (5–8), 2–4 exercises, and a TaskFlow project step from step 16 (solution built on `content/fastapi/15-testing/project/solution`):
  - 17 auth-concepts: password hashing, sessions vs JWT, cookies vs headers, authn vs authz
  - 18 oauth2-jwt: `OAuth2PasswordBearer`, login, `get_current_user`, refresh tokens, RBAC/scopes with `Security`, ownership checks
  - 19 background-work: `BackgroundTasks`, queue and worker (ARQ), retries, idempotent jobs
  - 20 caching: Redis, TTL, invalidation, stampede, ETag/Cache-Control
  - 21 streaming: `StreamingResponse`, SSE, WebSockets
  - 22 security: rate limiting, OWASP API issues, security headers, secrets
  - 23 docker-deploy: Dockerfile, gunicorn/uvicorn workers, compose, health vs readiness, CI, graceful shutdown
  - 24 l3-interview (`kind: interview`): Q&A plus a tools section for the coding exercises
- **`29-llm-backend-patterns`:** listed in `track.yaml` before 24, not written. LLM API calls with timeout/retry, streaming tokens, structured output with Pydantic, cost and rate limits, embeddings idea. No project step.
- Tests for L3 must stay offline (fake Redis, in-memory SQLite).

### Open items
- Dev has not yet reviewed: GenAI L1, L2 and L3 (never tried with a real Groq key either; the real `fastembed` model download and a real Chroma index over real docs were not run, only fake-embedder tests), Python L2/L3, FastAPI L1/L2, and the new gap lessons 25–28. Dev reviews each level before the next starts.
- Dev has not yet reviewed the GenAI booklet (`booklets/_build/genai.pdf`).
- The app was never run to look at the rendered lessons (`./dev.sh`).
- `plan_ids` are unchecked, because the source plan `~/Downloads/ai-engineer-learning-plan.md` is missing.
- No `reference/` entries yet for the new Python L3 lessons or the new FastAPI gap lessons.
