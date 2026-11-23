from solution import mask_email


def test_examples():
    assert mask_email("dev@example.com") == "d**@example.com"
    assert mask_email("kunal.k@gmail.com") == "k******@gmail.com"
    assert mask_email("a@b.io") == "a@b.io"


def test_length_preserved():
    email = "someone.long@company.co.in"
    assert len(mask_email(email)) == len(email)
