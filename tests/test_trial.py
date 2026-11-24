"""Trial room: free runs and the comment-only coach. Claude is faked, nothing touches the network."""

import asyncio
import json

from app.services import claude
from app.services.runner import run_script
from tests.test_app import client  # noqa: F401  (fixture)


def test_run_script_prints_and_reports_errors():
    ok = asyncio.run(run_script("print('hi')\nprint(1 + 2)"))
    assert ok.stdout.splitlines() == ["hi", "3"]
    assert ok.stderr == "" and not ok.timed_out

    bad = asyncio.run(run_script("print(1 / 0)"))
    assert "ZeroDivisionError" in bad.stderr
    assert "<trial>" in bad.stderr  # temp path hidden


def test_run_script_timeout_and_input_do_not_hang():
    slow = asyncio.run(run_script("while True:\n    pass", timeout=1))
    assert slow.timed_out

    asked = asyncio.run(run_script("x = input('name? ')", timeout=5))
    assert "EOFError" in asked.stderr


def test_run_endpoint(client):  # noqa: F811
    r = client.post("/api/trial/run", data={"code": "print('ok')"})
    assert r.status_code == 200
    assert r.json()["stdout"] == "ok\n"
    assert client.post("/api/trial/run", data={"code": "   "}).status_code == 400
    assert client.post("/api/trial/run", data={"code": "x" * 200_001}).status_code == 413


def _topics(client):
    return {t["tag"]: t for t in client.get("/api/trial/topics").json()}


def test_coach_saves_topic_and_gets_profile(client, monkeypatch):  # noqa: F811
    seen = []

    async def fake_coach(code, output, attempt, ai, profile="", tags=""):
        seen.append({"attempt": attempt, "profile": profile, "tags": tags})
        text = "# IDEA: look inside the dict\n# STEP 1: use .items()\nTOPIC: 11-dicts | loop over inner dict"
        yield text
        yield claude.StreamDone(text=text, session_id=None)

    monkeypatch.setattr(claude, "coach_stream", fake_coach)
    for n in (1, 2):
        r = client.post("/api/trial/coach", data={"code": "# PROBLEM: x\n", "output": "", "attempt": n})
        assert r.status_code == 200
        assert "# STEP 1" in r.text
    assert seen[1]["attempt"] == 2
    assert "11-dicts: " in seen[0]["tags"]  # the topic list reaches Claude
    assert seen[0]["profile"] == ""  # nothing known on the first press
    assert "(11-dicts)" in seen[1]["profile"]  # the first press is now a weak spot
    dicts = _topics(client)["11-dicts"]
    assert dicts["coach"] == 2 and dicts["score"] == 4 and dicts["details"] == ["loop over inner dict"]


def test_coach_failure_is_a_comment_not_a_500(client, monkeypatch):  # noqa: F811
    async def broken(*args):
        raise RuntimeError("no cli")
        yield  # pragma: no cover

    monkeypatch.setattr(claude, "coach_stream", broken)
    r = client.post("/api/trial/coach", data={"code": "x = 1"})
    assert r.status_code == 200
    assert r.text.startswith("# Coach is not available")
    assert client.get("/api/trial/topics").json() == []


def test_trial_chat_streams_passes_history_and_tags_only_gaps(client, monkeypatch):  # noqa: F811
    seen = {}
    replies = iter(
        [
            "A dict maps keys to values.\nTOPIC: 11-dicts | what a dict is",
            "Fine, that is right.\nTOPIC: none",
        ]
    )

    async def fake_chat(message, code, output, history, ai, profile="", tags=""):
        seen.update(message=message, code=code, output=output, history=history, tags=tags)
        text = next(replies)
        yield text
        yield claude.StreamDone(text=text, session_id=None)

    monkeypatch.setattr(claude, "trial_chat_stream", fake_chat)
    body = {
        "message": "what is a dict?",
        "code": "x = 1",
        "output": "1",
        "history": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}],
    }
    r = client.post("/api/trial/chat", json=body)
    assert r.status_code == 200 and r.text.startswith("A dict maps keys to values.")
    assert seen["history"] == [("user", "hi"), ("assistant", "hello")]
    assert seen["code"] == "x = 1" and "06-conditionals" in seen["tags"]
    assert client.post("/api/trial/chat", json={"message": "  "}).status_code == 400
    assert _topics(client)["11-dicts"]["chat"] == 1
    client.post("/api/trial/chat", json={"message": "is this right?"})
    assert _topics(client)["11-dicts"]["chat"] == 1  # TOPIC: none saves nothing


def test_trial_chat_failure_is_text_not_500(client, monkeypatch):  # noqa: F811
    async def broken(*args):
        raise RuntimeError("no cli")
        yield  # pragma: no cover

    monkeypatch.setattr(claude, "trial_chat_stream", broken)
    r = client.post("/api/trial/chat", json={"message": "hi"})
    assert r.status_code == 200 and "not available" in r.text


def test_parse_topic():
    tags = {"11-dicts": "Dicts", "06-conditionals": "Conditionals"}
    assert claude.parse_topic("# a\nTOPIC: 11-dicts | loop with items\n", tags) == ("11-dicts", "loop with items")
    assert claude.parse_topic("TOPIC: Conditionals | not in", tags) == ("06-conditionals", "not in")  # by title
    assert claude.parse_topic("TOPIC: made-up | thing", tags) == ("other", "made-up | thing")
    assert claude.parse_topic("TOPIC: none", tags) is None
    assert claude.parse_topic("# no topic", tags) is None


def test_profile_uses_failed_tests_and_drills(client):  # noqa: F811
    from app import db
    from app.models import Drill, Submission
    from app.services.profile import build_profile, profile_text

    async def go():
        async with db.SessionLocal() as s:
            lesson = "python/11-dicts"
            ex = "01-count-words"
            for _ in range(3):
                s.add(Submission(lesson_id=lesson, exercise_id=ex, code="x", tests_passed=False, tests_output=""))
            s.add(Submission(lesson_id="fastapi/01-x", exercise_id="a", code="x", tests_passed=False, tests_output=""))
            for status in ("done", "open"):
                s.add(
                    Drill(tag="11-dicts", title="t", prompt="p", starter="s", solution="x", calls_json="[]",
                          expected_json="[]", status=status)
                )  # fmt: skip
            await s.commit()
        async with db.SessionLocal() as s:
            return await build_profile(s)

    profile = asyncio.run(go())
    assert [p["tag"] for p in profile] == ["11-dicts"]  # the fastapi failure is ignored
    d = profile[0]
    assert d["failed"][0]["fails"] == 3 and d["drills_done"] == 1 and d["drills_total"] == 2
    assert d["score"] == 1  # 3 failed runs - 2 for the solved drill
    assert "drills 1/2 done" in profile_text(profile)


_DRILLS = json.dumps(
    [
        {
            "title": "Double it", "prompt": "Return n doubled.", "function_name": "double",
            "starter": "def double(n):\n    pass", "solution": "def double(n):\n    return n * 2",
            "calls": ["double(2)", "double(0)", "double(-3)"],
        },
        {
            "title": "Broken one", "prompt": "x", "function_name": "boom",
            "starter": "def boom(n):\n    pass", "solution": "def boom(n):\n    return 1 / 0",
            "calls": ["boom(1)", "boom(2)"],
        },
        {
            "title": "Shout", "prompt": "Make upper case.", "function_name": "shout",
            "starter": "def shout(s):\n    pass", "solution": "def shout(s):\n    return s.upper()",
            "calls": ['shout("a")', 'shout("")'],
        },
    ]
)  # fmt: skip


def test_drills_are_validated_checked_and_hide_the_solution(client, monkeypatch):  # noqa: F811
    async def fake_generate(lesson, details, profile, ai):
        return "Here you go:\n```json\n" + _DRILLS + "\n```"

    monkeypatch.setattr(claude, "generate_drills", fake_generate)
    assert client.post("/api/trial/drills", json={"tag": "nope"}).status_code == 400
    r = client.post("/api/trial/drills", json={"tag": "11-dicts"})
    assert r.status_code == 200
    made = r.json()
    assert [d["title"] for d in made] == ["Double it", "Shout"]  # the drill whose solution crashes is dropped
    assert all("solution" not in d and "expected" not in d for d in made)

    did = made[0]["id"]
    wrong = client.post(f"/api/trial/drills/{did}/check", json={"code": "def double(n):\n    return n + 2"}).json()
    assert not wrong["passed"] and wrong["status"] == "open"
    failed = [x for x in wrong["results"] if not x["ok"]]
    assert failed and failed[0]["want"] is not None
    assert next(x for x in wrong["results"] if x["call"] == "double(2)")["ok"]  # 2 + 2 == 2 * 2

    crash = client.post(f"/api/trial/drills/{did}/check", json={"code": "def double(n:\n"}).json()
    assert not crash["passed"] and "SyntaxError" in crash["error"]

    right = client.post(f"/api/trial/drills/{did}/check", json={"code": "def double(n):\n    return n * 2"}).json()
    assert right["passed"] and right["status"] == "done"
    assert [d["status"] for d in client.get("/api/trial/drills", params={"tag": "11-dicts"}).json()] == ["done", "open"]

    # Making drills again replaces the open ones and keeps the solved one.
    again = client.post("/api/trial/drills", json={"tag": "11-dicts"}).json()
    listed = client.get("/api/trial/drills", params={"tag": "11-dicts"}).json()
    assert [d["status"] for d in listed] == ["done", "open", "open"] and len(again) == 2
    assert client.post("/api/trial/drills/999/check", json={"code": "x = 1"}).status_code == 404


def test_drills_unusable_reply_is_502(client, monkeypatch):  # noqa: F811
    async def fake_generate(lesson, details, profile, ai):
        return "sorry, no json"

    monkeypatch.setattr(claude, "generate_drills", fake_generate)
    assert client.post("/api/trial/drills", json={"tag": "11-dicts"}).status_code == 502
