"""Help on exercises: the 'Tools you will need' box, Coach hints and the walkthrough. Claude is faked."""

from app.content import get_lesson
from app.services import claude
from app.services.tools_needed import tools_needed
from tests.test_app import client  # noqa: F401  (fixture)

LESSON = "genai/03-first-groq-call"
EXERCISE = "01-ask"


def _exercise(track: str, slug: str, ex_id: str):
    return next(e for e in get_lesson(track, slug).exercises if e.id == ex_id)


def test_tools_needed_names_tools_not_code():
    tools = tools_needed(_exercise("genai", "03-first-groq-call", "01-ask"))
    names = " ".join(t["name"] for t in tools)
    assert "dictionary" in names and "list" in names, names
    assert "dot" in names, "response.choices[0].message.content is an attribute read"
    assert "choices" not in names and "messages" not in names, "solution code must never leak"
    by_name = {t["name"]: t["lesson_id"] for t in tools}
    assert by_name["Make a dictionary with `{key: value}`"] == "python/11-dicts"


def test_tools_needed_skips_given_code():
    tools = tools_needed(_exercise("genai", "05-parameters", "03-ask-with-options"))
    assert tools[0]["name"] == "Use the given function `build_messages()`"
    assert tools[0]["lesson_id"] is None


def _fake(text: str, seen: list):
    async def fake(*args, **kwargs):
        seen.append(args)
        yield text
        yield claude.StreamDone(text=text, session_id=None)

    return fake


def test_coach_streams_and_records_level(client, monkeypatch):  # noqa: F811
    seen: list = []
    reply = "# IDEA: send one message\n# STEP 1: make a dictionary\nTOPIC: 11-dicts | dict literal"
    monkeypatch.setattr(claude, "exercise_coach_stream", _fake(reply, seen))
    r = client.post(f"/api/practice/{LESSON}/{EXERCISE}/coach", data={"code": "def ask(...):", "level": 9})
    assert r.status_code == 200 and "# STEP 1" in r.text
    assert seen[0][5] == 3, "level is clamped to 3"
    assert "def ask(client, question" in seen[0][2], "the solution reaches Claude (only for Claude)"
    help_ = next(e for e in client.get(f"/api/lessons/{LESSON}").json()["exercises"] if e["id"] == EXERCISE)["help"]
    assert help_["coach_level"] == 3 and help_["walkthrough_ready"] is False
    topics = {t["tag"]: t for t in client.get("/api/trial/topics").json()}
    assert topics["11-dicts"]["coach"] == 1, "the hint is a weak-spot signal"


def test_walkthrough_locked_until_really_stuck(client, monkeypatch):  # noqa: F811
    seen: list = []
    monkeypatch.setattr(claude, "exercise_coach_stream", _fake("# hint\nTOPIC: none", []))
    monkeypatch.setattr(claude, "walkthrough_stream", _fake("## The idea\nSend one message.\nTOPIC: 11-dicts | x", seen))
    url = f"/api/practice/{LESSON}/{EXERCISE}"
    assert client.post(f"{url}/walkthrough", data={"code": ""}).status_code == 403
    for _ in range(3):
        assert client.post(url, data={"code": "def ask(client, question):\n    return 1\n"}).json()["passed"] is False
    assert client.post(f"{url}/walkthrough", data={"code": ""}).status_code == 403, "hint level 3 not seen yet"
    client.post(f"{url}/coach", data={"code": "", "level": 3})
    r = client.post(f"{url}/walkthrough", data={"code": ""})
    assert r.status_code == 200 and "## The idea" in r.text
    help_ = next(e for e in client.get(f"/api/lessons/{LESSON}").json()["exercises"] if e["id"] == EXERCISE)["help"]
    assert help_ == {"coach_level": 3, "walkthrough": True, "fails": 3, "walkthrough_ready": True}
    assert {t["tag"]: t for t in client.get("/api/trial/topics").json()}["11-dicts"]["walkthrough"] == 1
