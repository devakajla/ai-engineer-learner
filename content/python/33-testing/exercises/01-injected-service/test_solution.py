import pytest

from solution import SignupService


class FakeStore:
    def __init__(self, existing=()):
        self.emails = set(existing)

    def exists(self, email):
        return email in self.emails

    def add(self, email):
        self.emails.add(email)


class FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, text):
        self.sent.append((to, text))


@pytest.fixture
def parts():
    return FakeStore(), FakeMailer()


def test_signup_cleans_adds_and_sends(parts):
    store, mailer = parts
    out = SignupService(store, mailer).signup("  Ana@X.io ")
    assert out == "ana@x.io"
    assert store.emails == {"ana@x.io"}
    assert mailer.sent == [("ana@x.io", "Welcome!")]


@pytest.mark.parametrize("bad", ["nope", "a@b@c", "", "   "])
def test_invalid_email_has_no_side_effects(parts, bad):
    store, mailer = parts
    with pytest.raises(ValueError, match="invalid email"):
        SignupService(store, mailer).signup(bad)
    assert store.emails == set()
    assert mailer.sent == []


def test_duplicate_has_no_side_effects():
    store, mailer = FakeStore({"ana@x.io"}), FakeMailer()
    with pytest.raises(ValueError, match="already registered"):
        SignupService(store, mailer).signup("ANA@x.io")
    assert store.emails == {"ana@x.io"}
    assert mailer.sent == []


def test_uses_given_helpers_not_its_own(parts):
    store, mailer = parts
    service = SignupService(store, mailer)
    service.signup("a@b.io")
    service.signup("c@d.io")
    assert len(mailer.sent) == 2 and len(store.emails) == 2
