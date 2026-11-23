from solution import nearest_text

VOCAB = ["task", "login", "token"]
TEXTS = ["delete a task", "login with a token", "list every task"]


def test_finds_login():
    assert nearest_text("login token", TEXTS, VOCAB) == "login with a token"


def test_tie_goes_to_earlier():
    assert nearest_text("task", TEXTS, VOCAB) == "delete a task"


def test_empty():
    assert nearest_text("task", [], VOCAB) is None


def test_single_text():
    assert nearest_text("zzz", ["only"], VOCAB) == "only"


def test_punctuation_and_case():
    assert nearest_text("LOGIN!", ["Task.", "Login."], VOCAB) == "Login."
