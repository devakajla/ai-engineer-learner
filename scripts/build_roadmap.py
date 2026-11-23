"""Builds content/roadmap.yaml: the fixed day-by-day study plan (site lessons only, no booklets).

Run:  uv run python scripts/build_roadmap.py
Edit WEEKS below and run again. Run it again after you write new lessons, so the plan
picks up their real quiz and exercise counts. The output is committed: the plan stays fixed
until you regenerate it on purpose.

Rhythm: Mon-Sat one or two site lessons (about 100 min on weekdays, more on Saturday),
Mon-Fri about 45 min of DSA exercises, Sunday a review. Last week: revision only.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.content import get_lesson, get_tracks  # noqa: E402

START = date(2026, 11, 22)  # Sunday, day 1: the first lessons start today
END = date(2027, 3, 22)
FIRST_MONDAY = date(2026, 11, 23)

# Lessons that do not exist as a site track yet. They are written before their week.
PLANNED = {
    "backend": ("Backend", [
        "HTTP, REST and API design recap",
        "SQL, indexes and EXPLAIN",
        "Transactions, isolation levels and locking",
        "Queues, caching and rate limiting patterns",
    ]),
    "agentic": ("Agentic AI", [
        "What an agent is: workflow vs agent",
        "The agent loop from scratch",
        "Tool design for agents",
        "Workflow patterns: chaining, routing, parallel",
        "Agent patterns: ReAct, plan-and-execute, reflection",
        "LangChain basics: models, prompts, LCEL",
        "LangGraph: state, nodes, edges, checkpoints",
        "Memory, context engineering and MCP",
        "Guardrails, human-in-the-loop and agent evals",
        "Deploy an agent behind FastAPI",
    ]),
    "devops": ("DevOps", [
        "Git beyond basics: branching, rebase, PR flow",
        "Linux and shell for backend work",
        "CI/CD with GitHub Actions",
        "Cloud basics: AWS and Kubernetes concepts",
    ]),
    "sysdesign": ("System Design", [
        "How to approach a design question, and estimation",
        "Scaling: load balancers, sharding, replication, CAP",
        "Caching, queues, CDNs; classic designs (URL shortener, chat)",
        "Low-level design: SOLID, parking lot, LRU cache",
        "LLM system design: a RAG chatbot for 10k documents",
        "Document pipelines at scale; LLM latency, cost, safety",
    ]),
    "capstone": ("Capstone", ["Build an agent with 3 to 5 real tools (extend DevDocs Copilot)"]),
}
PLANNED_MINUTES = {"capstone": 180}

# One entry per week (Mon-Sun). main = (track, [lesson numbers]) in the order to do them.
# Python level 3 (30-35) comes later: 30-31 just before FastAPI async, 32-35 in weeks 13-14.
WEEKS = [
    dict(main=[("python", range(1, 9))]),
    dict(main=[("python", range(9, 17))]),
    dict(main=[("python", range(17, 24)), ("genai", range(1, 3))]),
    dict(main=[("python", range(24, 30)), ("genai", range(3, 6))]),
    dict(main=[("genai", range(6, 14))]),
    dict(main=[("fastapi", [1, 2, 3, 4, 5, 25, 26, 6])]),
    dict(main=[("fastapi", [7, 8, 9, 10, 11, 28]), ("genai", [14, 15])]),
    dict(main=[("python", [30, 31]), ("fastapi", [12, 13, 27, 14, 15, 16])]),
    dict(main=[("fastapi", range(17, 22)), ("genai", [16, 17])]),
    dict(main=[("fastapi", [22, 23, 29, 24]), ("genai", [18, 19, 20])]),
    dict(main=[("genai", range(21, 27)), ("backend", [1, 2])]),
    dict(main=[("genai", range(27, 32)), ("backend", [3, 4])]),
    dict(main=[("agentic", range(1, 6)), ("python", [32, 33])]),
    dict(main=[("agentic", range(6, 11)), ("python", [34, 35])]),
    dict(main=[("devops", range(1, 5)), ("sysdesign", [1, 2, 3])]),
    dict(main=[("sysdesign", [4, 5, 6]), ("capstone", [1])]),
]

REVISION = [  # Mon 15 Mar .. Mon 22 Mar
    ("Revise Python", ["Redo the quiz of each Python interview lesson without notes (aim for 90%+)",
                       "Fix every wrong answer, then read your Python notes"],
     [("python", "17-l1-interview"), ("python", "29-l2-interview"), ("python", "35-l3-interview")]),
    ("Revise FastAPI", ["Redo the quiz of each FastAPI interview lesson without notes (aim for 90%+)",
                        "Re-run your TaskFlow tests and fix anything red"],
     [("fastapi", "07-l1-interview"), ("fastapi", "16-l2-interview"), ("fastapi", "24-l3-interview")]),
    ("Revise GenAI", ["Redo the quiz of each GenAI interview lesson without notes (aim for 90%+)",
                      "Run the DevDocs Copilot tests and explain the pipeline out loud"],
     [("genai", "13-l2-interview"), ("genai", "20-l3-interview"), ("genai", "26-l4-interview"),
      ("genai", "31-l5-interview")]),
    ("Revise DSA", ["Open content/dsa/QUESTIONS.md and solve 5 unsolved questions",
                    "Do the DSA Level 4 checkpoint again with no hints"],
     [("dsa", "30-l4-checkpoint")]),
    ("Revise Backend and DevOps", ["Explain auth, caching, queues and Docker out loud in 2 minutes each",
                                   "Answer 10 interview questions from the lessons, then check them"], []),
    ("Revise System Design", ["Design a URL shortener on paper in 30 minutes",
                              "Design a RAG chatbot for 10k documents on paper in 30 minutes"], []),
    ("Mock interview", ["Ask Claude in a chat to interview you for 60 minutes: Python, FastAPI, GenAI",
                        "Write down every question you got wrong"], []),
    ("Weak spots", ["Re-read the lessons for your weak spots from yesterday",
                    "Write the next 4-week plan after this one"], []),
]


def days_between(a: date, b: date) -> list[date]:
    return [a + timedelta(days=i) for i in range((b - a).days + 1)]


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
    if not f["written"]:
        return 90
    minutes = f["words"] / 150 + f["quiz"] + 10 * len(f["exercise_ids"]) + (25 if f["project"] else 0)
    return int(round(minutes / 5) * 5)


def lesson_parts(ref) -> list[dict]:
    """A site lesson as one task, or two (read + quiz, then exercises) when it is long."""
    f = lesson_facts(ref.track, ref.slug)
    base = {"kind": "practise", "track": ref.track, "lesson": ref.slug, "title": ref.title}
    if not f["written"]:
        return [{**base, "minutes": 90, "planned": True,
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


def main() -> None:
    tracks = get_tracks()
    by_number = {
        tid: {int(r.slug.split("-")[0]): r for r in t.lessons} for tid, t in tracks.items()
    }
    plan: dict[date, list[dict]] = {d: [] for d in days_between(START, END)}

    weekly_lessons: list[list[tuple[str, str, str]]] = []
    for w, week in enumerate(WEEKS):
        monday = FIRST_MONDAY + timedelta(weeks=w)
        ready_by = (monday - timedelta(days=3)).isoformat()
        items = []  # (kind, ref-or-planned, minutes, track)
        for track, numbers in week["main"]:
            for n in numbers:
                if track in PLANNED:
                    label, titles = PLANNED[track]
                    items.append(("planned", (track, label, titles[n - 1], n), PLANNED_MINUTES.get(track, 90), track))
                else:
                    ref = by_number[track][n]
                    for part in lesson_parts(ref):
                        items.append(("lesson", (ref, part), part["minutes"], track))
        # Fill the days in order: a lesson moves to the next day when today's main slot is full.
        # Week 1 also uses day 1 (Sunday 22 Nov), so the first lessons start on the first day.
        offsets = [-1, 0, 1, 2, 3, 4, 5] if w == 0 else [0, 1, 2, 3, 4, 5]
        last = len(offsets) - 1
        caps = [105] * last + [270]
        idx, load = 0, 0
        listed = []
        placed = []
        for kind, ref, minutes, track in items:
            if minutes >= 150:
                idx = last
            if load and load + minutes > caps[idx] and idx < last:
                idx, load = idx + 1, 0
            if load and load + minutes > caps[idx] and idx == last:
                print(f"WEEK {w + 1}: Saturday is over capacity ({load + minutes} min)")
            load += minutes
            placed.append((idx, kind, ref, minutes, track))
        for idx, kind, ref, minutes, track in placed:
            day = monday + timedelta(days=offsets[idx])
            if kind == "lesson":
                ref, part = ref
                suffix = f"-p{part['part'][0]}" if "part" in part else ""
                task = {"id": f"{day.isoformat()}-main-{ref.slug}{suffix}", **part}
                if not ref.available:
                    task["ready_by"] = ready_by
                    task["planned"] = True
                plan[day].append(task)
                if (ref.track, ref.slug, ref.title) not in listed:
                    listed.append((ref.track, ref.slug, ref.title))
            else:
                key, label, title, n = ref
                plan[day].append({
                    "id": f"{day.isoformat()}-main-{key}-{n}", "kind": "practise", "track": key, "planned": True,
                    "title": title, "minutes": minutes, "ready_by": ready_by,
                    "steps": ["This module is written before this week starts: lesson, quiz and exercises on the site."],
                })
        weekly_lessons.append(listed)

    # Sunday review of each week, with links to that week's lessons.
    for w, listed in enumerate(weekly_lessons):
        sunday = FIRST_MONDAY + timedelta(weeks=w, days=6)
        links = [{"track": t, "lesson": s, "title": title} for t, s, title in listed if get_lesson(t, s)]
        plan[sunday].append({
            "id": f"{sunday.isoformat()}-review", "kind": "review", "minutes": 60,
            "title": f"Week {w + 1} review",
            "steps": [
                "Open Revise (top bar) and close every open doubt",
                "Retake the quiz of any lesson this week where you scored under 90%",
                "Clear anything still overdue on the home page",
            ],
            "links": links,
        })

    # DSA: one stream of exercises, about 4 to 5 a day (about 45 min), Mon-Fri until Mar 12.
    # Later DSA lessons have 15 to 20 exercises, so the pace is set by exercises, not lessons.
    dsa_days = [d for d in days_between(FIRST_MONDAY, date(2027, 3, 12)) if d.weekday() < 5]
    queue = []  # (lesson ref, exercise id), in order
    facts = {}
    for ref in tracks["dsa"].lessons:
        facts[ref.slug] = lesson_facts("dsa", ref.slug)
        queue += [(ref, ex) for ex in facts[ref.slug]["exercise_ids"]]
    per_day = [len(queue) * (i + 1) // len(dsa_days) - len(queue) * i // len(dsa_days) for i in range(len(dsa_days))]
    pos = 0
    chunks: dict[str, list[tuple[date, list[str]]]] = {}  # slug -> [(day, exercise ids)]
    refs = {r.slug: r for r in tracks["dsa"].lessons}
    for day, n in zip(dsa_days, per_day):
        by_lesson: dict[str, list[str]] = {}
        for ref, ex in queue[pos: pos + n]:
            by_lesson.setdefault(ref.slug, []).append(ex)
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
            plan[day].append(task)

    # Last week: revision only.
    for d, (title, steps, lessons) in zip(days_between(date(2027, 3, 15), END), REVISION, strict=True):
        plan[d].append({
            "id": f"{d.isoformat()}-revision", "kind": "review", "minutes": 120, "title": title, "steps": steps,
            "links": [{"track": t, "lesson": s, "title": get_lesson(t, s).title if get_lesson(t, s) else s}
                      for t, s in lessons],
        })

    out = {
        "title": "4-month plan to job-ready AI Engineer",
        "start": START.isoformat(),
        "end": END.isoformat(),
        "tracks": {k: v[0] for k, v in PLANNED.items()},
        "days": [{"date": d.isoformat(), "tasks": plan[d]} for d in sorted(plan)],
    }
    header = (
        "# GENERATED by scripts/build_roadmap.py. The plan is fixed: change the script and run it again.\n"
        "# kinds: practise = a site lesson (done when the quiz is 75%+ and all its exercises pass), review = tick it yourself.\n"
    )
    (ROOT / "content" / "roadmap.yaml").write_text(
        header + yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=120)
    )

    names = "Mon Tue Wed Thu Fri Sat Sun".split()
    worst: dict[int, tuple[int, str]] = {}
    for d, tasks in plan.items():
        m = sum(t["minutes"] for t in tasks)
        if m > worst.get(d.weekday(), (0, ""))[0]:
            worst[d.weekday()] = (m, d.isoformat())
    print("busiest day per weekday (minutes, date):", {names[k]: worst[k] for k in sorted(worst)})
    over = [(d.isoformat(), sum(t["minutes"] for t in ts)) for d, ts in plan.items()
            if d.weekday() < 5 and sum(t["minutes"] for t in ts) > 160]
    print("weekdays over 160 min:", over)


if __name__ == "__main__":
    main()
