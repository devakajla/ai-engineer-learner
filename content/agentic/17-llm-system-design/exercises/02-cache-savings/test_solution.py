import pytest

from solution import cost_with_cache, prompt_cache_cost, savings_percent


def test_response_cache_saves_the_hits_and_costs_a_little_per_lookup():
    assert cost_with_cache(1000, 0.3, 0.01, 0.0001) == 7.1     # 700 misses * 0.01 + 1000 lookups * 0.0001
    assert cost_with_cache(1000, 0.0, 0.01) == 10.0
    assert cost_with_cache(1000, 1.0, 0.01) == 0.0


def test_hit_rate_must_be_a_share():
    for bad in (-0.1, 1.5):
        with pytest.raises(ValueError, match="hit_rate must be between 0 and 1"):
            cost_with_cache(10, bad, 1.0)


def test_prompt_caching_makes_the_repeated_prefix_cheap():
    hit = prompt_cache_cost(4000, 200, 300, 1.0, 4.0, 0.1, cache_hit=True)
    miss = prompt_cache_cost(4000, 200, 300, 1.0, 4.0, 0.1, cache_hit=False)
    assert hit == pytest.approx(0.0018)      # (400 + 200 + 1200) / 1e6
    assert miss == pytest.approx(0.0054)     # (4000 + 200 + 1200) / 1e6


def test_savings_percent():
    assert savings_percent(10.0, 7.1) == 29.0
    assert savings_percent(0.0054, 0.0018) == 66.7
    assert savings_percent(5, 5) == 0.0
    assert savings_percent(0, 0) == 0.0
    assert savings_percent(10, 12) == -20.0, "a negative saving means it got more expensive"
