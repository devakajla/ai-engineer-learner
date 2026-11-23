from solution import assign_tenants, shard_for, spread

TENANTS = [f"company-{i}" for i in range(400)]


def test_shard_is_stable_and_in_range():
    for tenant in TENANTS[:50]:
        shard = shard_for(tenant, 8)
        assert 0 <= shard < 8
        assert shard == shard_for(tenant, 8), "the same tenant must always land on the same shard"


def test_one_shard_means_everything_is_shard_zero():
    assert shard_for("anything", 1) == 0


def test_assign_tenants_keeps_every_tenant_once():
    groups = assign_tenants(TENANTS, 4)
    assert sorted(groups) == [0, 1, 2, 3]
    assert sorted(t for members in groups.values() for t in members) == sorted(TENANTS)
    assert all(shard_for(t, 4) == shard for shard, members in groups.items() for t in members)


def test_shards_without_tenants_are_still_present():
    groups = assign_tenants(["only-one"], 5)
    assert len(groups) == 5
    assert sum(len(m) for m in groups.values()) == 1


def test_spread_measures_the_gap_between_the_biggest_and_smallest_shard():
    assert spread({0: ["a", "b", "c"], 1: ["d"], 2: []}) == 3
    assert spread({0: ["a"], 1: ["b"]}) == 0
    assert spread({}) == 0


def test_hashing_spreads_tenants_reasonably():
    assert spread(assign_tenants(TENANTS, 4)) < 40
