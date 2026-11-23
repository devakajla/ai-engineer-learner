from solution import recall, save_fact


def test_save_and_recall():
    store = {}
    assert save_fact(store, "u1", "Dev likes Python") is True
    assert save_fact(store, "u1", "Dev lives in Pune") is True
    assert recall(store, "u1", "Pune") == ["Dev lives in Pune"]
    assert recall(store, "u1", "dev python") == ["Dev likes Python", "Dev lives in Pune"], "two matches beat one"


def test_duplicate_facts_are_not_saved_twice():
    store = {}
    assert save_fact(store, "u1", "Dev likes Python") is True
    assert save_fact(store, "u1", "  dev LIKES python ") is False
    assert store["u1"] == ["Dev likes Python"]


def test_facts_are_kept_per_user():
    store = {}
    save_fact(store, "u1", "likes tea")
    save_fact(store, "u2", "likes coffee")
    assert recall(store, "u1", "likes") == ["likes tea"]
    assert recall(store, "u2", "likes") == ["likes coffee"]
    assert recall(store, "u3", "likes") == [], "an unknown user has no facts"


def test_best_match_first_and_k_limit():
    store = {}
    for fact in ["Dev likes tea", "Dev likes strong tea in the morning", "Asha likes tea"]:
        save_fact(store, "u", fact)
    out = recall(store, "u", "strong tea morning", k=2)
    assert out[0] == "Dev likes strong tea in the morning"
    assert len(out) == 2


def test_no_match_gives_empty_list():
    store = {}
    save_fact(store, "u", "likes tea")
    assert recall(store, "u", "zebra") == []
