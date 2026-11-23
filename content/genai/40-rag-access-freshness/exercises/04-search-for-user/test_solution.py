from solution import search_for_user

DB = [
    {"id": "1", "tenant": "other", "updated": "2026-11-01"},
    {"id": "2", "tenant": "acme", "groups": ["hr"], "updated": "2026-11-01"},
    {"id": "3", "tenant": "acme", "updated": "2020-01-01"},
    {"id": "4", "tenant": "acme", "updated": "2026-10-01"},
    {"id": "5", "tenant": "acme", "updated": "2026-10-02"},
    {"id": "6", "tenant": "acme", "updated": "2026-10-03"},
]
USER = {"tenant": "acme", "groups": ["dev"]}


class Spy:
    def __init__(self):
        self.asked = []

    def __call__(self, question, k):
        self.asked.append(k)
        return DB[:k]


def test_filters_and_cuts():
    out = search_for_user(Spy(), USER, "q", k=2)
    assert [h["id"] for h in out] == ["3", "4"]


def test_overfetch_k():
    spy = Spy()
    search_for_user(spy, USER, "q", k=2, overfetch=3)
    assert spy.asked == [6]


def test_default_overfetch_is_five():
    spy = Spy()
    search_for_user(spy, USER, "q", k=2)
    assert spy.asked == [10]


def test_stale_applied_only_with_both_args():
    out = search_for_user(Spy(), USER, "q", k=3, today="2026-11-23", max_age_days=100)
    assert [h["id"] for h in out] == ["4", "5", "6"]
    out2 = search_for_user(Spy(), USER, "q", k=3, today="2026-11-23")
    assert out2[0]["id"] == "3"


def test_hr_user_sees_hr_chunk():
    out = search_for_user(Spy(), {"tenant": "acme", "groups": ["hr"]}, "q", k=1)
    assert out[0]["id"] == "2"


def test_k_zero():
    spy = Spy()
    assert search_for_user(spy, USER, "q", k=0) == []
    assert spy.asked == []
