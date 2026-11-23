from solution import split_thinking


def test_examples():
    assert split_thinking("<think>23-9=14</think>\nAnswer: 14") == ("23-9=14", "Answer: 14")
    assert split_thinking("Just an answer.") == ("", "Just an answer.")
    assert split_thinking("<think>still thinking") == ("still thinking", "")


def test_spaces_and_newlines():
    assert split_thinking("<think>\n a \n</think>\n\n b \n") == ("a", "b")


def test_text_before_the_tag_is_ignored():
    assert split_thinking("noise <think>t</think> a") == ("t", "a")


def test_empty_thinking():
    assert split_thinking("<think></think>Hi") == ("", "Hi")
    assert split_thinking("") == ("", "")
