"""Claude integration over claude-agent-sdk, which drives the locally installed `claude`
CLI and uses its login (no API key).

Claude runs with every tool disabled and in an empty workspace, so it can only talk.
"""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from dataclasses import dataclass

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, StreamEvent, TextBlock, query

from app.config import CLAUDE_CWD, project_name
from app.content import Exercise, Lesson
from app.services.runner import RunResult

TUTOR_RULES = """\
You are a patient programming tutor inside Dev's personal learning app.
Dev is a Python backend developer (~1.5 years) preparing for AI Engineer interviews.
Rules:
- Use simple, clear English. Short paragraphs, small code examples, Markdown formatting.
- Explain the "why", not only the "how". Mention common interview follow-ups when useful.
- When Dev is stuck on an exercise, guide with hints and questions first.
  Only give a full solution if Dev explicitly asks for it.
- If a question is outside the current lesson, still answer it, briefly.
"""

REVIEW_RULES = """\
You are a strict but friendly code reviewer for a learning app. You review a learner's
solution to a coding exercise. You can see the exercise, the learner's code and the result
of the hidden tests.

Your FIRST line must be exactly one of:
VERDICT: CORRECT
VERDICT: PARTIAL
VERDICT: INCORRECT

CORRECT = tests pass and the code solves the task properly (not hard-coded for the tests).
PARTIAL = works but has a real problem (edge case, wrong complexity, misuse of the concept).
INCORRECT = tests fail or the approach is wrong.

Then write short Markdown sections:
### What's good
### Problems
(bugs, missed edge cases, style issues. Skip the section if there are none.)
### Hints
(if not CORRECT: nudge towards the fix with hints, do NOT write the full corrected solution)
### Complexity
(time and space, one line each, when it matters)
### Interview tip
(one follow-up question an interviewer could ask about this code)

Keep it under 250 words. Simple English.
"""

PROJECT_REVIEW_RULES = """\
You are a senior backend engineer mentoring a learner who is building a FastAPI project
step by step. You see the step's instructions, the result of the hidden checkpoint tests,
and a snapshot of the learner's project (folder tree + source files).

Your FIRST line must be exactly one of:
VERDICT: CORRECT
VERDICT: PARTIAL
VERDICT: INCORRECT

CORRECT = checkpoint tests pass and the step is done in a clean, professional way.
PARTIAL = tests pass but there are real best-practice problems worth fixing now.
INCORRECT = tests fail or the step's requirements are not met.

Then short Markdown sections:
### What's good
### Fix before moving on
(concrete problems with file paths: wrong layer, logic in routes, hard-coded config,
missing type hints, bad naming, secrets in code, missing .gitignore entries, etc.
Skip the section if there are none.)
### Best-practice tip
(one habit that real production FastAPI codebases follow, relevant to this step)
### Interview angle
(one question an interviewer could ask about this design)

Judge only what this step and earlier steps require; do not demand features from later
lessons. Give hints, not full rewrites. Under 300 words. Simple English.
"""

NOTES_RULES = """\
You write revision notes for Dev, a Python backend developer preparing for AI Engineer
interviews. Dev will re-read the note later to refresh the lesson and to remember what
was confusing. You see the lesson, Dev's current note (may be empty), the new chat with
the tutor, Dev's starred doubts and the quiz questions Dev got wrong.

Output ONLY the full updated note in Markdown, with no preamble and no closing remarks.
Use exactly these sections, as `###` headings, in this order:

### Big idea
2-3 short lines: what this lesson is about and why it matters.

### Code recap
The key runnable snippets of the whole lesson, each in a fenced code block with the output
as a comment (`# -> 42`), and a one-line "why" under it. Only use concepts from this
lesson. Keep each snippet small.

### Confusions cleared
One item per confusion Dev had (from the chat, doubts and wrong quiz answers), as
**Q: ...** then "I thought ... / Actually ..." and a tiny example when it helps.

### Remember
3-5 bullets: gotchas, rules of thumb, one likely interview question.

Rules:
- Simple English. Short sentences. Be concrete, no filler.
- If a current note exists, treat it as the base (Dev may have edited it by hand). Keep Dev's
  own wording and every earlier confusion. Add the new confusions to the right section,
  merge duplicates, fix mistakes only if they are wrong.
- Only add a confusion if it really came from the chat, doubts or quiz. Never invent any.
  If there are none, write "No confusions yet." under that section.
- Do not copy whole paragraphs of the lesson. Notes should be much shorter than the lesson.
"""

GUIDE_RULES = """You are Dev's plan guide and strict mentor. Dev follows a fixed daily plan to become a job-ready
AI Engineer. The plan never moves. You get the current plan state. Reply in exactly this Markdown shape, in
simple English, at most 110 words in total:

**Now:** one sentence naming the exact task to do first and how long it takes.
**How:** 2 or 3 short bullets on how to go through it, using the steps you were given (read, quiz, exercises).
Skip steps that are already passed (the state shows it). Say what to do when stuck: ask the chat panel, star a doubt, never skip the exercise.
**Watch:** one sentence. If tasks are overdue, say how many and the oldest date, and be firm. Otherwise give one
short tip or name the next big thing coming up.

Be firm and fair, not cruel. No emoji, no greeting, no fake praise. Use only the facts given. Never invent
lesson content."""

ASK_RULES = """You are Dev's plan guide. Dev follows a fixed daily plan to become a job-ready AI Engineer. You get the
current plan state, then Dev's question. Answer in simple English in at most 80 words. Be direct and practical.
The plan cannot be moved; if Dev asks to skip or move work, say no and give the fastest way to catch up.
Use only the facts given. If the question is about a concept, give a one-line answer and say which lesson covers it
if you can tell from the plan."""

COACH_RULES = """You are Dev's Python coach in a trial room. Dev is a beginner who can think of the solution but
cannot turn it into Python code. You get Dev's code, the output of its last run, and a hint level (1 to 3).
Dev marks the problem in a comment that starts with `# PROBLEM:` (the comment lines right after it belong to it).
If there is no such comment, work from the error in the last output.

YOUR WHOLE REPLY IS PYTHON COMMENT LINES. Every line starts with `# `. NEVER write a line of code that solves
the problem or fixes Dev's code. Dev must type the code. Do not rewrite Dev's lines in corrected form.

Write, in this order:
1. `# IDEA:` one or two lines: what the problem means in plain everyday words.
2. `# WHAT IS WRONG:` only if Dev's code already has a mistake: say which line and why, in words. Do not give the fix line.
3. `# STEP 1:`, `# STEP 2:` ... a short plan. Each step says what to do and names the Python tool for it
   (for example: dictionary lookup, `.items()`, a variable that remembers the best so far).
4. A last line `TOPIC: <lesson-slug> | <short detail>` (this one line is not a comment, it is for the app). Pick the
   slug from <topic_list>, the lesson whose idea Dev is missing. Example: `TOPIC: 11-dicts | loop over inner dict`.
   If nothing fits, use `other`.

Hint level:
- 1: plan in words. End the plan with one question Dev should answer to himself.
- 2: also give the exact tool or method name for each step and a tiny example of that tool on DIFFERENT data
  than Dev's problem, as a comment (for example `# scores = {"a": 3}` then `# for k, v in scores.items(): ...`).
- 3: make each step more detailed (what goes in, what comes out, what to check), still no solution line.

Simple English, short sentences, at most 80 characters per line, at most 25 lines. No Markdown, no emoji.

<weak_spots> lists what Dev keeps getting wrong (most important first). On those topics use simpler words and one
extra small step. Mention an earlier mistake only when it helps this problem. Never print the list itself."""

EXERCISE_COACH_RULES = """You are Dev's Python coach on an exercise page. Dev is a beginner who understands the lesson
but gets stuck turning the idea into Python. You get the exercise text, Dev's code, the output of the last test run,
a hint level (1 to 3) and the reference solution.

The reference solution is ONLY for you, so your hints are correct. NEVER write it, never write any line of it, never
rewrite Dev's code in corrected form. Dev must type the code. Functions marked "given" in the starter are already
written: tell Dev to call them, do not explain how to write them.

YOUR WHOLE REPLY IS PYTHON COMMENT LINES. Every line starts with `# `. Write, in this order:
1. `# IDEA:` one or two lines: what the function must do, in plain everyday words.
2. `# WHAT IS WRONG:` only if Dev's code or the test output shows a mistake: say which line and why, in words.
   Read the failing test message and say what it means in plain words.
3. `# STEP 1:`, `# STEP 2:` ... a short plan. Each step says what to do and names the Python tool for it.
4. A last line `TOPIC: <lesson-slug> | <short detail>` (not a comment, it is for the app). Pick the slug from
   <topic_list>: the Python lesson whose idea Dev is missing. If Dev's gap is not a Python idea, use `none`.

Hint level:
- 1: plan in words. End with one question Dev should answer to himself.
- 2: also give the exact tool or method name for each step and a tiny example of that tool on DIFFERENT data,
  as a comment (for example `# scores = {"a": 3}` then `# scores["a"]  # -> 3`).
- 3: make each step more detailed (what goes in, what comes out, what to check), still no solution line.

Simple English, short sentences, at most 80 characters per line, at most 25 lines. No Markdown, no emoji.
<weak_spots> lists what Dev keeps getting wrong. On those topics use simpler words and one extra small step."""

WALKTHROUGH_RULES = """You are Dev's Python tutor. Dev tried this exercise several times and used every hint, and is
still stuck. Give a step-by-step walkthrough that gets Dev to write the code himself. You get the exercise text,
Dev's code, the last test output and the reference solution (ONLY for you, so the walkthrough is correct).

Rules:
- NEVER show the reference solution or any line of it, and never rewrite Dev's code in corrected form.
- Write Markdown. Start with `## The idea` (2-3 short sentences, everyday words).
- Then `## Steps`: numbered steps, one small thing each. For every step write:
  - what to do, in plain words;
  - the shape in English pseudo-code (for example: "make an empty list called pieces");
  - the Python tool shown on DIFFERENT data in a ```python block of at most 4 lines, with output as `# ->`.
- Then `## Your mistake` (only if Dev's code has one): which line, why it is wrong, in words.
- Then `## Check yourself`: 2 small questions Dev answers before running the tests.
- Functions marked "given" in the starter are already written: just say to call them.
- Simple English, short sentences. At most 450 words.
- End with one line `TOPIC: <lesson-slug> | <short detail>` (from <topic_list>, the Python idea Dev is missing,
  or `none`)."""

TRIAL_CHAT_RULES = """You are Dev's Python tutor in a trial room. Dev is a beginner who can think of a solution but
has trouble writing it in Python. Dev asks you questions. You also get Dev's current code, the output of its last run
and the earlier messages of this chat.

- Answer the question that was asked, in simple English, short sentences. Plain everyday meaning first, then a small example.
- Examples use DIFFERENT data than Dev's problem and are at most 6 lines, in a ```python block with the output as `# ->`.
- Do NOT write the solution to Dev's own problem and do NOT rewrite Dev's code in corrected form. You may say which
  line is wrong and why, and name the tool to use. If Dev asks for the full answer, say no kindly and explain the idea
  in words; the Coach me button gives a step plan.
- Use only what a beginner knows (Python basics). If you need something harder, explain it in one line first.
- At most 150 words unless Dev asks for more. No emoji, no greeting.
- <weak_spots> lists what Dev keeps getting wrong. On those topics use simpler words and connect to the earlier
  mistake only when it helps. Never print the list itself.
- Last line, always: if the question shows Dev is missing a Python idea, write `TOPIC: <lesson-slug> | <short detail>`
  with the slug from <topic_list> (example: `TOPIC: 06-conditionals | not in vs not`). If it is only a curious or
  already-understood question, write `TOPIC: none`. This line is for the app, not for Dev."""

DRILL_RULES = """You write practice drills for Dev, a beginner who has read only a little Python. You get the text of the
lesson Dev is weak on, the exact weak details, and what Dev keeps getting wrong. Reply with ONLY a JSON array of 4
drills, easy to hard, nothing else. Each drill is an object with these keys:
- "title": 2 to 5 words.
- "prompt": Markdown, simple English. Say what the function takes and returns, the rules, and 2 examples with
  results as `# ->`. Do not give the solution steps.
- "function_name": the function Dev writes.
- "starter": the `def` line with a one-line docstring and `pass` as the body. Never any solution lines.
- "solution": a correct, simple reference solution (never shown to Dev).
- "calls": 3 to 5 distinct expressions that call the function, each a different case (include one edge case such as
  empty input). Deterministic only: no input(), files, network, random or time.

Rules: use ONLY Python taught in the given lesson or earlier lessons (no lambda, classes or comprehensions unless the
lesson teaches them). Drill 1 is tiny and targets the weak detail directly. Each next drill adds one small twist.
Do not copy a problem from the lesson text. Return values must be plain (numbers, strings, bools, None, lists,
dicts, tuples) so they print the same every time."""

_VERDICT_RE = re.compile(r"VERDICT:\s*(CORRECT|PARTIAL|INCORRECT)")
_TOPIC_RE = re.compile(r"^\s*TOPIC:\s*(.+?)\s*$", re.MULTILINE)


@dataclass
class AISettings:
    """The model and effort picked in the UI for one use (see app/routers/settings.py)."""

    model: str
    effort: str


def _options(system_prompt: str, ai: AISettings, resume: str | None = None) -> ClaudeAgentOptions:
    CLAUDE_CWD.mkdir(parents=True, exist_ok=True)
    return ClaudeAgentOptions(
        system_prompt=system_prompt,
        tools=[],  # no built-in tools at all
        max_turns=1,
        cwd=str(CLAUDE_CWD),
        include_partial_messages=True,
        setting_sources=[],
        # Keep the claude.ai connectors (Gmail, Drive, ...) out: when they load, a short
        # review grows from ~1.5k to ~60k input tokens.
        extra_args={"strict-mcp-config": None},
        env={"ENABLE_CLAUDEAI_MCP_SERVERS": "false"},
        resume=resume,
        model=ai.model,
        effort=ai.effort,
    )


@dataclass
class StreamDone:
    """Yielded last by `_stream`: the full text and the session id to resume later."""

    text: str
    session_id: str | None


async def _stream(prompt: str | AsyncIterator[dict], options: ClaudeAgentOptions) -> AsyncIterator[str | StreamDone]:
    parts: list[str] = []
    final_text: str | None = None
    session_id = None
    streamed = False
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, StreamEvent):
            event = msg.event
            if event.get("type") == "content_block_delta" and event["delta"].get("type") == "text_delta":
                chunk = event["delta"]["text"]
                streamed = True
                parts.append(chunk)
                yield chunk
        elif isinstance(msg, AssistantMessage) and not streamed:
            # Fallback if partial messages are not delivered.
            for block in msg.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
                    yield block.text
        elif isinstance(msg, ResultMessage):
            session_id = msg.session_id
            if msg.is_error:
                final_text = "".join(parts) or f"Claude returned an error: {msg.result or msg.subtype}"
                if not parts:
                    yield final_text
    yield StreamDone(text=final_text or "".join(parts), session_id=session_id)


def lesson_context(lesson: Lesson) -> str:
    plan = f" (plan topics: {', '.join(lesson.plan_ids)})" if lesson.plan_ids else ""
    ex = "\n".join(f"- {e.title}" for e in lesson.exercises) or "- none"
    project = (
        f"Project step in this lesson (Dev builds the {project_name(lesson.ref.track)} project in their own folder):\n"
        f"{lesson.project.title}\n{lesson.project.instructions[:4000]}\n\n"
        if lesson.project
        else ""
    )
    return (
        f"Current lesson: {lesson.ref.track} / {lesson.title}{plan}\n"
        f"Summary: {lesson.summary}\n"
        f"Exercises in this lesson:\n{ex}\n\n"
        f"{project}"
        f"Lesson text (for reference):\n<lesson>\n{lesson.body[:12000]}\n</lesson>"
    )


async def _with_images(message: str, images: list[tuple[str, str]]) -> AsyncIterator[dict]:
    """One user turn with text plus screenshots, in the SDK's streaming-input format."""
    content: list[dict] = [
        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}
        for media_type, data in images
    ]
    content.append({"type": "text", "text": message})
    yield {
        "type": "user",
        "message": {"role": "user", "content": content},
        "parent_tool_use_id": None,
        "session_id": "default",
    }


async def chat_stream(
    lesson: Lesson,
    message: str,
    session_id: str | None,
    ai: AISettings,
    images: list[tuple[str, str]] | None = None,
    profile: str = "",
) -> AsyncIterator[str | StreamDone]:
    """`images` is a list of (media_type, base64 data) screenshots attached to this message."""
    system = TUTOR_RULES + "\n" + lesson_context(lesson)
    if profile:
        system += (
            "\n\nWhat Dev keeps getting wrong (most important first). On these topics use simpler words and "
            "connect to the earlier mistake only when it helps. Never print this list:\n" + profile
        )
    prompt = _with_images(message, images) if images else message
    async for item in _stream(prompt, _options(system, ai, resume=session_id)):
        yield item


async def review_stream(
    lesson: Lesson, exercise: Exercise, code: str, result: RunResult, ai: AISettings
) -> AsyncIterator[str | StreamDone]:
    prompt = (
        f"Lesson: {lesson.title}\n\n"
        f"<exercise>\n# {exercise.title}\n\n{exercise.prompt}\n</exercise>\n\n"
        f"<learner_code>\n{code}\n</learner_code>\n\n"
        f"<hidden_tests passed=\"{result.passed}\">\n{result.summary}\n{result.output[-4000:]}\n</hidden_tests>"
    )
    async for item in _stream(prompt, _options(REVIEW_RULES, ai)):
        yield item


async def project_review_stream(
    lesson: Lesson, result: RunResult, snapshot: str, ai: AISettings
) -> AsyncIterator[str | StreamDone]:
    step = lesson.project
    prompt = (
        f"Lesson: {lesson.title}\n\n"
        f"<step title=\"{step.title if step else ''}\">\n{step.instructions if step else ''}\n</step>\n\n"
        f"<checkpoint_tests passed=\"{result.passed}\">\n{result.output[-4000:]}\n</checkpoint_tests>\n\n"
        f"<project>\n{snapshot}\n</project>"
    )
    async for item in _stream(prompt, _options(PROJECT_REVIEW_RULES, ai)):
        yield item


async def notes_stream(
    lesson: Lesson,
    old_note: str,
    new_chat: list[tuple[str, str]],
    doubts: list[str],
    wrong_quiz: list[str],
    ai: AISettings,
) -> AsyncIterator[str | StreamDone]:
    chat = "\n\n".join(f"{'Dev' if role == 'user' else 'Tutor'}: {text}" for role, text in new_chat)
    # Keep the newest part if the chat is very long.
    chat = chat[-20000:] or "(no new chat)"
    prompt = (
        f"{lesson_context(lesson)}\n\n"
        f"<current_note>\n{old_note or '(empty)'}\n</current_note>\n\n"
        f"<new_chat>\n{chat}\n</new_chat>\n\n"
        f"<starred_doubts>\n{chr(10).join(f'- {d}' for d in doubts) or '(none)'}\n</starred_doubts>\n\n"
        f"<wrong_quiz_answers>\n{chr(10).join(f'- {w}' for w in wrong_quiz) or '(none)'}\n</wrong_quiz_answers>"
    )
    async for item in _stream(prompt, _options(NOTES_RULES, ai)):
        yield item


async def guide_stream(prompt: str, ai: AISettings, rules: str = GUIDE_RULES) -> AsyncIterator[str | StreamDone]:
    async for item in _stream(prompt, _options(rules, ai)):
        yield item


def _weak_block(profile: str, tags: str) -> str:
    return (
        f"<topic_list>\n{tags or '(none)'}\n</topic_list>\n\n"
        f"<weak_spots>\n{profile or '(nothing known yet)'}\n</weak_spots>\n\n"
    )


async def coach_stream(
    code: str, output: str, attempt: int, ai: AISettings, profile: str = "", tags: str = ""
) -> AsyncIterator[str | StreamDone]:
    prompt = (
        f"{_weak_block(profile, tags)}"
        f"<hint_level>{max(1, min(attempt, 3))}</hint_level>\n\n"
        f"<dev_code>\n{code[:20000]}\n</dev_code>\n\n"
        f"<last_run_output>\n{output[-3000:] or '(not run yet)'}\n</last_run_output>"
    )
    async for item in _stream(prompt, _options(COACH_RULES, ai)):
        yield item


def _exercise_block(exercise_prompt: str, starter: str, solution: str, code: str, output: str) -> str:
    return (
        f"<exercise>\n{exercise_prompt[:6000]}\n</exercise>\n\n"
        f"<starter>\n{starter[:6000]}\n</starter>\n\n"
        f"<reference_solution_for_you_only>\n{solution[:8000]}\n</reference_solution_for_you_only>\n\n"
        f"<dev_code>\n{code[:20000] or '(empty)'}\n</dev_code>\n\n"
        f"<last_test_output>\n{output[-3000:] or '(not run yet)'}\n</last_test_output>"
    )


async def exercise_coach_stream(
    exercise_prompt: str, starter: str, solution: str, code: str, output: str, level: int,
    ai: AISettings, profile: str = "", tags: str = "",
) -> AsyncIterator[str | StreamDone]:
    """Comment-only hint for one exercise in the Practice tab (level 1-3)."""
    prompt = (
        f"{_weak_block(profile, tags)}<hint_level>{max(1, min(level, 3))}</hint_level>\n\n"
        + _exercise_block(exercise_prompt, starter, solution, code, output)
    )
    async for item in _stream(prompt, _options(EXERCISE_COACH_RULES, ai)):
        yield item


async def walkthrough_stream(
    exercise_prompt: str, starter: str, solution: str, code: str, output: str,
    ai: AISettings, profile: str = "", tags: str = "",
) -> AsyncIterator[str | StreamDone]:
    """Step-by-step walkthrough (no solution code) once Dev is really stuck on an exercise."""
    prompt = _weak_block(profile, tags) + _exercise_block(exercise_prompt, starter, solution, code, output)
    async for item in _stream(prompt, _options(WALKTHROUGH_RULES, ai)):
        yield item


async def trial_chat_stream(
    message: str,
    code: str,
    output: str,
    history: list[tuple[str, str]],
    ai: AISettings,
    profile: str = "",
    tags: str = "",
) -> AsyncIterator[str | StreamDone]:
    """Free questions in the trial room. Stateless: the earlier turns come from the browser."""
    earlier = "\n\n".join(f"{'Dev' if role == 'user' else 'Tutor'}: {text}" for role, text in history[-10:])
    prompt = (
        f"{_weak_block(profile, tags)}"
        f"<dev_code>\n{code[:20000]}\n</dev_code>\n\n"
        f"<last_run_output>\n{output[-3000:] or '(not run yet)'}\n</last_run_output>\n\n"
        f"<earlier_chat>\n{earlier[-8000:] or '(none)'}\n</earlier_chat>\n\n"
        f"<question>\n{message}\n</question>"
    )
    async for item in _stream(prompt, _options(TRIAL_CHAT_RULES, ai)):
        yield item


async def generate_drills(lesson: Lesson, details: list[str], profile: str, ai: AISettings) -> str:
    """One non-streamed call. Returns Claude's reply (a JSON array of drills, see app/services/drills.py)."""
    prompt = (
        f"<lesson title=\"{lesson.title}\">\n{lesson.body[:6000]}\n</lesson>\n\n"
        f"<weak_details>\n{chr(10).join(f'- {d}' for d in details) or '- (none given: cover the core idea of the lesson)'}\n</weak_details>\n\n"
        f"<weak_spots>\n{profile or '(nothing known yet)'}\n</weak_spots>"
    )
    text = ""
    async for item in _stream(prompt, _options(DRILL_RULES, ai)):
        if isinstance(item, StreamDone):
            text = item.text
    return text


def parse_topic(text: str, valid_tags: dict[str, str] | None = None) -> tuple[str, str] | None:
    """`TOPIC: 11-dicts | loop over inner dict` -> ("11-dicts", "loop over inner dict"). None for `TOPIC: none`.

    A slug that is not in `valid_tags` (or a lesson title) becomes "other" and keeps the text as the detail.
    """
    matches = _TOPIC_RE.findall(text)
    if not matches:
        return None
    raw = matches[-1].strip().strip("`")
    if raw.lower() in {"none", "n/a", ""}:
        return None
    tag, _, detail = raw.partition("|")
    tag, detail = tag.strip().lower(), detail.strip()[:80]
    tags = valid_tags or {}
    if tag in tags:
        return tag, detail
    by_title = {t.lower(): slug for slug, t in tags.items()}
    if tag in by_title:
        return by_title[tag], detail
    return "other", raw[:80]


def parse_verdict(text: str) -> str | None:
    m = _VERDICT_RE.search(text[:200])
    return m.group(1) if m else None
