from solution import pick_quantization, plan


def test_the_biggest_format_that_fits_wins():
    assert pick_quantization(7, 24) == 16     # 14 * 1.2 = 16.8 <= 24
    assert pick_quantization(13, 24) == 8     # 13 * 1.2 = 15.6 <= 24
    assert pick_quantization(30, 24) == 4     # 15 * 1.2 = 18 <= 24


def test_nothing_fits_gives_none():
    assert pick_quantization(70, 24) is None  # even 4 bits: 35 * 1.2 = 42 GB
    assert pick_quantization(7, 2) is None


def test_options_can_be_changed_and_any_order_works():
    assert pick_quantization(13, 24, options=(4, 16)) == 4
    assert pick_quantization(7, 24, options=(4, 8)) == 8


def test_plan_for_several_models():
    models = {"small": 3, "medium": 13, "large": 70}
    assert plan(models, 24) == {"small": 16, "medium": 8, "large": None}
    assert plan({}, 24) == {}
