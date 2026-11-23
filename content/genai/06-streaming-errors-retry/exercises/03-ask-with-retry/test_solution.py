from types import SimpleNamespace as NS

import pytest

from solution import ask_with_retry

MESSAGES = [{"role": "user", "content": "Hi"}]


class FlakyClient:
    """Raises an error for the first `fail_times` calls, then answers."""

    def __init__(self, fail_times, text="Hello!"):
        self.fail_times = fail_times
        self.text = text
        self.calls = 0
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RuntimeError(f"fail #{self.calls}")
        return NS(choices=[NS(message=NS(role="assistant", content=self.text))])


def test_works_first_time():
    client = FlakyClient(0)
    assert ask_with_retry(client, MESSAGES) == "Hello!"
    assert client.calls == 1, "do not call again after a success"


def test_retries_until_success():
    client = FlakyClient(2)
    assert ask_with_retry(client, MESSAGES) == "Hello!"
    assert client.calls == 3


def test_raises_the_last_error_when_all_fail():
    client = FlakyClient(10)
    with pytest.raises(RuntimeError) as info:
        ask_with_retry(client, MESSAGES, max_tries=2)
    assert str(info.value) == "fail #2", "raise the error from the last try"
    assert client.calls == 2


def test_max_tries_must_be_positive():
    with pytest.raises(ValueError, match="max_tries must be at least 1"):
        ask_with_retry(FlakyClient(0), MESSAGES, max_tries=0)


def test_waits_with_backoff():
    waits = []
    client = FlakyClient(2)
    assert ask_with_retry(client, MESSAGES, max_tries=4, sleep=waits.append) == "Hello!"
    assert waits == [1, 2], "wait 1 second, then 2 seconds, and not after the success"


def test_no_wait_after_the_last_failure():
    waits = []
    client = FlakyClient(10)
    with pytest.raises(RuntimeError):
        ask_with_retry(client, MESSAGES, max_tries=3, sleep=waits.append)
    assert waits == [1, 2], "3 tries need only 2 waits"


def test_no_sleep_function_means_no_waiting():
    client = FlakyClient(1)
    assert ask_with_retry(client, MESSAGES) == "Hello!"
