from solution import build_context, size

STORE = {"u": ["Dev likes Python", "Dev lives in Pune", "Asha likes tea"]}
HISTORY = [
    {"role": "user", "content": "first question"},
    {"role": "assistant", "content": "first answer"},
    {"role": "user", "content": "second question"},
    {"role": "assistant", "content": "second answer"},
]


def test_order_system_facts_history_question():
    out = build_context("Be kind.", STORE, "u", HISTORY, "python tips", 10_000)
    assert out[0] == {"role": "system", "content": "Be kind."}
    assert out[1] == {"role": "system", "content": "Known facts about the user:\n- Dev likes Python"}
    assert out[2:6] == HISTORY
    assert out[-1] == {"role": "user", "content": "python tips"}
    assert len(out) == 7


def test_no_matching_facts_means_no_facts_message():
    out = build_context("Be kind.", STORE, "u", HISTORY, "zebra", 10_000)
    assert [m["role"] for m in out] == ["system", "user", "assistant", "user", "assistant", "user"]


def test_oldest_history_is_dropped_first():
    out = build_context("S", {}, "u", HISTORY, "Q", max_chars=size(HISTORY[2:]) + 2)
    assert [m["content"] for m in out] == ["S", "second question", "second answer", "Q"]


def test_system_and_question_are_never_dropped():
    out = build_context("Be kind.", STORE, "u", HISTORY, "python tips", max_chars=1)
    assert out[0]["content"] == "Be kind."
    assert out[-1]["content"] == "python tips"
    assert all(m not in HISTORY for m in out), "all history is dropped when nothing else fits"


def test_total_size_stays_within_the_budget_when_possible():
    out = build_context("S", {}, "u", HISTORY, "Q", max_chars=40)
    assert size(out) <= 40


def test_history_is_not_changed_in_place():
    history = list(HISTORY)
    build_context("S", {}, "u", history, "Q", max_chars=5)
    assert history == HISTORY
