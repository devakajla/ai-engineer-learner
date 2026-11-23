import hashlib


def shard_for(tenant_id, shards):
    digest = hashlib.md5(tenant_id.encode("utf-8")).hexdigest()
    return int(digest, 16) % shards


def assign_tenants(tenant_ids, shards):
    groups = {i: [] for i in range(shards)}
    for tenant in tenant_ids:
        groups[shard_for(tenant, shards)].append(tenant)
    return groups


def spread(groups):
    sizes = [len(members) for members in groups.values()]
    return max(sizes) - min(sizes) if sizes else 0
