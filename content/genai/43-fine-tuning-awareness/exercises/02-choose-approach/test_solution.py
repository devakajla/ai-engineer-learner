from solution import choose_approach


def test_try_prompting_first():
    assert choose_approach(True, True, True, 10000) == "prompting", "if a prompt already works, stop there"


def test_private_or_changing_knowledge_means_rag():
    assert choose_approach(False, True, False, 0) == "rag"
    assert choose_approach(False, True, True, 5000) == "rag", "facts that change belong in a database, not in the weights"


def test_style_with_enough_examples_means_fine_tune():
    assert choose_approach(False, False, True, 500) == "fine-tune"
    assert choose_approach(False, False, True, 20000) == "fine-tune"


def test_style_with_few_examples_means_few_shot():
    assert choose_approach(False, False, True, 499) == "few-shot"
    assert choose_approach(False, False, True, 0) == "few-shot"


def test_nothing_special_means_prompting():
    assert choose_approach(False, False, False, 100) == "prompting"
