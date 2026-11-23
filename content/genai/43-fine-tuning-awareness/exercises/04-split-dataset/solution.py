import hashlib


def split_dataset(lines, val_fraction=0.1):
    train, val = [], []
    limit = round(val_fraction * 100)
    for line in lines:
        bucket = int(hashlib.md5(line.encode("utf-8")).hexdigest(), 16) % 100
        (val if bucket < limit else train).append(line)
    return train, val
