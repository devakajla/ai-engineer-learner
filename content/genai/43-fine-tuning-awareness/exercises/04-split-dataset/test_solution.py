from solution import split_dataset

LINES = [f"example number {i}" for i in range(1000)]


def test_no_example_is_lost_or_copied():
    train, val = split_dataset(LINES)
    assert len(train) + len(val) == 1000
    assert set(train) | set(val) == set(LINES)
    assert not set(train) & set(val), "an example in both sets would leak the answers into the test"


def test_validation_size_is_about_the_fraction():
    _, val = split_dataset(LINES, 0.1)
    assert 60 <= len(val) <= 140
    _, val = split_dataset(LINES, 0.3)
    assert 240 <= len(val) <= 360


def test_same_input_gives_the_same_split():
    assert split_dataset(LINES) == split_dataset(list(LINES))


def test_order_is_kept():
    train, _ = split_dataset(LINES)
    assert train == [x for x in LINES if x in set(train)]


def test_an_example_stays_in_its_set_when_the_data_grows():
    train, val = split_dataset(LINES[:500])
    train2, val2 = split_dataset(LINES)
    assert set(val) <= set(val2) and set(train) <= set(train2), "new data must not move old examples"


def test_zero_fraction_puts_everything_in_train():
    train, val = split_dataset(LINES, 0)
    assert len(train) == 1000 and val == []
