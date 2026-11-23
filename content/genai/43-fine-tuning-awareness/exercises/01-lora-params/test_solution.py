from solution import lora_params


def test_typical_attention_matrix():
    assert lora_params(4096, 4096, 8) == {"full": 16777216, "lora": 65536, "percent": 0.39}


def test_bigger_rank_trains_more():
    assert lora_params(4096, 4096, 64)["lora"] == 524288
    assert lora_params(4096, 4096, 64)["percent"] == 3.12


def test_non_square_matrix():
    assert lora_params(1000, 200, 4) == {"full": 200000, "lora": 4800, "percent": 2.4}


def test_rank_must_be_positive():
    for bad in (0, -3):
        try:
            lora_params(10, 10, bad)
        except ValueError:
            continue
        raise AssertionError("rank below 1 must raise ValueError")
