from solution import JUDGE_SYSTEM, build_judge_messages


def test_shape():
    messages = build_judge_messages("Q?", "some text", "A.")
    assert [m["role"] for m in messages] == ["system", "user"]
    assert messages[0]["content"] == JUDGE_SYSTEM


def test_user_text_exact():
    user = build_judge_messages("Q?", "some text", "A.")[1]["content"]
    assert user == "<question>\nQ?\n</question>\n<context>\nsome text\n</context>\n<answer>\nA.\n</answer>"


def test_system_asks_for_json_score():
    assert "score" in JUDGE_SYSTEM and "JSON" in JUDGE_SYSTEM


def test_keeps_text_as_is():
    user = build_judge_messages("a\nb", "", "x")[1]["content"]
    assert "a\nb" in user and "<context>\n\n</context>" in user
