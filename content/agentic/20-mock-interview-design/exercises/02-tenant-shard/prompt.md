# Design drill 2: put tenants on shards

**Asked as:** "You have thousands of tenants. How do you split their data across several vector databases or servers?"

A common first answer is **hash sharding**: compute a stable number from the tenant id, and take it modulo the number of shards. The same tenant always goes to the same shard, and tenants spread out evenly. (Changing the number of shards moves many tenants. That is why real systems use **consistent hashing** or a lookup table. Mention it in the interview.)

Write (`import hashlib` is in the starter):

1. `shard_for(tenant_id, shards)`: `int(hashlib.md5(tenant_id.encode("utf-8")).hexdigest(), 16) % shards`.
2. `assign_tenants(tenant_ids, shards)`: a dict with **every** shard number `0` to `shards - 1` as a key, each with a list of the tenants that belong to it (in the input order).
3. `spread(groups)`: the size of the biggest group minus the size of the smallest (`0` for an empty dict). A small spread means a balanced split.

```python
shard_for("company-1", 4)      # always the same number from 0 to 3
spread(assign_tenants(tenants, 4))
# -> a small number for 400 tenants
```

**Think first:** one huge tenant is 40% of your traffic. Does hashing help with that? What would you do?

**Hint:** build the dict with all shard numbers first, so empty shards are still there.
