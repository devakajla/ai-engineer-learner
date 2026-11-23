from solution import train_and_generate

TEXT = "the cat sat on the mat the cat ran"


def test_examples():
    assert train_and_generate(TEXT, "the", 4) == "the cat sat on"
    assert train_and_generate(TEXT, "The", 2) == "the cat"
    assert train_and_generate(TEXT, "dog", 5) == "dog"


def test_stops_when_no_next_word():
    assert train_and_generate("a b", "a", 10) == "a b", "stop at a word with no next word"


def test_most_common_wins():
    text = "i like tea i like tea i like milk"
    assert train_and_generate(text, "i", 3) == "i like tea", "the most counted word wins"


def test_a_fluent_but_false_sentence():
    # The model only learned word order, not facts: this is how a hallucination starts.
    text = "paris is in france . berlin is in germany ."
    result = train_and_generate(text, "berlin", 5)
    assert result == "berlin is in france .", "a one-word model mixes facts: fluent, but false"
