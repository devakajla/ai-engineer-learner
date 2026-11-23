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

_VERDICT_RE = re.compile(r"VERDICT:\s*(CORRECT|PARTIAL|INCORRECT)")


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
) -> AsyncIterator[str | StreamDone]:
    """`images` is a list of (media_type, base64 data) screenshots attached to this message."""
    system = TUTOR_RULES + "\n" + lesson_context(lesson)
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


def parse_verdict(text: str) -> str | None:
    m = _VERDICT_RE.search(text[:200])
    return m.group(1) if m else None
