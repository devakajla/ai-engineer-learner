from solution import merge_messages


def m(id, text):
    return {"id": id, "text": text}


def test_new_messages_are_appended():
    assert merge_messages([m("1", "a")], [m("2", "b")]) == [m("1", "a"), m("2", "b")]


def test_same_id_replaces_in_place():
    assert merge_messages([m("1", "a"), m("2", "b")], [m("1", "A")]) == [m("1", "A"), m("2", "b")]


def test_messages_without_an_id_are_always_appended():
    old = [{"text": "x"}]
    assert merge_messages(old, [{"text": "x"}]) == [{"text": "x"}, {"text": "x"}]


def test_duplicate_ids_inside_new_replace_each_other():
    assert merge_messages([], [m("1", "a"), m("1", "b")]) == [m("1", "b")]


def test_inputs_are_not_changed():
    old, new = [m("1", "a")], [m("1", "b"), m("2", "c")]
    merge_messages(old, new)
    assert old == [m("1", "a")] and new == [m("1", "b"), m("2", "c")]


def test_empty_cases():
    assert merge_messages([], []) == []
    assert merge_messages([m("1", "a")], []) == [m("1", "a")]
