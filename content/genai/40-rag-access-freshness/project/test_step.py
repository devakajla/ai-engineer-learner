"""Step 16 checks. Runs with the current directory = the learner's project folder."""

import json
import uuid
from types import SimpleNamespace as NS

from copilot.access import (
    allowed,
    answer_for_user,
    drop_stale,
    filter_hits,
    load_access,
    search_for_user,
    with_access,
)
from copilot.citations import cited_answer
from copilot.store import add_chunks, open_collection


def embed(texts):
    return [[t.lower().count("salary"), t.lower().count("task"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [
    chunk(0, "tasks.md", "Create", "create a task with POST"),
    chunk(1, "payroll.md", "Salary", "salary bands are secret salary"),
    chunk(2, "other-company.md", "Salary", "globex salary salary salary table"),
    chunk(3, "no-rule.md", "Notes", "a task note with no access rule"),
]

TABLE = {
    "tasks.md": {"tenant": "acme", "groups": [], "updated": "2026-11-01"},
    "payroll.md": {"tenant": "acme", "groups": ["hr"], "updated": "2026-10-01"},
    "other-company.md": {"tenant": "globex", "groups": [], "updated": "2026-11-10"},
}

ENGINEER = {"tenant": "acme", "groups": ["eng"]}
HR = {"tenant": "acme", "groups": ["hr"]}


class FakeClient:
    def __init__(self, text="Done [1]."):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return NS(choices=[NS(message=NS(content=self.text))])


def filled():
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, CHUNKS, embed=embed)
    return collection


def test_earlier_steps_still_work():
    result = cited_answer(FakeClient("Create it [1]."), filled(), "create a task", k=1, embed=embed)
    assert result["ok"] and result["sources"]
    given = [{"source": "a.md", "heading": "", "text": "x", "id": "a"}]
    assert cited_answer(FakeClient("Yes [1]."), None, "q", hits=given)["sources"][0]["source"] == "a.md"
    assert cited_answer(FakeClient("Yes [1]."), None, "q", hits=[])["hits"] == []


def test_load_access(tmp_path):
    assert load_access(tmp_path / "missing.json") == {}
    path = tmp_path / "access.json"
    path.write_text(json.dumps(TABLE))
    assert load_access(path) == TABLE


def test_with_access_adds_rules_and_denies_unknown_sources():
    hits = [{"id": "1", "source": "payroll.md", "text": "x"}, {"id": "2", "source": "no-rule.md", "text": "y"}]
    result = with_access(hits, TABLE)
    assert result[0]["tenant"] == "acme" and result[0]["groups"] == ["hr"] and result[0]["updated"] == "2026-10-01"
    assert result[1]["tenant"] is None and result[1]["groups"] == [] and "updated" not in result[1]
    assert "tenant" not in hits[0], "input hits must not be changed"


def test_allowed():
    open_chunk = {"tenant": "acme", "groups": []}
    hr_chunk = {"tenant": "acme", "groups": ["hr", "legal"]}
    assert allowed(open_chunk, ENGINEER)
    assert not allowed(hr_chunk, ENGINEER) and allowed(hr_chunk, HR)
    assert not allowed({"tenant": "globex", "groups": []}, ENGINEER), "another tenant is never allowed"
    assert not allowed({"tenant": None, "groups": []}, ENGINEER), "no rule means deny"
    assert not allowed({"tenant": None, "groups": []}, {"tenant": None, "groups": []}), "None must not match None"
    assert not allowed(hr_chunk, {"tenant": "acme"}), "a user with no groups key has no groups"


def test_filter_hits_keeps_order():
    hits = [
        {"id": "a", "tenant": "acme", "groups": []},
        {"id": "b", "tenant": "globex", "groups": []},
        {"id": "c", "tenant": "acme", "groups": ["hr"]},
        {"id": "d", "tenant": "acme", "groups": []},
    ]
    assert [h["id"] for h in filter_hits(hits, ENGINEER)] == ["a", "d"]
    assert filter_hits([], ENGINEER) == []


def test_drop_stale():
    hits = [
        {"id": "new", "updated": "2026-11-20"},
        {"id": "old", "updated": "2025-01-01"},
        {"id": "edge", "updated": "2026-10-24"},
        {"id": "undated"},
    ]
    ids = [h["id"] for h in drop_stale(hits, "2026-11-23", 30)]
    assert ids == ["new", "edge", "undated"], "30 days old is still fresh, undated hits are kept"


def test_search_for_user_hides_other_tenants_and_groups():
    collection = filled()
    sources = [h["source"] for h in search_for_user(collection, TABLE, ENGINEER, "salary", k=4, embed=embed)]
    assert "other-company.md" not in sources, "another tenant's chunk leaked"
    assert "payroll.md" not in sources, "an hr-only chunk leaked to an engineer"
    assert "no-rule.md" not in sources, "a chunk without a rule must be hidden"
    assert "tasks.md" in sources
    hr_sources = [h["source"] for h in search_for_user(collection, TABLE, HR, "salary", k=4, embed=embed)]
    assert hr_sources[0] == "payroll.md"


def test_search_for_user_overfetches_so_k_is_still_filled():
    collection = filled()
    hits = search_for_user(collection, TABLE, ENGINEER, "salary", k=1, embed=embed)
    assert len(hits) == 1 and hits[0]["source"] == "tasks.md"
    assert search_for_user(collection, TABLE, ENGINEER, "salary", k=0, embed=embed) == []


def test_search_for_user_drops_stale():
    collection = filled()
    hits = search_for_user(collection, TABLE, HR, "salary", k=3, today="2026-11-23", max_age_days=30, embed=embed)
    assert "payroll.md" not in [h["source"] for h in hits], "payroll.md was updated 54 days ago"


def test_answer_for_user_never_sends_forbidden_text_to_the_model():
    client = FakeClient("Create it [1].")
    result = answer_for_user(client, filled(), TABLE, ENGINEER, "salary", k=3, embed=embed)
    sent = " ".join(m["content"] for m in client.calls[0]["messages"])
    assert "secret" not in sent and "globex" not in sent, "forbidden chunks must never reach the prompt"
    assert result["ok"] and all(s["source"] == "tasks.md" for s in result["sources"])


def test_answer_for_user_with_nothing_allowed_skips_the_model():
    client = FakeClient()
    nobody = {"tenant": "initech", "groups": []}
    result = answer_for_user(client, filled(), TABLE, nobody, "salary", embed=embed)
    assert result["hits"] == [] and result["ok"] and client.calls == []
