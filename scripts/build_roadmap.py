"""Builds content/roadmap.yaml: the fixed day-by-day study plan (site lessons only, no booklets).

Run:  uv run python scripts/build_roadmap.py [preview.yaml]   (without an argument it writes content/roadmap.yaml)
Edit WEEKS below and run again. Run it again after you write new lessons, so the plan
picks up their real quiz and exercise counts. The output is committed: the plan stays fixed
until you regenerate it on purpose.

Three streams, 120 days (Mon 23 Nov 2026 to Mon 22 Mar 2027), Sunday off:
- GenAI + Agentic AI: 9 weeks of site lessons (WEEKS), then 2 weeks of buffer and revision (W10, W11).
- DSA phase 1 (days 1-75, to Fri 5 Feb): Mon-Sat about 5 exercises a day, Easy + Medium only, hard ones wait.
- DSA phase 2 (days 76-120): redo from memory, no hints: L4 mediums, L3 pattern mediums, basics, then a mixed set.
  Redo tasks are `review` tasks (tick by hand), because the exercises already pass.
- From week 10, a 30-minute GenAI + Agentic revision task every study day.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.content import get_lesson, get_tracks  # noqa: E402

START = FIRST_MONDAY = date(2026, 11, 23)  # day 1
PHASE1_END = date(2027, 2, 5)  # day 75, a Friday
PHASE2_START = date(2027, 2, 6)  # day 76, a Saturday
END = date(2027, 3, 22)  # day 120, a Monday

# Minutes for lessons that are listed but not written yet (default 90). Written lessons are measured.
UNWRITTEN_MINUTES = {
    ("agentic", "18-capstone-agent"): 120,
    ("agentic", "19-mock-interview-concepts"): 60,
    ("agentic", "20-mock-interview-design"): 60,
}

# Weeks 1-9, Mon-Sat. Each day is a list of (track, lesson number). Sunday is off.
# genai numbers: 01-06 and 32-36 level 1, 07-13 and 36-37 level 2, 14-20 and 38 level 3,
# 21-26 and 39-42 level 4, 27-31 and 43-44 level 5. agentic: 01-05 level A1, 06-10 A2, 11-15 A3, 16-20 A4.
WEEKS = [
    # W1: LLM from zero
    [[("genai", 1)], [("genai", 2)], [("genai", 32), ("genai", 3)], [("genai", 4)], [("genai", 5)], [("genai", 33)]],
    # W2: robust API calls, prompting, structured output, tools. Sat: L1 + L2 projects and drill
    [[("genai", 6), ("genai", 34)], [("genai", 35), ("genai", 7)], [("genai", 8), ("genai", 9)],
     [("genai", 10)], [("genai", 11)], [("genai", 36), ("genai", 13)]],
    # W3: memory, injection, embeddings, chunking, Chroma
    [[("genai", 12)], [("genai", 37)], [("genai", 14)], [("genai", 15)], [("genai", 16)], [("genai", 17)]],
    # W4: search and RAG core. Mon also has the multimodal awareness lesson. Sat: L3 drill
    [[("genai", 38), ("genai", 19)], [("genai", 18)], [("genai", 21)], [("genai", 22)], [("genai", 23)], [("genai", 20)]],
    # W5: RAG in production and evaluation. Sat: RAG awareness + L4 drill
    [[("genai", 39)], [("genai", 40)], [("genai", 24)], [("genai", 25)], [("genai", 41)],
     [("genai", 42), ("genai", 26)]],
    # W6: agents without a framework. Sat: failure modes and frameworks
    [[("agentic", 1)], [("genai", 27)], [("agentic", 2)], [("agentic", 3)], [("agentic", 4)], [("agentic", 5)]],
    # W7: LangChain and LangGraph. Sat: fine-tuning awareness
    [[("agentic", 6)], [("agentic", 7)], [("agentic", 8)], [("agentic", 9)], [("agentic", 10)], [("genai", 43)]],
    # W8: advanced agents and safety. Sat: quantization and local models
    [[("agentic", 11)], [("agentic", 12)], [("agentic", 13), ("genai", 30)], [("agentic", 14)], [("agentic", 15)],
     [("genai", 44)]],
    # W9: production, capstone, interview. Sat: mock interview 2
    [[("agentic", 16)], [("genai", 28)], [("genai", 29)], [("agentic", 17), ("agentic", 18)],
     [("agentic", 19), ("genai", 31)], [("agentic", 20)]],
]

# Week 10 (Mon 25 Jan - Sat 30 Jan): buffer and polish. 60 minutes a day beside DSA.
W10 = [
    ("Clear everything overdue", ["Open the home page and clear every overdue GenAI and Agentic task",
                                  "Retake any quiz where you scored under 90%"], []),
    ("Polish the capstone", ["Run the capstone tests and fix anything red",
                             "Write a README: what it does, how to run it, what you would improve"],
     [("agentic", 18)]),
    ("Revise GenAI levels 1 to 3", ["Redo the interview quizzes without notes (aim for 90%+)",
                                   "Say 3 interview answers out loud, then check them"],
     [("genai", 13), ("genai", 20)]),
    ("Revise GenAI levels 4 and 5", ["Redo the interview quizzes without notes (aim for 90%+)",
                                    "Explain the RAG pipeline and the agent loop out loud in 2 minutes each"],
     [("genai", 26), ("genai", 31)]),
    ("Revise Agentic AI", ["Redo the agentic quizzes without notes (aim for 90%+)",
                           "Draw a LangGraph graph for a support agent on paper"],
     [("agentic", 5), ("agentic", 10), ("agentic", 15), ("agentic", 16)]),
    ("Mock interview with Claude", ["Ask Claude in a chat to interview you for 45 minutes: GenAI and Agentic AI",
                                    "Write down every question you got wrong"], []),
]

# From week 11 on, one 30-minute revision task per study day, in this order, repeating.
ROTATION = [
    ("GenAI 1: tokens, context, parameters, retries", [("genai", 2), ("genai", 5), ("genai", 6)]),
    ("GenAI 2: prompts, JSON, Pydantic, tools, memory", [("genai", 7), ("genai", 9), ("genai", 11), ("genai", 13)]),
    ("GenAI 3: embeddings, chunking, hybrid search", [("genai", 14), ("genai", 16), ("genai", 18), ("genai", 20)]),
    ("GenAI 4: RAG pipeline, citations, rerank", [("genai", 21), ("genai", 22), ("genai", 23)]),
    ("RAG in production and evaluation", [("genai", 25), ("genai", 39), ("genai", 41), ("genai", 26)]),
    ("GenAI 5: agent loop, serving, cost, guardrails", [("genai", 27), ("genai", 28), ("genai", 29), ("genai", 30)]),
    ("Agentic 1: workflow vs agent, tools, patterns", [("agentic", 1), ("agentic", 2), ("agentic", 3), ("agentic", 4)]),
    ("LangChain and LangGraph", [("agentic", 6), ("agentic", 8), ("agentic", 9), ("agentic", 10)]),
    ("Memory, multi-agent and MCP", [("agentic", 11), ("agentic", 13), ("agentic", 14)]),
    ("Agent safety, eval and tracing", [("agentic", 15), ("agentic", 16)]),
    ("LLM system design: say one design out loud", [("agentic", 17), ("genai", 29)]),
    ("Capstone and mock interview questions", [("agentic", 18), ("agentic", 19), ("agentic", 20)]),
]
ROTATION_STEPS = [
    "Redo the quizzes of these lessons without notes (aim for 90%+)",
    "Say 3 interview answers out loud, then check them",
]

# DSA phase 2 blocks: (title, first day, last day, lesson numbers, exercises a day, minutes per exercise).
PHASE2_BLOCKS = [
    ("Core structures, medium problems", date(2027, 2, 6), date(2027, 2, 20), range(23, 30), 3, 25),
    ("Pattern foundations, medium problems", date(2027, 2, 22), date(2027, 3, 6), range(14, 22), 3, 25),
    ("Basics: loops, strings, lists, sets, dicts", date(2027, 3, 8), date(2027, 3, 13), range(3, 13), 5, 10),
]
MIXED_DAYS = (date(2027, 3, 15), date(2027, 3, 20))  # mixed medium set plus optional Hard problems


def days_between(a: date, b: date) -> list[date]:
    return [a + timedelta(days=i) for i in range((b - a).days + 1)]


def study_days(a: date, b: date) -> list[date]:
    """Mon-Sat only: Sunday is off."""
    return [d for d in days_between(a, b) if d.weekday() != 6]


def lesson_facts(track: str, slug: str) -> dict:
    """Real quiz and exercise counts for one site lesson (empty if the lesson is not written)."""
    lesson = get_lesson(track, slug)
    if not lesson:
        return {"written": False}
    return {
        "written": True,
        "words": len(lesson.body.split()),
        "quiz": len(lesson.quiz),
        "exercise_ids": [e.id for e in lesson.exercises],
        "project": lesson.project.title if lesson.project and lesson.project.test_file else None,
    }


def lesson_minutes(f: dict) -> int:
    minutes = f["words"] / 150 + f["quiz"] + 10 * len(f["exercise_ids"]) + (25 if f["project"] else 0)
    return int(round(minutes / 5) * 5)


def lesson_parts(ref) -> list[dict]:
    """A site lesson as one task, or two (read + quiz, then exercises) when it is long."""
    f = lesson_facts(ref.track, ref.slug)
    base = {"kind": "practise", "track": ref.track, "lesson": ref.slug, "title": ref.title}
    if not f["written"]:
        minutes = UNWRITTEN_MINUTES.get((ref.track, ref.slug), 90)
        return [{**base, "minutes": minutes, "planned": True,
                 "steps": ["This lesson is not written yet. It will be ready before this week starts."]}]
    read = max(5, round(f["words"] / 150))
    read_steps = [f"Read the lesson (about {read} min)"]
    quiz = {}
    if f["quiz"]:
        read_steps.append(f"Quiz: {f['quiz']} questions, pass with 75% or more")
        quiz = {"quiz": True}
    work_steps, work = [], {}
    if f["exercise_ids"]:
        work_steps.append(f"Exercises: {len(f['exercise_ids'])}, every test must pass")
        work["exercise_ids"] = f["exercise_ids"]
    if f["project"]:
        work_steps.append(f"Project step: {f['project']}")
        work["project"] = True
    read_min = int(round((read + f["quiz"]) / 5) * 5)
    work_min = 10 * len(f["exercise_ids"]) + (25 if f["project"] else 0)
    if read_min + work_min <= 110 or not work:
        return [{**base, "minutes": lesson_minutes(f), "steps": read_steps + work_steps, **quiz, **work}]
    return [
        {**base, "minutes": read_min, "part": [1, 2], "steps": read_steps, **quiz},
        {**base, "minutes": work_min, "part": [2, 2], "steps": work_steps, **work},
    ]


def load_difficulty() -> dict[tuple[str, str], tuple[str, str]]:
    """(lesson slug, exercise id) -> (title, E|M|H), from the DSA question sheet."""
    text = (ROOT / "content" / "dsa" / "QUESTIONS.md").read_text()
    out = {}
    for m in re.finditer(r"^\| \[.\] \| `dsa/([^/`]+)/([^`]+)` \| (.*?) \| ([EMH]) \|", text, re.M):
        out[(m[1], m[2])] = (m[3], m[4])
    return out


def pick(items: list, k: int) -> list:
    """k items spread evenly over the list (all of them when the list is short)."""
    if k >= len(items):
        return list(items)
    return [items[int((i + 0.5) * len(items) / k)] for i in range(k)]


def main() -> None:
    tracks = get_tracks()
    by_number = {tid: {int(r.slug.split("-")[0]): r for r in t.lessons} for tid, t in tracks.items()}
    plan: dict[date, list[dict]] = {d: [] for d in days_between(START, END)}
    kinds: dict[date, dict[str, int]] = defaultdict(lambda: defaultdict(int))  # day -> stream -> minutes

    def link(track: str, n: int) -> dict:
        ref = by_number[track][n]
        return {"track": track, "lesson": ref.slug, "title": ref.title}

    def add(day: date, stream: str, task: dict) -> None:
        plan[day].append(task)
        kinds[day][stream] += task["minutes"]

    # GenAI + Agentic lessons, weeks 1-9.
    for w, week in enumerate(WEEKS):
        monday = FIRST_MONDAY + timedelta(weeks=w)
        ready_by = (monday - timedelta(days=3)).isoformat()
        assert len(week) == 6, f"week {w + 1} needs 6 days (Mon-Sat)"
        for offset, items in enumerate(week):
            day = monday + timedelta(days=offset)
            for track, n in items:
                ref = by_number[track][n]
                for part in lesson_parts(ref):
                    suffix = f"-p{part['part'][0]}" if "part" in part else ""
                    task = {"id": f"{day.isoformat()}-main-{ref.slug}{suffix}", **part}
                    if not ref.available:
                        task["ready_by"] = ready_by
                        task["planned"] = True
                    add(day, "lessons", task)

    # Week 10: buffer and polish.
    for offset, (title, steps, links) in enumerate(W10):
        day = date(2027, 1, 25) + timedelta(days=offset)
        add(day, "revision", {
            "id": f"{day.isoformat()}-revision", "kind": "review", "minutes": 60, "title": title, "steps": steps,
            "links": [link(t, n) for t, n in links],
        })

    # From week 11 on: a rotating 30-minute revision task (the last day has its own mock interview).
    rotation_days = study_days(date(2027, 2, 1), END - timedelta(days=1))
    for i, day in enumerate(rotation_days):
        title, links = ROTATION[i % len(ROTATION)]
        add(day, "revision", {
            "id": f"{day.isoformat()}-revision", "kind": "review", "minutes": 30,
            "title": f"Revise {title}", "steps": ROTATION_STEPS, "links": [link(t, n) for t, n in links],
        })
    add(END, "revision", {
        "id": f"{END.isoformat()}-final-mock", "kind": "review", "minutes": 120, "title": "Final mock interview",
        "steps": [
            "Ask Claude in a chat to interview you for 60 minutes: GenAI, RAG, agents and LLM system design",
            "Solve 2 unseen medium DSA problems in 25 minutes each, no hints",
            "Write down every weak spot, and the plan for the next 4 weeks",
        ],
        "links": [link("genai", 31), link("agentic", 19), link("agentic", 20)],
    })

    # DSA phase 1: one stream of exercises, Mon-Sat, Easy + Medium only. Hard ones wait for phase 2.
    diffs = load_difficulty()
    facts: dict[str, dict] = {}
    refs = {r.slug: r for r in tracks["dsa"].lessons}
    queue: list[tuple[str, str]] = []  # (lesson slug, exercise id), in learning order
    hard: list[tuple[str, str]] = []
    pool: dict[str, list[tuple[str, str, str, str]]] = {}  # slug -> [(slug, exercise id, title, diff)]
    for ref in tracks["dsa"].lessons:
        facts[ref.slug] = lesson_facts("dsa", ref.slug)
        pool[ref.slug] = []
        for ex in facts[ref.slug]["exercise_ids"]:
            if (ref.slug, ex) not in diffs:
                raise SystemExit(f"{ref.slug}/{ex} is not in content/dsa/QUESTIONS.md (needs a difficulty)")
            title, diff = diffs[(ref.slug, ex)]
            pool[ref.slug].append((ref.slug, ex, title, diff))
            (hard if diff == "H" else queue).append((ref.slug, ex))
    days1 = study_days(START, PHASE1_END)
    # Fewer exercises on days that already have a heavy lesson, more on light days. The total stays fixed.
    weights = [min(6.5, max(3.5, (160 - kinds[d]["lessons"] - kinds[d]["revision"]) / 8)) for d in days1]
    cum = [0.0]
    for wt in weights:
        cum.append(cum[-1] + wt)
    edges = [round(len(queue) * c / cum[-1]) for c in cum]
    per_day = [edges[i + 1] - edges[i] for i in range(len(days1))]
    pos = 0
    chunks: dict[str, list[tuple[date, list[str]]]] = {}
    for day, n in zip(days1, per_day):
        by_lesson: dict[str, list[str]] = {}
        for slug, ex in queue[pos: pos + n]:
            by_lesson.setdefault(slug, []).append(ex)
        pos += n
        for slug, ids in by_lesson.items():
            chunks.setdefault(slug, []).append((day, ids))
    for slug, parts in chunks.items():
        f, ref = facts[slug], refs[slug]
        for k, (day, ids) in enumerate(parts):
            first, last = k == 0, k == len(parts) - 1
            steps = ["Read the toolbox (about 10 min)"] if first else []
            steps.append(f"Exercises {len(ids)} (every test must pass)")
            task = {
                "id": f"{day.isoformat()}-dsa-{slug}", "kind": "practise", "track": "dsa", "lesson": slug,
                "title": ref.title, "part": [k + 1, len(parts)], "exercise_ids": ids,
                "minutes": int(round((8 * len(ids) + 10 * first + f["quiz"] * last) / 5) * 5),
            }
            if last and f["quiz"]:
                task["quiz"] = True
                steps.append(f"Quiz: {f['quiz']} questions, pass with 75% or more")
            task["steps"] = steps
            add(day, "dsa", task)

    # DSA phase 2: redo without hints, medium first, then down to the basics, then a mixed set.
    used: set[tuple[str, str]] = set()

    def redo(day: date, title: str, rows: list[tuple[str, str, str, str]], minutes: int, extra: list[str] | None = None):
        lessons, seen = [], set()
        for slug, ex, _t, _d in rows:
            if slug not in seen:
                seen.add(slug)
                lessons.append({"track": "dsa", "lesson": slug, "title": refs[slug].title})
        steps = [f"{t} ({'optional Hard, ' if d == 'H' else ''}{slug}/{ex})" for slug, ex, t, d in rows]
        add(day, "dsa", {
            "id": f"{day.isoformat()}-dsa-redo", "kind": "review", "track": "dsa", "title": title,
            "minutes": minutes, "steps": ["No hints, no solution. Solve each one from memory, then tick the task:"]
            + steps + (extra or []), "links": lessons,
        })

    for title, first, last, numbers, k, each in PHASE2_BLOCKS:
        days = study_days(first, last)
        medium_only = each == 25
        rows = [r for n in numbers for slug in pool if int(slug.split("-")[0]) == n for r in pool[slug]
                if (r[3] == "M" if medium_only else r[3] in "EM")]
        chosen = pick(rows, k * len(days))
        used.update((r[0], r[1]) for r in chosen)
        for i, day in enumerate(days):
            redo(day, f"Redo: {title}", chosen[i * k:(i + 1) * k], k * each)
    mixed_days = study_days(*MIXED_DAYS)
    left = [r for n in range(14, 30) for slug in pool if int(slug.split("-")[0]) == n for r in pool[slug]
            if r[3] == "M" and (r[0], r[1]) not in used]
    mixed = pick(left, 2 * len(mixed_days))
    hards = pick([r for slug in pool for r in pool[slug] if r[3] == "H"], 2 * len(mixed_days))
    for i, day in enumerate(mixed_days):
        redo(day, "Mixed set: medium problems from every pattern, plus Hard (optional)",
             mixed[2 * i: 2 * i + 2] + hards[2 * i: 2 * i + 2], 110)

    out = {
        "title": "Roadmap: GenAI, Agentic AI and DSA (120 days)",
        "start": START.isoformat(),
        "end": END.isoformat(),
        "tracks": {},
        "days": [{"date": d.isoformat(), "tasks": plan[d]} for d in sorted(plan)],
    }
    header = (
        "# GENERATED by scripts/build_roadmap.py. The plan is fixed: change the script and run it again.\n"
        "# kinds: practise = a site lesson (done when the quiz is 75%+ and all its exercises pass), review = tick it yourself.\n"
    )
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "content" / "roadmap.yaml"  # optional: a preview file
    target.write_text(
        header + yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=120)
    )

    # Report: planned load per week, and days that are too full.
    print(f"DSA phase 1: {len(queue)} Easy+Medium exercises on {len(days1)} days, {len(hard)} Hard moved to phase 2")
    for w in range(18):
        monday = FIRST_MONDAY + timedelta(weeks=w)
        week_days = [monday + timedelta(days=i) for i in range(6) if monday + timedelta(days=i) <= END]
        les = sum(kinds[d]["lessons"] for d in week_days)
        dsa = sum(kinds[d]["dsa"] for d in week_days)
        rev = sum(kinds[d]["revision"] for d in week_days)
        print(f"W{w + 1:>2} {monday}  lessons {les / 60:4.1f} h  dsa {dsa / 60:4.1f} h  revision {rev / 60:4.1f} h")
    over = [(d.isoformat(), sum(t["minutes"] for t in ts)) for d, ts in plan.items()
            if sum(t["minutes"] for t in ts) > (175 if d.weekday() < 5 else 150)]
    print("days over the limit (175 min weekday, 150 min Saturday):", over)


if __name__ == "__main__":
    main()
