from solution import ttl_cache


def make(now):
    calls = []

    @ttl_cache(seconds=10, clock=lambda: now[0])
    def price(symbol, currency="USD"):
        """Get a price."""
        calls.append((symbol, currency))
        return len(calls)

    return price, calls


def test_caches_until_expiry():
    now = [0.0]
    price, calls = make(now)
    assert price("AAPL") == 1 and price("AAPL") == 1
    now[0] = 9.9
    assert price("AAPL") == 1
    now[0] = 10.5
    assert price("AAPL") == 2, "entries older than ttl must be recomputed"


def test_keys_include_args_and_kwargs():
    now = [0.0]
    price, calls = make(now)
    price("A")
    price("B")
    price("A", currency="EUR")
    assert len(calls) == 3


def test_metadata_and_clear():
    now = [0.0]
    price, calls = make(now)
    assert price.__name__ == "price" and price.__doc__ == "Get a price."
    price("A")
    price.cache_clear()
    price("A")
    assert len(calls) == 2
