import asyncio

import pytest
from fastapi.testclient import TestClient

from app import db
from app.content import get_lesson, get_tracks
from app.routers.quiz import score_quiz
from app.services.runner import run_tests


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Fresh SQLite DB per test so the real data/learner.db is never touched.
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setattr(db, "engine", engine)
    session_local = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(db, "SessionLocal", session_local)
    # Routers that save after streaming imported SessionLocal by name.
    from app.routers import chat, practice, project, trial

    for mod in (chat, practice, project, trial):
        monkeypatch.setattr(mod, "SessionLocal", session_local)
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_tracks_load_in_order():
    tracks = get_tracks()
    assert list(tracks) == ["python", "fastapi", "dsa", "genai", "agentic"]
    assert tracks["python"].lessons[0].slug == "01-intro-setup"


def test_quiz_scoring_needs_exact_set():
    quiz = get_lesson("python", "05-booleans-operators").quiz
    multi = quiz[0]
    assert score_quiz([multi], [multi.answer]) == [True]
    assert score_quiz([multi], [multi.answer[:-1]]) == [False]
    assert score_quiz([multi], [multi.answer + [4]]) == [False]


def _exercise(track, slug, ex_id):
    return next(e for e in get_lesson(track, slug).exercises if e.id == ex_id)


def test_runner_pass_fail_timeout():
    ex = _exercise("python", "01-intro-setup", "01-hello")
    good = asyncio.run(run_tests('def greet(name):\n    return f"Hello, {name}!"\n', ex.dir))
    assert good.passed
    bad = asyncio.run(run_tests("def greet(name):\n    print(name)\n", ex.dir))
    assert not bad.passed and "failed" in bad.summary
    slow = asyncio.run(run_tests("while True:\n    pass\n", ex.dir, timeout=2))
    assert slow.timed_out and not slow.passed


def test_lesson_api_hides_quiz_answers(client):
    data = client.get("/api/lessons/python/02-variables-types").json()
    assert data["title"] == "Variables & data types"
    assert "answer" not in data["quiz"][0]
    assert data["status"] == "learning"
    assert data["prev"]["slug"] == "01-intro-setup"


def test_quiz_and_progress_flow(client):
    lesson = get_lesson("python", "01-intro-setup")
    answers = [q.answer for q in lesson.quiz]
    r = client.post("/api/quiz/python/01-intro-setup", json={"answers": answers}).json()
    assert r["score"] == r["total"] == len(lesson.quiz)

    assert client.post("/api/progress/python/01-intro-setup", json={"status": "done"}).status_code == 200
    track = client.get("/api/tracks/python").json()
    assert track["done"] == 1
    assert track["next_up"]["slug"] == "02-variables-types"


def test_practice_submit_runs_tests(client):
    r = client.post(
        "/api/practice/python/01-intro-setup/02-shout",
        data={"code": "def shout(text):\n    return text.upper() + '!!!'\n"},
    ).json()
    assert r["passed"] is True
    files = {"file": ("mine.py", b"def shout(text):\n    return text\n", "text/x-python")}
    r = client.post("/api/practice/python/01-intro-setup/02-shout", files=files).json()
    assert r["passed"] is False


def test_review_is_reused_for_identical_code(client, monkeypatch):
    from app.services import claude

    calls = []

    async def fake_review(*args):
        calls.append(1)
        yield "VERDICT: CORRECT\n\nLooks good."
        yield claude.StreamDone(text="VERDICT: CORRECT\n\nLooks good.", session_id=None)

    monkeypatch.setattr(claude, "review_stream", fake_review)
    url = "/api/practice/python/01-intro-setup/02-shout"
    code = {"code": "def shout(text):\n    return text.upper() + '!!!'\n"}
    first = client.post(url, data=code).json()["submission_id"]
    second = client.post(url, data=code).json()["submission_id"]
    assert client.get(f"/api/practice/review/{first}").text.startswith("VERDICT: CORRECT")
    assert client.get(f"/api/practice/review/{first}").text.startswith("VERDICT: CORRECT"), "re-asking returns the saved review"
    assert client.get(f"/api/practice/review/{second}").text.startswith("VERDICT: CORRECT"), "same code reuses the review"
    assert len(calls) == 1, f"Claude should be called once for identical code, got {len(calls)}"


def test_concurrent_lesson_loads_do_not_conflict(client):
    # React dev mode fetches a lesson twice at once; both must succeed.
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(4) as pool:
        codes = list(pool.map(lambda _: client.get("/api/lessons/python/02-variables-types").status_code, range(4)))
    assert codes == [200, 200, 200, 200]


def test_fastapi_lesson_has_project(client):
    data = client.get("/api/lessons/fastapi/02-first-app").json()
    assert data["project"]["has_check"] is True
    assert data["project"]["title"].startswith("Step 2")


def test_project_check_against_reference(client, tmp_path):
    # The reference solution for step 2 must pass its own checkpoint through the API.
    import shutil

    from app.config import CONTENT_DIR

    project = tmp_path / "taskflow"
    shutil.copytree(CONTENT_DIR / "fastapi/02-first-app/project/solution", project)
    (project / "pyproject.toml").unlink()  # run with this interpreter instead of creating a uv env
    r = client.put("/api/settings/project-dir/fastapi", json={"project_dir": str(project)})
    assert r.json()["project_dir"] == str(project)
    check = client.post("/api/project/fastapi/02-first-app/check").json()
    assert check["passed"], check["output"]

    r = client.put("/api/settings/project-dir/fastapi", json={"project_dir": str(tmp_path / "missing")})
    assert client.post("/api/project/fastapi/02-first-app/check").json()["passed"] is False


def test_claude_settings_are_separate_for_chat_and_review(client):
    r = client.get("/api/settings/claude").json()
    assert r["chat"] == {"model": "claude-sonnet-5-5", "effort": "medium"}, "chat defaults to Sonnet/medium"
    assert r["review"] == {"model": "claude-haiku-5-5", "effort": "medium"}, "reviews default to Haiku/medium"
    r = client.put("/api/settings/claude", json={"use": "review", "effort": "low"}).json()
    assert r["review"]["effort"] == "low", "review effort should be saved"
    assert r["chat"]["effort"] == "medium", "changing reviews must not touch chat"
    assert client.put("/api/settings/claude", json={"use": "chat", "model": "nope"}).status_code == 400


def test_doubts_star_note_and_resolve(client):
    url = "/api/doubts/python/02-variables-types"
    r = client.post(url, json={"location": "Theory › Strings", "anchor": "strings", "note": "  Why are strings immutable?  "})
    assert r.status_code == 201
    doubt = r.json()
    assert doubt["note"] == "Why are strings immutable?", "note should be trimmed"
    assert doubt["lesson_title"] == "Variables & data types"
    assert client.post("/api/doubts/python/nope", json={"location": "Quiz"}).status_code == 404

    lesson = client.get("/api/lessons/python/02-variables-types").json()
    assert [d["id"] for d in lesson["doubts"]] == [doubt["id"]], "lesson should include its doubts"
    track = client.get("/api/tracks/python").json()
    ref = next(l for lv in track["levels"] for l in lv["lessons"] if l["slug"] == "02-variables-types")
    assert ref["doubts"] == 1, "sidebar should show one open doubt"

    client.patch(f"/api/doubts/{doubt['id']}", json={"resolved": True})
    assert client.get("/api/doubts").json() == [], "resolved doubts are hidden by default"
    assert len(client.get("/api/doubts?include_resolved=true").json()) == 1
    assert client.delete(f"/api/doubts/{doubt['id']}").status_code == 200
    assert client.get("/api/doubts?include_resolved=true").json() == []


def test_notes_generate_save_update_and_export(client, monkeypatch):
    from app.services import claude

    seen = []

    async def fake_notes(lesson, old_note, new_chat, doubts, wrong_quiz, ai):
        seen.append({"old": old_note, "chat": new_chat, "doubts": doubts})
        yield "### Big idea\nNew note"
        yield claude.StreamDone(text="### Big idea\nNew note", session_id=None)

    monkeypatch.setattr(claude, "notes_stream", fake_notes)
    lesson_url = "/api/notes/python/02-variables-types"

    empty = client.get(lesson_url).json()
    assert empty["exists"] is False and empty["has_new_chat"] is False

    # Chat rows are written directly: the real chat route needs Claude.
    import asyncio

    from app.models import ChatMessage

    async def add_chat(*pairs):
        async with db.SessionLocal() as s:
            for role, text in pairs:
                s.add(ChatMessage(lesson_id="python/02-variables-types", role=role, content=text))
            await s.commit()

    asyncio.run(add_chat(("user", "why immutable?"), ("assistant", "because hashing")))
    note = client.get(lesson_url).json()
    assert note["has_new_chat"] is True, "chat with no note yet counts as new"

    r = client.post(f"{lesson_url}/generate")
    assert r.text == "### Big idea\nNew note"
    assert [c[1] for c in seen[0]["chat"]] == ["why immutable?", "because hashing"]
    assert client.get(lesson_url).json()["exists"] is False, "generate must not save"

    saved = client.put(lesson_url, json={"body": "### Big idea\nNew note\n\n```py\n# keep\n```"}).json()
    assert saved["exists"] and saved["has_new_chat"] is False, "saving covers the chat so far"
    assert client.get("/api/lessons/python/02-variables-types").json()["note"]["exists"] is True

    asyncio.run(add_chat(("user", "and tuples?")))
    assert client.get(lesson_url).json()["has_new_chat"] is True
    client.post(f"{lesson_url}/generate")
    assert [c[1] for c in seen[1]["chat"]] == ["and tuples?"], "update only sends chat since the last note"
    assert "keep" in seen[1]["old"], "the saved (possibly hand-edited) note is the base"

    track = client.get("/api/notes/python").json()
    lessons = [l for lv in track["levels"] for l in lv["lessons"]]
    mine = next(l for l in lessons if l["slug"] == "02-variables-types")
    assert mine["note"]["body"].startswith("### Big idea")
    exported = client.get("/api/notes/python/export.md")
    assert "attachment" in exported.headers["content-disposition"]
    assert "#### Big idea" in exported.text, "note headings are pushed under the lesson heading"
    assert "# keep" in exported.text, "code blocks must not be changed"

    assert client.get("/api/notes/python/nope").status_code == 404
    assert client.get("/api/notes/nope").status_code == 404
    assert client.delete(lesson_url).status_code == 200
    assert client.get(lesson_url).json()["exists"] is False


# ---- roadmap (content/roadmap.yaml) ----


def test_roadmap_refs_exist_and_plan_is_fresh():
    """Every lesson in the plan is listed, and written lessons have their real exercise ids
    (if this fails, run scripts/build_roadmap.py again)."""
    from app.routers.roadmap import load_roadmap

    plan = load_roadmap()
    assert plan["days"], "content/roadmap.yaml is missing: run scripts/build_roadmap.py"
    listed = {r.id: r for t in get_tracks().values() for r in t.lessons}
    ids = [t["id"] for d in plan["days"] for t in d["tasks"]]
    assert len(ids) == len(set(ids)), "duplicate task ids"
    for d in plan["days"]:
        for t in d["tasks"]:
            assert t["kind"] in ("practise", "review"), t["id"]
            if not t.get("lesson"):
                continue
            assert t["lesson_id"] in listed, f"{t['id']}: {t['lesson_id']} is not in any track.yaml"
            if listed[t["lesson_id"]].available:
                assert t["gated"], f"{t['id']}: lesson is written but the plan has no gate: rerun build_roadmap.py"
                real = {e.id for e in get_lesson(t["track"], t["lesson"]).exercises}
                assert set(t.get("exercise_ids", [])) <= real, f"{t['id']}: unknown exercise id"


def test_gate_needs_quiz_and_every_exercise():
    from app.routers.roadmap import Facts, gate_of, is_done

    task = {"id": "t", "gated": True, "lesson_id": "python/08-lists", "quiz": True, "exercise_ids": ["a", "b"]}
    assert not is_done(task, Facts(set(), {}, {}, set()))
    assert not is_done(task, Facts(set(), {"python/08-lists": 100}, {"python/08-lists": {"a"}}, set()))
    assert not is_done(task, Facts(set(), {"python/08-lists": 60}, {"python/08-lists": {"a", "b"}}, set()))
    assert is_done(task, Facts(set(), {"python/08-lists": 75}, {"python/08-lists": {"a", "b"}}, set()))
    # Ticking by hand does not open a gate.
    assert not is_done(task, Facts({"t"}, {}, {}, set()))
    assert gate_of({"id": "r", "gated": False}, Facts(set(), {}, {}, set())) is None


def test_next_tab_points_at_the_first_open_step():
    from app.routers.roadmap import next_tab

    task = {"quiz": True}
    quiz_open = {"quiz": {"ok": False, "best": None}, "exercises": {"ok": False, "solved": 0}}
    assert next_tab(task, quiz_open) == "theory"
    assert next_tab(task, {"quiz": {"ok": False, "best": 50}, "exercises": {"ok": False, "solved": 0}}) == "quiz"
    assert next_tab(task, {"quiz": {"ok": True, "best": 90}, "exercises": {"ok": False, "solved": 1}}) == "practice"
    second_half = {"part": [2, 2]}
    assert next_tab(second_half, {"exercises": {"ok": False, "solved": 0}}) == "practice"


def test_streak_counts_complete_days_and_ignores_open_today():
    from app.routers.roadmap import Facts, streaks

    def day(date, task):
        return {"date": date, "tasks": [{"id": task, "gated": False}]}

    days = [day("2026-01-01", "a"), day("2026-01-02", "b"), day("2026-01-03", "c"), day("2026-01-04", "d")]
    assert streaks(days, "2026-01-02", Facts({"a"}, {}, {}, set())) == (1, 1)  # today open: streak stays
    assert streaks(days, "2026-01-03", Facts({"a"}, {}, {}, set())) == (0, 1)  # day 2 missed: streak breaks
    assert streaks(days, "2026-01-04", Facts({"a", "b", "c", "d"}, {}, {}, set())) == (4, 4)
    rest = [day("2026-01-01", "a"), {"date": "2026-01-02", "tasks": []}, day("2026-01-03", "c")]
    assert streaks(rest, "2026-01-03", Facts({"a", "c"}, {}, {}, set())) == (2, 2)  # a rest day keeps the streak
    assert streaks(rest, "2026-01-03", Facts({"c"}, {}, {}, set())) == (1, 1)  # day 1 missed: streak restarts after it


def test_roadmap_tick_review_task_and_refuse_gated_task(client):
    from app.routers.roadmap import load_roadmap

    tasks = load_roadmap()["tasks"]
    review = next(t for t in tasks.values() if not t["gated"])
    gated = next(t for t in tasks.values() if t["gated"])
    assert client.get("/api/roadmap").status_code == 200
    assert client.put(f"/api/roadmap/tasks/{review['id']}", json={"done": True}).json()["done"] is True
    assert client.put(f"/api/roadmap/tasks/{review['id']}", json={"done": False}).json()["done"] is False
    assert client.put(f"/api/roadmap/tasks/{gated['id']}", json={"done": True}).status_code == 409
    assert client.put("/api/roadmap/tasks/nope", json={"done": True}).status_code == 404


def test_roadmap_lesson_task_done_after_quiz_and_exercises(client):
    from app.routers.roadmap import load_roadmap

    task = next(
        t for t in load_roadmap()["tasks"].values()
        if t["gated"] and t.get("quiz") and t.get("exercise_ids") and t["kind"] == "practise"
    )
    track, slug = task["lesson_id"].split("/")
    lesson = get_lesson(track, slug)
    client.post(f"/api/quiz/{track}/{slug}", json={"answers": [q.answer for q in lesson.quiz]})
    flat = {t["id"]: t for d in client.get("/api/roadmap").json()["days"] for t in d["tasks"]}
    assert flat[task["id"]]["gate"]["quiz"]["ok"] is True
    assert flat[task["id"]]["done"] is False  # exercises are still open
