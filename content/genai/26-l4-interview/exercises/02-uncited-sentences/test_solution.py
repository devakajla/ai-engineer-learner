from solution import uncited_sentences


def test_example():
    assert uncited_sentences("Use DELETE [1]. It is fast. Send a token [2].") == ["It is fast."]


def test_decimal_not_a_split():
    assert uncited_sentences("Version 3.5 is out [1].") == []
    assert uncited_sentences("Version 3.5 is out.") == ["Version 3.5 is out."]


def test_all_cited_and_none():
    assert uncited_sentences("A [1]. B [2]!") == []
    assert uncited_sentences("") == []
    assert uncited_sentences("   ") == []


def test_bad_markers():
    assert uncited_sentences("A [x]. B []. C [1].") == ["A [x].", "B []."]


def test_question_and_trailing_text():
    assert uncited_sentences("Why? Because [1]. no end") == ["Why?", "no end"]


def test_multiple_markers():
    assert uncited_sentences("A [1][2]. B.") == ["B."]
