import hashlib


# Given from earlier exercises. Do not change these.
def content_hash(text):
    normal = " ".join(text.split())
    return hashlib.sha256(normal.encode("utf-8")).hexdigest()[:16]


# Your task:
def plan_sync(stored, docs):
    ...
