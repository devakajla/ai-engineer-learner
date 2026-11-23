from solution import allow, new_bucket


def test_a_new_bucket_is_full():
    bucket = new_bucket(1, 3)
    assert [allow(bucket, 0.0) for _ in range(4)] == [True, True, True, False]


def test_tokens_come_back_over_time():
    bucket = new_bucket(2, 2)                 # 2 tokens per second, room for 2
    assert allow(bucket, 0.0) and allow(bucket, 0.0)
    assert allow(bucket, 0.0) is False
    assert allow(bucket, 0.5) is True         # 0.5 s x 2 = 1 token back
    assert allow(bucket, 0.5) is False


def test_the_bucket_never_holds_more_than_its_capacity():
    bucket = new_bucket(10, 2)
    assert allow(bucket, 100.0) and allow(bucket, 100.0)
    assert allow(bucket, 100.0) is False, "a long wait must not store more than capacity"


def test_cost_can_be_more_than_one():
    bucket = new_bucket(1, 10)
    assert allow(bucket, 0.0, cost=7) is True
    assert allow(bucket, 0.0, cost=7) is False
    assert allow(bucket, 4.0, cost=7) is True      # 3 left + 4 refilled = 7


def test_a_refused_call_does_not_use_up_tokens():
    bucket = new_bucket(1, 5)
    assert allow(bucket, 0.0, cost=9) is False
    assert allow(bucket, 0.0, cost=5) is True


def test_time_going_backwards_is_ignored():
    bucket = new_bucket(1, 2, now=10.0)
    assert allow(bucket, 5.0) is True
    assert bucket["tokens"] <= 2
